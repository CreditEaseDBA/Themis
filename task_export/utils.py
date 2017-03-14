# -*- coding: utf-8 -*-

from pyh import *
import json
import sqlparse

def print_html_script():
    """
    加载离线页面的各种js和css脚本
    """
    page = PyH('sqlreview report')
    page << """
            <!-- ================== BEGIN BASE CSS STYLE ================== -->
            <link href="http://fonts.googleapis.com/css?family=Open+Sans:300,400,600,700" rel="stylesheet">
            <link href="assets/plugins/jquery-ui/themes/base/minified/jquery-ui.min.css" rel="stylesheet" />
            <link href="assets/plugins/bootstrap/css/bootstrap.min.css" rel="stylesheet" />
            <link href="assets/plugins/font-awesome/css/font-awesome.min.css" rel="stylesheet" />
            <link href="assets/css/animate.min.css" rel="stylesheet" />
            <link href="assets/css/style.min.css" rel="stylesheet" />
            <link href="assets/css/style-responsive.min.css" rel="stylesheet" />
            <link href="assets/css/theme/default.css" rel="stylesheet" id="theme" />
            <!-- ================== END BASE CSS STYLE ================== -->
            
            <!-- ================== BEGIN PAGE LEVEL CSS STYLE ================== -->
            <link href="assets/plugins/jquery-jvectormap/jquery-jvectormap-1.2.2.css" rel="stylesheet" />

            <link href="assets/plugins/gritter/css/jquery.gritter.css" rel="stylesheet" />
            <link href="assets/plugins/morris/morris.css" rel="stylesheet" />
            <link href="css/lib/dataTables.bootstrap.css" rel="stylesheet">
            <link href="css/lib/dataTableStyle.css" rel="stylesheet">
            <link href="css/lib/jquery.treegrid.css" rel="stylcesheet">

            <link href="css/style.css" rel="stylesheet"/>
            <!-- ================== END PAGE LEVEL CSS STYLE ================== -->
            
            <!-- ================== BEGIN BASE JS ================== -->
            <script src="assets/plugins/pace/pace.min.js"></script>
            <!-- ================== END BASE JS ================== -->
            <!-- ================== BEGIN BASE JS ================== -->
            <script src="assets/plugins/jquery/jquery-1.9.1.min.js"></script>
            <script src="assets/plugins/jquery/jquery-migrate-1.1.0.min.js"></script>
            <script src="assets/plugins/jquery-ui/ui/minified/jquery-ui.min.js"></script>
            <script src="assets/plugins/bootstrap/js/bootstrap.min.js"></script>
            <!--[if lt IE 9]>
                <script src="assets/crossbrowserjs/html5shiv.js"></script>
                <script src="assets/crossbrowserjs/respond.min.js"></script>
                <script src="assets/crossbrowserjs/excanvas.min.js"></script>
            <![endif]-->
            <script src="assets/plugins/slimscroll/jquery.slimscroll.min.js"></script>
            <script src="assets/plugins/jquery-cookie/jquery.cookie.js"></script>
            <!-- ================== END BASE JS ================== -->
            
            <!-- ================== BEGIN PAGE LEVEL JS ================== -->
            <script src="assets/plugins/morris/raphael.min.js"></script>
            <script src="assets/plugins/morris/morris.js"></script>
            <script src="assets/plugins/jquery-jvectormap/jquery-jvectormap-1.2.2.min.js"></script>
            <script src="assets/plugins/jquery-jvectormap/jquery-jvectormap-world-merc-en.js"></script>

            <script src="assets/plugins/gritter/js/jquery.gritter.js"></script>
            <script src="js/lib/jquery.dataTables.js") }}"></script>
            <script src="js/lib/dataTables.bootstrap.js")}}"></script>
            <script src="js/lib/echarts-all.js"></script>
            <script src="js/lib/jquery.treegrid.js"></script>
            <script src="js/lib/jquery.treegrid.bootstrap3.js"></script>
            <script src="assets/js/apps.min.js"></script>
            <script src="js/task.js"></script>
            <!-- ================== END PAGE LEVEL JS ================== -->
            """
    return page

def print_html_body(page, ipaddress, port, schema):
    """
    生成离线页面的body
    """
    page << """
        <body>
        <!-- begin #page-loader -->
        <div id="page-loader" class="fade in"><span class="spinner"></span></div>
        <!-- end #page-loader -->
        
        <!-- begin #page-container -->
        <div id="page-container" class="fade page-sidebar-fixed page-header-fixed">
            <!-- begin #header -->
            <div id="header" class="header navbar navbar-default navbar-fixed-top">
                <!-- begin container-fluid -->
                <div class="container-fluid">
                    <!-- begin mobile sidebar expand / collapse button -->
                    <div class="navbar-header">
                        <a href="#"><h3 class="top-title">
                        IPADDRESS:""" + ipaddress + """ PORT:""" + port + """ SCHEMA:""" + schema + """ sqlreview明细报告
                        </h3></a>
                    </div>
                    <!-- end mobile sidebar expand / collapse button -->
                </div>
                <!-- end container-fluid -->
            </div>
            <!-- end #header -->
            
            <!-- begin #content -->
            <div id="content" class="content">
            <div class="row">
            <!-- begin panel -->
            <div id="base">
            </div>
            <!-- end panel -->
            </div>
            <!-- end row -->
            </div>
            <!-- end #content -->
            
            
            <!-- begin scroll to top btn -->
            <a href="javascript:;" class="btn btn-icon btn-circle btn-success btn-scroll-to-top fade" data-click="scroll-top"><i class="fa fa-angle-up"></i></a>
            <!-- end scroll to top btn -->
        </div>
        <!-- end page container -->
        </body>
            """

def print_html_js(page):
    page << """
            <script>
                $(document).ready(function() {
                    App.init();
                });
            </script>
            """

def print_html_chart(total_score, page, rules):
    """
    生成页面中的饼图，依赖于百度的echarts
    """
    legend = ""
    pie_data = ""
    deduct_marks = 0
    for value in rules:
        legend += "'" + str(value[0]) + "',"
        pie_data += "{value:" + str(value[3]) + ", name: '" + value[0] + "'},"
        deduct_marks += float(value[3])
    score = (total_score - deduct_marks) / total_score * 100
    title = '规则总分: ' + str(round(score, 3))
    legend = "[" + legend + "]"
    pie_data = "[" + pie_data + "]"
    page << "<script>genCharts('" + title + "', '规则扣分详情'," + legend + ", "+ pie_data + ")</script>"
    page << br()

def print_html_rule_table(page, ipaddress, port, schema, rules):
    """
    生成离线页面中的规则表格
    """
    title = ipaddress + " " + str(port) + " " + schema + "规则概览"
    data = ""
    columns = """[{ "title": "规则名称", "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {$(nTd).html("<a href='#" + oData[0] + "'>" + oData[0] + "</a>");}},{ "title": "规则描述"},{ "title": "违反次数"},{ "title": "扣分"}]"""
    for value in rules:
        data += "['" + value[0] + "','" + value[1] + "','" + str(value[2]) + "','" + str(value[3]) + "'],"
    page << "<script>genTable('#base', '"+ title + "', 'rule_info_table', [" + data[:-1] + "], " + columns + ", 'rule_info', '1')</script>"
    page << br()

def print_html_rule_detail_table(page, results, rules, rule_type):
    """
    生成违反的规则的具体信息，由表格和文本构成
    """
    if rule_type.upper() == "SQLPLAN" or rule_type.upper() == "SQLSTAT":
        columns = """[
                        {   
                            "title": "rulename",
                        },
                        {
                            "title": "sqlid",
                            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                                $(nTd).html("<a href='#" + oData[0] + "-" + oData[1] + "-" +oData[3] + "-" + oData[4] + "'>" + oData[1] + "</a>");
                                }
                        },
                        { 
                            "title": "sqltext"
                        },
                        { 
                            "title": "plan_hashvalue"
                        },
                        { 
                            "title": "pos"
                        },
                        {
                            "title": "object_name"
                        }
                    ]"""
    elif rule_type.upper() == "TEXT":
        columns = """[
                        {   
                            "title": "rulename"
                        },
                        {
                            "title": "sqlid",
                            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                                $(nTd).html("<a href='#" + oData[0] + "-" + oData[1] + "-1-v'>" + oData[1] + "</a>");
                                }
                        },
                        { 
                            "title": "sqltext"
                        }
                    ]
            """

    for rule in rules:
        data = ""
        for key in results[rule[0]].keys():
            if "#" in key:
                sql_id = key.split("#")[0]
                hash_value = key.split("#")[1]
                obj_id = key.split("#")[2]
                if rule_type.upper() == "SQLPLAN" or rule_type.upper() == "SQLSTAT":
                    sql_text = results[rule[0]][key]["sql_text"]
                    sql_text = sql_text.replace("\n", " ")
                    sql_text = sql_text.replace("'", "\"")
                    obj_name = results[rule[0]][key].get("obj_name", None)
                    if not obj_name:
                        obj_name = "空"
                    # obj_name = results[rule[0]][key]["obj_name"]
                    # obj_name = "test"
                    data += "['" + rule[0] + "', '" + sql_id + "','" + str(sql_text) + "','" + str(long(hash_value)) + "','" + str(obj_id) + "','" + obj_name + "'],"
                elif rule_type.upper() == "TEXT":
                    if len(results[rule[0]][key]["sql_text"]) > 40:
                        sql_text = results[rule[0]][key]["sql_text"][:40]
                    else:
                        sql_text = results[rule[0]][key]["sql_text"]
                    sql_text = sql_text.replace("\n", " ")
                    sql_text = sql_text.replace("'", "\"")
                    data += "['" + rule[0] + "', '" + sql_id + "','" + str(sql_text) + "'],"
        if data:
            page << "<script>genTable('#base', '" + rule[0] + "', '" + rule[0] + "_table', [" + data[:-1] + "], " + columns + ",'" + rule[0] + "', '3', '" + rule[4] + "')</script>"
            page << br()
    page << br()


def print_html_rule_detail_info(page, results, rules):
    """
    sqlplan和sqlstat的具体信息
    """
    for rule in rules:
        data = ""
        for key in results[rule[0]].keys():
            if "#" in key:
                index_id = key.replace("#", "-")
                div_id = rule[0] + "-" + index_id
                text_id = div_id + "-text"
                sql_fulltext = sqlparse.format(results[rule[0]][key]["sql_fulltext"], reindent=True)
                sql_fulltext = json.dumps(sql_fulltext)
                # sql_fulltext = sql_fulltext.strip("\n").replace("'", "\"")
                obj_info = results[rule[0]][key]["obj_info"]
                temp_obj_columns = []
                temp_obj_info = []
                # obj_id = key + "-obj"
                obj_id = div_id + "-obj"
                if obj_info:
                    for obj_key in obj_info.keys():
                        # temp_obj_columns += "{'title': '" + obj_key + "'},"
                        temp_obj_columns.append({"title" : obj_key})
                        # temp_obj_info += str(obj_info[obj_key]) + ","
                        temp_obj_info.append(str(obj_info[obj_key]))
                #     temp_obj_info = "[[" + temp_obj_info + "]]"
                temp_obj_info = json.dumps([temp_obj_info])
                temp_obj_columns = json.dumps(temp_obj_columns)
                stat_info = results[rule[0]][key]["stat"]
                temp_stat_columns = []
                stat_id = div_id + "-stat"
                temp_stat_info = []
                if stat_info:
                    for stat_key in stat_info.keys():
                        # temp_stat_columns += "{'title': '" + stat_key + "'},"
                        temp_stat_columns.append({"title": stat_key})
                        temp_stat_info.append(str(stat_info[stat_key]))
                temp_stat_info = json.dumps([temp_stat_info])
                temp_stat_columns = json.dumps(temp_stat_columns)
                #         temp_stat_info += str(stat_info[stat_key]) + ","
                #     temp_stat_info = "[[" + temp_stat_info + "]]"
                plan_id = div_id + "-plan"
                plans = json.dumps(results[rule[0]][key]["plan"])
                page << "<script>genMultiTable('#base', '" + div_id + "', '" + obj_id + "', " + temp_obj_info + ", " + temp_obj_columns + ", '" + stat_id + "', " + temp_stat_info + ", " + temp_stat_columns + ", '" + text_id + "', " + sql_fulltext + ", '" + plan_id + "', " + plans + ", '" + div_id + "')</script>"
                page << br()

def print_html_rule_text_detail_info(page, results, rules):
    """
    文本类规则的具体信息
    """
    for rule in rules:
        for key in results[rule[0]].keys():
            if "#" in key:
                index_id = key.replace("#", "-")
                div_id = rule[0] + "-" + index_id
                text_id = div_id + "-text"
                sql_fulltext = sqlparse.format(results[rule[0]][key]["sql_text"], reindent=True)
                sql_fulltext = json.dumps(sql_fulltext)
                stat_info = results[rule[0]][key]["stat"]
                temp_stat_columns = []
                temp_stat_info = []
                stat_id = div_id + "-stat"
                if stat_info:
                    for stat_key in stat_info[0].keys():
                        temp_stat_columns.append({"title": stat_key})
                    for stat in stat_info:
                        temp = []
                        for stat_key in stat.keys():
                            temp.append(str(stat[stat_key]))
                        temp_stat_info.append(temp)
                temp_stat_info = json.dumps(temp_stat_info)
                temp_stat_columns = json.dumps(temp_stat_columns)
                page << "<script>genMultiTextTable('#base', '" + div_id + "', '" + stat_id + "', " + temp_stat_info + ", " + temp_stat_columns + ", '" + text_id + "', " + sql_fulltext + ", '" + div_id + "')</script>"
                page << br()

def print_html_obj_detail_info(page, results, rules, rule_summary):
    """
    对象类规则的具体信息
    """
    for rule in rules:
        if results[rule[0]]["records"]:
            table_title = []
            records = []
            for data in rule_summary[rule[0]][2]:
                # table_title.append(data["parm_desc"])
                table_title.append({"title": data["parm_desc"]})
            for data in results[rule[0]]["records"]:
                records.append(data)
            table_title = json.dumps(table_title)
            records = json.dumps(records)
            page << "<script>genTable('#base', '" + rule[0] + "', '" + rule[0] + "_table', " + records + ", " + table_title + ",'" + rule[0] + "', '3', '" + rule[4] + "')</script>"
            page << br()
    page << br()