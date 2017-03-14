# -*- coding: utf-8 -*-"

from webui.utils.oracle_connect import oracle_connect


def f_priv_db_user_list(**kwargs):
    l_dbinfo = kwargs["v_dbinfo"]
    conn = oracle_connect(
        l_dbinfo[0],
        l_dbinfo[1],
        l_dbinfo[3],
        l_dbinfo[4],
        l_dbinfo[2]
    )
    cursor = conn.cursor()
    cursor.execute(
        """select distinct owner from dba_segments
        where owner in
        (select username from dba_users
        where account_status='OPEN' and username
        not in ( 'SYS','SYSTEM') and default_tablespace
        NOT IN ('USERS','SYSAUX'))"""
    )
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    l_return_stru = records
    return l_return_stru


if __name__ == "__main__":
    v_dbinfo = ["127.0.0.1", "1521", "cedb", "system", "xxxxxxx"]
    arg = {
        "v_dbinfo": v_dbinfo
    }
    print(f_priv_db_user_list(**arg))
