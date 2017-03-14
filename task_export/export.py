# -*- coding: utf-8 -*-

import tarfile
import sys
import imp

from task_export.utils import print_html_script
from task_export.utils import print_html_body
from task_export.utils import print_html_js
from task_export.utils import print_html_chart
from task_export.utils import print_html_rule_table
from task_export.utils import print_html_rule_detail_table
from task_export.utils import print_html_rule_detail_info
from task_export.utils import print_html_rule_text_detail_info
from task_export.utils import print_html_obj_detail_info

if sys.version_info[0] == 2:
    reload(sys) 
    sys.setdefaultencoding('utf-8')



def main_task(client, task_uuid, page):
    """
    导出任务功能，获取任务id，匹配规则类型，生成离线页面等
    """
    results = client.get_collection("results").\
                find_one({"task_uuid": task_uuid})
    job_info = client.get_collection("job").\
                find_one({"id": task_uuid})
    rule_type = job_info["desc"]["rule_type"]
    rule_info = client.get_collection("rule").\
                    find({"rule_type": rule_type.upper()})
    search_temp = {}
    port = ""
    rule_summary = {}
    for value in rule_info:
        if rule_type == "OBJ":
            rule_summary.update({
                value["rule_name"]: [
                    value["rule_summary"],
                    value["exclude_obj_type"],
                    value["output_parms"],
                    "<br>".join(value["solution"])
                ],
            })
        else:
            rule_summary.update({
                value["rule_name"]: [
                    value["rule_summary"],
                    value["exclude_obj_type"],
                    "<br>".join(value["solution"])
                ],
            })
    if int(job_info["desc"]["port"]) == 1521:
        port = 1521
        db_type = "O"
    else:
        port = job_info["desc"]["port"]
        db_type = "mysql"
    score = []
    [score.append(float(data["max_score"]))
            for data in client.get_collection("rule").\
                find({"db_type": db_type, "rule_type": rule_type.upper()})]
    total_score = sum(score)
    ipaddress = job_info["desc"]["db_ip"]
    schema = job_info["desc"]["owner"]
    rules = []
    if rule_type.upper() == "OBJ":
        for key, value in results.items():
            if isinstance(results[key], dict):
                if value["records"]:
                    rules.append([
                        key,
                        rule_summary[key][0],
                        len(value["records"]),
                        value["scores"],
                        rule_summary[key][3]
                    ])
    elif rule_type.upper() in ["SQLPLAN", "SQLSTAT", "TEXT"]:
        for key, value in results.items():
                if isinstance(results[key], dict):
                    num = 0
                    for temp in results[key].keys():
                        if "#" in temp:
                            num += 1
                    rules.append([
                        key,
                        rule_summary[key][0],
                        num, value.get("scores", 0),
                        rule_summary[key][2]
                    ])
    print_html_body(page, str(ipaddress), str(port), str(schema))
    print_html_js(page)
    print_html_chart(total_score, page, rules)
    print_html_rule_table(page, ipaddress, port, schema, rules)
    if rule_type.upper() == "OBJ":
        print_html_obj_detail_info(page, results, rules, rule_summary)
    else:
        print_html_rule_detail_table(page, results, rules, rule_type)
        if rule_type.upper() == "SQLPLAN" or rule_type.upper() == "SQLSTAT":
            print_html_rule_detail_info(page, results, rules)
        elif rule_type.upper() == "TEXT":
            print_html_rule_text_detail_info(page, results, rules)

def export_task(client, task_uuid, file_id):
    """
    生成报告的离线压缩包，可配合下载服务器使用
    """
    v_page = print_html_script()
    main_task(client, task_uuid, v_page)
    v_page.printOut("sqlreview.html")
    v_page.printOut("task_export/sqlreview.html")
    path = "task_export/downloads/" + file_id + ".tar.gz"
    tar = tarfile.open(str(path), "w:gz")
    tar.add("task_export/css")
    tar.add("task_export/assets")
    tar.add("task_export/js")
    tar.add("task_export/sqlreview.html")
    tar.add("task_export/readme.txt")
    tar.close()
