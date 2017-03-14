# -*- coding: utf-8 -*-


# base sql
# 获取数据库中被审核schema名称列表
OWNER_LIST_SQL = """
SELECT DISTINCT OWNER
FROM dba_segments
WHERE OWNER IN
    (SELECT username
     FROM dba_users
     WHERE account_status = 'OPEN'
       AND username NOT IN ('SYS',
                            'SYSTEM')
       AND default_tablespace NOT IN ('USERS', 'SYSAUX'))
"""

# 从awr中根据快照编号、schema名称以及按照top sql的类别（elapsed_time,cpu_time,disk_reads,executions,buffer_gets）取出所有的被审核的sql语句
SQL_SET = """
SELECT sql_id,
       plan_hash_value,
       parsing_schema_name
FROM table(dbms_sqltune.select_workload_repository(&beg_snap, &end_snap, 'parsing_schema_name=''&username''', NULL, '&parameter', NULL, NULL, NULL, NULL))
"""

# 从dba_hist_sqlstat中，按照sql_id，plan_hash_value，快照点以及schema 名，取出某一条sql在执行时，使用cpu，buffer_gets等方面的情况。
SQL_STAT_SET = """
SELECT t.sql_id,
       t.plan_hash_value,
       t.parsing_schema_name AS username,
       round(sum(t.cpu_time_total) / 1000000, 4) AS cpu_time_total,
       round(sum(t.cpu_time_delta) / 1000000, 4) AS cpu_time_delta,
       round(ceil((sum(cpu_time_delta) / decode(sum(executions_delta), 0, 1, sum(executions_delta)))) / 1000000, 4) per_cpu_time,
       sum(t.disk_reads_total) AS disk_reads_total,
       sum(t.disk_reads_delta) AS disk_reads_delta,
       ceil((sum(disk_reads_delta) / decode(sum(executions_delta), 0, 1, sum(executions_delta)))) per_disk_reads,
       sum(t.direct_writes_total) AS direct_writes_total,
       sum(t.direct_writes_delta) AS direct_writes_delta,
       ceil((sum(direct_writes_delta) / decode(sum(executions_delta), 0, 1, sum(executions_delta)))) per_direct_writes,
       round(sum(t.elapsed_time_total) / 1000000, 4) AS elapsed_time_total,
       round(sum(t.elapsed_time_delta) / 1000000, 4) AS elapsed_time_delta,
       round(ceil((sum(elapsed_time_delta) / decode(sum(executions_delta), 0, 1, sum(executions_delta)))) / 1000000, 4) per_elapsed_time,
       sum(t.buffer_gets_total) AS buffer_gets_total,
       sum(t.buffer_gets_delta) AS buffer_gets_delta,
       ceil((sum(buffer_gets_delta) / decode(sum(executions_delta), 0, 1, sum(executions_delta)))) per_buffer_gets,
       sum(t.rows_processed_delta) AS rows_processed_delta,
       sum(t.rows_processed_total) AS rows_processed_total,
       ceil((sum(rows_processed_delta) / decode(sum(executions_delta), 0, 1, sum(executions_delta)))) rows_processed_gets,
       sum(t.executions_total) AS executions_total,
       sum(t.executions_delta) AS executions_delta,
       round(sum(DISK_READS_DELTA) + sum(BUFFER_GETS_DELTA) / decode(sum(ROWS_PROCESSED_DELTA), 0, 1, sum(ROWS_PROCESSED_DELTA)), 3) AS per_row_blk
FROM dba_hist_sqlstat t
WHERE t.snap_id BETWEEN '&beg_snap' AND '&end_snap'
  AND t.parsing_schema_name = '&username'
  AND t.sql_id = '&sql_id'
  AND t.plan_hash_value = '&plan_hash_value'
GROUP BY sql_id,
         plan_hash_value,
         t.parsing_schema_name
"""

# 从dba_hist_sql_plan中，按照sql_id，plan_hash_value，获取某一条sql语句的执行计划，并保存该执行计划的前799行。
SQL_PLAN_SET = """
SELECT p.sql_id,
       p.plan_hash_value,
       p.id,
       p.depth,
       p.parent_id,
       p.operation,
       lpad(' ', 2 * p.depth) || p.operation operation_display,
       p.options,
       p.object_node,
       p.object_owner,
       p.object_name,
       p.object_type,
       p.optimizer,
       p.search_columns,
       p.position,
       p.cost,
       p.cardinality,
       p.bytes,
       p.other_tag,
       p.partition_start,
       p.partition_stop,
       p.partition_id,
       p.other,
       p.distribution,
       p.cpu_cost,
       p.io_cost,
       to_char(t.FILTER_PREDICATES) AS FILTER_PREDICATES
FROM dba_hist_sql_plan p
LEFT JOIN
  (SELECT *
   FROM
     (SELECT sql_id,
             plan_hash_value,
             s.ID,
             FILTER_PREDICATES,
             rank() over(partition BY sql_id, plan_hash_value
                         ORDER BY s.TIMESTAMP,s.CHILD_NUMBER DESC) mm
      FROM gv$sql_plan s
      WHERE s.inst_id<>0
        AND s.SQL_ID = '&sql_id'
        AND s.PLAN_HASH_VALUE = '&h_value'
        AND s.id<=799 )
   WHERE mm = 1) t ON p.sql_id = t.sql_id
AND p.plan_hash_value = t.plan_hash_value
AND p.id=t.id
WHERE p.sql_id = '&sql_id'
  AND p.plan_hash_value = '&h_value'
  AND p.id<=799
"""

# 从dba_hist_sqltext中，获取某条sql语句的文本，分别保存该sql语句文本的40和2000个字符。
SQL_TEXT_SET = """
SELECT p.dbid,
       p.sql_id,
       dbms_lob.substr(p.sql_text,40,1) sql_text,
       dbms_lob.substr(p.sql_text,2000,1) sql_text_detail
FROM dba_hist_sqltext p
WHERE p.sql_id = '&sql_id'
"""

# 获取未使用绑定变量的sql语句的情况，并且FORCE_MATCHING_SIGNATURE和username字段作为获取相关未使用绑定变量的依据。
SQL_NO_BIND_SET = """
SELECT d.INST_ID,
       d.PARSING_SCHEMA_NAME AS username,
       to_char(FORCE_MATCHING_SIGNATURE),
       d.PLAN_HASH_VALUE,
       count(*)
FROM gv$sql d
WHERE FORCE_MATCHING_SIGNATURE > 0
  AND d.PARSING_SCHEMA_NAME NOT IN ('SYS',
                                    'SYSTEM')
  AND d.MODULE <> 'PL/SQL Developer'
  AND d.module <> 'DBMS_SCHEDULER'
  AND FORCE_MATCHING_SIGNATURE != EXACT_MATCHING_SIGNATURE
  AND d.PARSING_SCHEMA_NAME ='&username'
GROUP BY to_char(FORCE_MATCHING_SIGNATURE),
         d.PLAN_HASH_VALUE,
         d.PARSING_SCHEMA_NAME,
         d.INST_ID
HAVING count(*) > 100
ORDER BY d.INST_ID,
         count(*) DESC
"""

# 根据快照点，获取两个快照点之间的某个schema下的sql语句的游标使用情况。
SQL_CURSOR_SET = """
SELECT *
FROM
  (SELECT t.parsing_schema_name AS username,
          t.sql_id,
          t.plan_hash_value,
          t.version_count,
          row_number() over(partition BY t.sql_id
                            ORDER BY t.plan_hash_value DESC) rank
   FROM dba_hist_sqlstat t
   WHERE t.parsing_schema_name = '&username'
     AND (t.snap_id BETWEEN '&beg_snap' AND '&end_snap')) e
WHERE e.rank = 1
"""

# 获取某个schema下的对象类型为index的基本信息，如：索引名称，索引类型，索引的高度，最后一次ddl的时间等信息。
OBJ_BASE_IDX_HEAP_INFO_SQL = """
select owner,
       index_name,
       decode(INDEX_TYPE,
              'NORMAL',
              'B-tree',
              decode(index_type,
                     'BITMAP',
                     'BitMap',
                     decode(table_type,
                            'IOT',
                            'IOT',
                            decode(index_type, 'LOB', 'LOB')))) idx_type,
       TABLE_OWNER,
       table_name,
       TABLE_TYPE,
       COMPRESSION,
       STATUS,
       BLEVEL,
       CLUSTERING_FACTOR,
       UNIQUENESS,
       DISTINCT_KEYS,
       LAST_ANALYZED,
       LAST_DDL_TIME
  from (select distinct t.INDEX_NAME,
                        t.OWNER,
                        t.index_type,
                        t.TABLE_OWNER,
                        t.TABLE_NAME,
                        decode(u.partitioned,
                               'YES',
                               'PART',
                               decode(u.temporary,
                                      'Y',
                                      'TEMP',
                                      decode(u.iot_type,
                                             'IOT',
                                             'IOT',
                                             'NORMAL'))) table_type,
                        t.COMPRESSION,
                        t.STATUS,
                        t.BLEVEL,
                        t.CLUSTERING_FACTOR,
                        t.DISTINCT_KEYS,
                        t.UNIQUENESS,
                        t.LAST_ANALYZED,
                        s.LAST_DDL_TIME
          from dba_indexes t, dba_objects s, dba_tables u
         where t.INDEX_NAME = s.OBJECT_NAME
           and u.table_name = t.table_name
           and s.owner = u.owner
           and t.OWNER = s.OWNER
           and s.object_type = 'INDEX'
           and t.owner = '{obj_owner}'
         order by t.index_name)
"""

# 获取某个schema下的对象类型为index的基本信息，如：索引的物理大小。
OBJ_BASE_IDX_HEAP_PHY_SIZE_SQL = """
    select u.owner,
       u.segment_name,
       sum(u.bytes) / 1024 / 1024 as idx_space
  from dba_segments u
 where u.segment_type like '%INDEX%'
   and u.owner = '{obj_owner}'
 group by u.owner, u.segment_name, u.segment_type
 order by u.owner, u.segment_name, u.segment_type
"""

# 获取某个schema下的对象类型为index的基本信息，如：索引所在列的名称，列在索引中的位置（复合索引）等。
OBJ_BASE_IDX_COL_HEAP_COL_INFO_SQL = """
    select 
    INDEX_OWNER,     
    INDEX_NAME,     
    TABLE_OWNER,    
    TABLE_NAME,      
    COLUMN_NAME,     
    COLUMN_POSITION,   
    DESCEND   
    from  dba_ind_columns t
    where index_owner='{obj_owner}' and index_name not like '%BIN$%'
    order by t.INDEX_NAME,t.COLUMN_POSITION   
"""

# 获取某个schema下的对象类型为table的基本信息，如：表的名称，表的类型，最后一次ddl的时间等信息。
OBJ_BASE_TAB_HEAP_INFO_SQL = """
    select t.owner,
           t.table_name,
           decode(t.partitioned,
                  'YES',
                  'PART',
                  decode(t.temporary, 'Y', 'TEMP', decode (t.iot_type,'IOT','IOT','NORMAL'))) table_type,
           s.object_type,
           t.iot_name,
           t.NUM_ROWS,
           t.BLOCKS,
           t.AVG_ROW_LEN,
           t.LAST_ANALYZED,
           s.last_ddl_time,
           t.CHAIN_CNT,
           trunc(((t.AVG_ROW_LEN * t.NUM_ROWS) / 8) /
                 (decode(t.BLOCKS, 0, 1, t.BLOCKS)) * 100) as HWM_STAT,
           t.COMPRESSION
      from dba_tables t, dba_objects s
     where t.table_name = s.object_name
       and t.owner = s.owner
       and s.object_type = 'TABLE'
       and t.table_name not like '%BIN%'
       and t.owner = '{obj_owner}'
"""
# 获取某个schema下的对象类型为table的基本信息，如：表的物理大小
OBJ_BASE_TAB_HEAP_PHY_SIZE_SQL = """
    select segment_name, sum(bytes) / 1024 / 1024 as tab_space
    from dba_segments u
    where u.segment_type in ('TABLE','TABLE PARTITION','TABLE SUBPARTITION') 
    and u.owner = '{obj_owner}'
    and u.segment_name not like '%BIN%'
    group by u.owner, u.segment_name
"""
# 获取某个schema下的对象类型为table的基本信息，如：表中列的数量。
OBJ_BASE_TAB_HEAP_COL_NUM_SQL = """
    select s.table_name,count(s.COLUMN_NAME) as col_num
    from dba_tab_columns s, dba_objects t
    where s.owner = '{obj_owner}'
    and s.owner = t.owner
    and s.TABLE_NAME = t.object_NAME
    and t.object_type = 'TABLE'
    and s.table_name not like '%BIN%'
    group by s.OWNER, s.TABLE_NAME
"""
# 获取某个schema下的对象类型为partition index的基本信息，如：索引名称，类型，所在列的名称等。
OBJ_PART_IDX_INFO_SQL = """
    select t.INDEX_NAME,
       t.OWNER,
       t.TABLE_NAME,   
       v.column_name,
       t.PARTITIONING_TYPE,
       t.SUBPARTITIONING_TYPE,
       t.PARTITION_COUNT,
       t.LOCALITY,
       t.ALIGNMENT
  from dba_part_indexes t, dba_part_key_columns v
 where t.index_name = v.name
   and t.owner = '{obj_owner}'
"""

# 获取某个schema下的对象类型为partition index的基本信息，如：索引的物理大小。
OBJ_PART_IDX_PHY_SIZE_SQL = """
    select segment_name, sum(t.bytes) / 1024 / 1024 as tab_space
    from dba_segments t
    where t.owner = '{obj_owner}'
    and t.partition_name is not null
    and t.segment_type in ('INDEX SUBPARTITION', 'INDEX PARTITION')
    group by segment_name
"""
# 获取某个schema下的对象类型为partition index的基本信息，如：索引的名称，最后一次ddl的时间。
OBJ_PART_IDX_DETAIL_INFO_SQL = """
    select t.OWNER,
       t.INDEX_NAME,
       t.TABLE_NAME,
       u.partition_name,
       u.partition_position,       
       v.column_name,
       t.PARTITIONING_TYPE,
       t.SUBPARTITIONING_TYPE,
       t.PARTITION_COUNT,
       t.LOCALITY,
       t.ALIGNMENT,
       u.COMPRESSION,
       u.STATUS,
       u.BLEVEL,
       u.CLUSTERING_FACTOR,
       u.DISTINCT_KEYS,
       u.LAST_ANALYZED
  from dba_part_indexes t, dba_ind_partitions u,dba_part_key_columns v
 where t.INDEX_NAME = u.INDEX_NAME
   and t.index_name = v.name
   and t.OWNER = u.INDEX_OWNER
   and t.owner = '{obj_owner}'
 order by u.index_name,u.partition_name   
"""
# 获取某个schema下的对象类型为partition table的基本信息，如：表的名称，分区名称，最后一次ddl的时间等。
OBJ_PART_TAB_INFO_SQL = """
    select t.table_owner,
       t.table_name,
       s.object_id,
       s.OBJECT_TYPE,
       'part tab' as part_role,
       s.DATA_OBJECT_ID,
       t.partition_name,
       t.subpartition_count,
       t.partition_position,
       t.CHAIN_CNT,
       trunc(((t.AVG_ROW_LEN * t.NUM_ROWS) / 8) /
             (decode(t.BLOCKS, 0, 1, t.BLOCKS)) * 100) as HWM_STAT,
       t.blocks,
       t.num_rows,
       t.avg_row_len,
       t.last_analyzed,
       s.LAST_DDL_TIME
  from dba_tab_Partitions t, dba_objects s
 where t.partition_name = s.SUBOBJECT_NAME
   and t.table_name = s.object_name
   and t.table_owner = s.owner
   and t.table_name not like '%BIN$%'     
   and s.OBJECT_TYPE = 'TABLE PARTITION'
   and t.table_owner = '{obj_owner}'
 order by table_owner, table_name, partition_name
"""
# 获取某个schema下的对象类型为partition table的基本信息，如：表中每个分区的物理大小
OBJ_PART_TAB_PHY_SIZE_SQL = """
    select u.segment_name,
       u.partition_name,
       sum(u.bytes) / 1024 / 1024 as tab_space
  from dba_segments u
 where u.segment_type = 'TABLE PARTITION'
   and u.owner = '{obj_owner}'
   and u.segment_name not like '%BIN$%'
 group by u.owner, u.segment_name, u.partition_name
union
select s.segment_name,
       t.partition_name,
       sum(s.bytes) / 1024 / 1024 as tab_space
  from dba_segments s, dba_tab_subpartitions t
 where s.partition_name = t.subpartition_name
   and s.segment_type = 'TABLE SUBPARTITION'
   and s.segment_name not like '%BIN$%'
   and s.owner = t.table_owner
   and s.owner = '{obj_owner}'
 group by s.owner, s.segment_name,t.partition_name
"""

# 获取某个schema下对象类型为partition table的相关信息，如：分区表的类型，分区键，分区的数量等信息。
OBJ_PART_TAB_PARENT_SQL = """
       select s.OWNER,
       s.OBJECT_NAME as TABLE_NAME,
       s.OBJECT_ID,
       s.DATA_OBJECT_ID,
       u.partitioning_type,
       t.column_name,
       u.partitioning_key_count,
       u.partition_count,
       u.subpartitioning_key_count,
       u.subpartitioning_type,
       s.LAST_DDL_TIME,
       'part tab parent' as part_role
  from dba_objects s, Dba_part_key_columns t, dba_part_tables u
 where s.OBJECT_NAME = t.name
   and t.name = u.table_name
   and t.owner = u.owner
   and s.owner = t.owner
   and s.owner = '{obj_owner}'
   and s.SUBOBJECT_NAME is null
   and s.OBJECT_name in (select distinct table_name
                           from dba_tab_partitions t
                          where t.table_owner =  '{obj_owner}')
 order by owner, object_name
"""

# 获取某个schema下对象类型为partition table的相关信息，如：每个part table的物理大小。
OBJ_PART_TAB_PARENT_PHY_SIZE_SQL = """
    select segment_name, sum(t.bytes) / 1024 / 1024 as tab_space
    from dba_segments t
    where t.owner = '{obj_owner}'
    and t.partition_name is not null
    and t.segment_name not like '%BIN$%'
    and t.segment_type in ('TABLE SUBPARTITION','TABLE PARTITION')
    group by segment_name  
"""
# 获取某个schema下对象类型为partition table的相关信息，如：每个part table包含的记录数量。
OBJ_PART_TAB_PARENT_COL_SQL = """
    select t.table_name, sum(t.num_rows) num_rows
    from dba_tab_Partitions t
    where t.table_owner = '{obj_owner}'
    and t.table_name not like '%BIN$%'
    group by t.table_name
    order by t.table_name 
"""
# 获取某个schema下对象类型为partition table，并且包含子分区的相关信息，如：子分区的名称，位置等信息。
OBJ_PART_TAB_SON_INFO_SQL = """
    select t.table_owner,
       t.table_name,
       s.object_id,
       s.OBJECT_TYPE,
       'part tab son' as part_role,
       s.DATA_OBJECT_ID,
       t.partition_name,
       t.SUBPARTITION_NAME,
       t.SUBPARTITION_POSITION,
       u.column_name,
       t.CHAIN_CNT,
       t.blocks,
       t.num_rows,
       t.avg_row_len,
       trunc(((t.AVG_ROW_LEN * t.NUM_ROWS) / 8) /
             (decode(t.BLOCKS, 0, 1, t.BLOCKS)) * 100) as HWM_STAT,
       t.last_analyzed,
       s.LAST_DDL_TIME
  from dba_tab_subpartitions t, dba_objects s,Dba_Subpart_Key_Columns u
 where t.table_name = u.name
 and t.subpartition_name = s.SUBOBJECT_NAME
   and t.table_name = s.object_name
   and t.table_owner = s.owner
   and t.table_name not like '%BIN$%'     
   and s.OBJECT_TYPE = 'TABLE SUBPARTITION'
   and t.table_owner = '{obj_owner}'
 order by table_owner, table_name, partition_name
 """
# 获取某个schema下对象类型为table，并且包含子分区的相关信息，如：子分区的物理大小。
OBJ_PART_TAB_SON_PHY_SIZE_SQL = """
   select s.segment_name,
       t.partition_name,
       s.partition_name,
       sum(s.bytes) / 1024 / 1024 as tab_space
  from dba_segments s, dba_tab_subpartitions t
 where s.partition_name = t.subpartition_name
   and s.segment_type = 'TABLE SUBPARTITION'
   and s.owner = t.table_owner
   and s.owner = '{obj_owner}'
 group by s.owner, s.segment_name,t.partition_name,s.partition_name
 """
# 获取某个schema下对象类型为table的相关信息，如：列的名称，列的类型，平均长度等信息。
OBJ_TAB_COL_SQL = """
     select t.OWNER,
       t.TABLE_NAME,
       t.COLUMN_NAME,
       t.DATA_TYPE,
       '' TYPE_CHANGE,
       t.NULLABLE,
       t.NUM_NULLS,
       t.NUM_DISTINCT,
       t.DATA_DEFAULT,
       t.AVG_COL_LEN
  from dba_tab_columns t, dba_objects s
 where t.OWNER = s.owner
   and t.TABLE_NAME = s.object_name
   and t.OWNER = '{obj_owner}'
   and s.OBJECT_TYPE='TABLE' 
   order by t.TABLE_NAME,t.COLUMN_NAME
 """
# 获取某个schema下对象类型为view的相关信息，如：view依赖的对象名称和对象类型。
OBJ_VIEW_INFO_SQL = """
     select name||referenced_name as obj_pk,
     s.owner,
     s.name as view_name,
     s.type as object_type,
     s.referenced_owner,
     s.referenced_name,
     s.referenced_type
    from DBA_DEPENDENCIES s
    where s.type = 'VIEW'
    and s.owner = '{obj_owner}'
    order by s.name
 """
