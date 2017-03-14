function genTable(domid, title, table_id, data, columns, div_id, flag){
    var desc = arguments[7] ? arguments[7] : "";
    var order = 0
    if (flag === "1" || flag === "2"){
      if (flag === "1") {
        order = 3;
      }
      $(domid).append('<div id=\"' + div_id + '\">\
                    <div class=\"panel panel-inverse\">\
                      <div class=\"panel-heading\">\
                          <h4 class=\"panel-title\">' + title + '</h4>\
                      </div>\
                      <div class=\"panel-body\">\
                          <div class=\"table-responsive\">\
                          <table class=\"table table-striped table-bordered table_rule\" id=\"' + table_id +'\"></table>\
                        </div>\
                      </div>\
              </div>')
    }
    else if(flag === "3"){
      $(domid).append('<div id=\"' + div_id + '\">\
                    <div class=\"panel panel-inverse\">\
                      <div class=\"panel-heading\">\
                          <h4 class=\"panel-title\">' + title + '</h4>\
                      </div>\
                      <div class=\"panel-body\">\
                      <button class=\"btn btn-primary m-r-5 m-b-5 accordion-toggle accordion-toggle-styled collapsed\" data-toggle=\"collapse\" href=\"#solution_' + title + '\">解决方案</button>\
                        <div id=\"solution_' + title + '\" class=\"panel panel-body panel-collapse collapse\">' + desc + '</div>\
                          <div class=\"table-responsive\">\
                          <table class=\"table table-striped table-bordered table_rule\" id=\"' + table_id +'\"></table>\
                        </div>\
                      </div>\
              </div>')
    }
    var table = $("#" + table_id).dataTable({
        "data": data,
        "columns": columns,
        "order": [[ order, "desc" ]],
        "language": {
           "sProcessing": "处理中...",
           "sLengthMenu": "显示 _MENU_ 项结果",
           "sZeroRecords": "没有匹配结果",
           "sInfo": "显示第 _START_ 至 _END_ 项结果，共 _TOTAL_ 项",
           "sInfoEmpty": "显示第 0 至 0 项结果，共 0 项",
           "sInfoFiltered": "(由 _MAX_ 项结果过滤)",
           "sInfoPostFix": "",
           "sSearch": "搜索:",
           "sUrl": "",
           "sEmptyTable": "表中数据为空",
           "sLoadingRecords": "载入中...",
           "sInfoThousands": ",",
           "oPaginate": {
               "sFirst": "首页",
               "sPrevious": "上页",
               "sNext": "下页",
               "sLast": "末页"
           }
        },
    });
    return table;
}
function genCharts(title, subtext, legend, rule_mark){
    var myChart;
    // require(['echarts', 'echarts/chart/pie', 'echarts/chart/funnel', 'echarts/chart/line'],
    $("#base").append('<div class=\"panel panel-inverse\">\
                      <div class=\"panel-heading\">\
                          <h4 class=\"panel-title\">' + title + '</h4>\
                      </div>\
                      <div class=\"panel-body\">\
                          <div class=\"table-responsive\">\
                          <div  id=\"rule_mark_pie\" style=\"height:400px\"></div>\
                        </div>\
                      </div>\
              </div>')

    function gen() {
            option = {
                    title : {
                        text: title,
                        subtext: subtext,
                        x: "center"
                    },
                    tooltip : {
                        trigger: 'items',
                        formatter: "{a} <br/>{b} : {c} ({d}分)"
                    },
                    legend: {
                        data: legend,
                        orient : 'vertical',
                        x : 'left',
                    },
                    toolbox: {
                        show : true,
                        feature : {
                            // mark : {show: true},
                            // dataView : {show: true, readOnly: false},
                            restore : {show: true},
                            saveAsImage : {show: true},
                            magicType : {
                            show: true, 
                            type: ['pie', 'funnel'],
                            option: {
                                funnel: {
                                    x: '50%',
                                    width: '50%',
                                    funnelAlign: 'left',
                                    max: 1548
                                }
                            }
                        },
                      }
                    },
                    calculable : true,
                    series : [
                        {
                            name: "规则扣分图",
                            type:'pie',
                            radius : '55%',
                            center: ['60%', '60%'],
                            data: rule_mark,
                        }
                    ]
                }; 
        var myChart = echarts.init(document.getElementById("rule_mark_pie"));
        myChart.setOption(option);
        // return myChart
        // });
        return myChart;
    }
    return gen();
}

function genMultiTable(domid, title, obj_id, obj_data, obj_columns, stat_id, stat_data, stat_columns, text_id, text, plan_id, plan, div_id){
    // $("#base").append("<table class=\"table table-striped table-bordered\" id=\"" + table_id + "\"></table>\"")
    // $(domid).append('<div id=\"' + div_id + '\">\
    //                     <div class=\"panel panel-inverse\">\
    //                       <div class=\"panel-heading\">\
    //                           <h4 class=\"panel-title\">' + title + '</h4>\
    //                       </div>\
    //                       <div class=\"panel-body\">\
    //                           <div class=\"table-responsive\">\
    //                           <table class=\"table table-striped table-bordered table_rule\" id=\"' + obj_id +'\"></table>\
    //                         </div>\
    //                       </div>\
    //               </div>')
    var sql_detail = '<div id=\"' + div_id + '\">\
                        <div class=\"panel panel-inverse\">\
                          <div class=\"panel-heading\">\
                              <h4 class=\"panel-title\">' + title + '</h4>\
                          </div>\
                          <div class=\"panel-body\">\
                              <div class=\"table-responsive\">\
                                <textarea id=\"' + text_id + '\" rows=\"8\" class=\"form-control\"></textarea>\
                              </div>\
                      '
    // var plan = '<div class=\"table-responsive\">\
    //                         <table class=\"table table-striped table-bordered table_rule\" id=\"' + plan_id + '\"><thead><tr><th>sql</th><th>OPTIONS</th><th>OBJECT_OWNER</th><th>OBJECT_NAME</th><th>COST</th></tr></thread></table>\
    //                       </div>\
    //                       '
    if (obj_columns.length){
      obj_table = '<div class=\"table-responsive\"><table class=\"table table-striped table-bordered table_rule\" id=\"' + obj_id +'\"></table></div>'
      sql_detail += obj_table
    }
    if(stat_columns.length){
      stat_table = '<div class=\"table-responsive\">\
                              <table class=\"table table-striped table-bordered table_rule\" id=\"' + stat_id +'\"></table>\
                              </div>\
                              '
      sql_detail += stat_table
    }
    sql_detail += "</div></div>"
    $(domid).append(sql_detail)
    var language = {
           "sProcessing": "处理中...",
           "sLengthMenu": "显示 _MENU_ 项结果",
           "sZeroRecords": "没有匹配结果",
           "sInfo": "显示第 _START_ 至 _END_ 项结果，共 _TOTAL_ 项",
           "sInfoEmpty": "显示第 0 至 0 项结果，共 0 项",
           "sInfoFiltered": "(由 _MAX_ 项结果过滤)",
           "sInfoPostFix": "",
           "sSearch": "搜索:",
           "sUrl": "",
           "sEmptyTable": "表中数据为空",
           "sLoadingRecords": "载入中...",
           "sInfoThousands": ",",
           "oPaginate": {
               "sFirst": "首页",
               "sPrevious": "上页",
               "sNext": "下页",
               "sLast": "末页"
           }
        }
    if (obj_columns.length){
        $("#" + obj_id).dataTable({
          "data": obj_data,
          "columns": obj_columns,
          "paging":   false,
          "searching": false,
          "language": language
      });
    }
    if(stat_columns.length){
        $("#" + stat_id).dataTable({
          "data": stat_data,
          "columns": stat_columns,
          "paging":   false,
          "searching": false,
          "language": language
      });
    }
    $("#" + text_id).val(text);
    // $.each(plan, function(key, val){
    //       var td = "<td>" + val["OPERATION_DISPLAY"] + "</td><td>" + val["OPTIONS"] + "</td><td>" + val["OBJECT_OWNER"] + "</td><td>" + val["OBJECT_NAME"] + "</td><td>" + val["COST"] + "</td>"; 
    //       if (val["PARENT_ID"] === null){
    //         var tr=$("<tr></tr>").addClass("treegrid-" + (parseInt(val["ID"]) + 1)).appendTo($('#' + plan_id)).html(td);
    //       }
    //       else{
    //         var tr=$("<tr></tr>").addClass("treegrid-" + (parseInt(val["ID"]) + 1)).addClass("treegrid-parent-" + (parseInt(val["PARENT_ID"]) + 1)).appendTo($('#' + plan_id)).html(td);
    //       }
    //     });
    // $("#" + plan_id).treegrid({
    //         expanderExpandedClass: 'glyphicon glyphicon-minus',
    //         expanderCollapsedClass: 'glyphicon glyphicon-plus'
    // });

}

function genMultiTextTable(domid, title, stat_id, stat_data, stat_columns, text_id, text, div_id){
    var sql_detail = '<div id=\"' + div_id + '\">\
                        <div class=\"panel panel-inverse\">\
                          <div class=\"panel-heading\">\
                              <h4 class=\"panel-title\">' + title + '</h4>\
                          </div>\
                          <div class=\"panel-body\">\
                              <div class=\"table-responsive\">\
                                <textarea id=\"' + text_id + '\" rows=\"8\" class=\"form-control\"></textarea>\
                              </div>\
                      '
    if(stat_columns.length){
      stat_table = '<div class=\"table-responsive\">\
                              <table class=\"table table-striped table-bordered table_rule\" id=\"' + stat_id +'\"></table>\
                              </div>\
                              '
      sql_detail += stat_table
    }
    sql_detail += "</div></div>"
    $(domid).append(sql_detail)
    var language = {
           "sProcessing": "处理中...",
           "sLengthMenu": "显示 _MENU_ 项结果",
           "sZeroRecords": "没有匹配结果",
           "sInfo": "显示第 _START_ 至 _END_ 项结果，共 _TOTAL_ 项",
           "sInfoEmpty": "显示第 0 至 0 项结果，共 0 项",
           "sInfoFiltered": "(由 _MAX_ 项结果过滤)",
           "sInfoPostFix": "",
           "sSearch": "搜索:",
           "sUrl": "",
           "sEmptyTable": "表中数据为空",
           "sLoadingRecords": "载入中...",
           "sInfoThousands": ",",
           "oPaginate": {
               "sFirst": "首页",
               "sPrevious": "上页",
               "sNext": "下页",
               "sLast": "末页"
           }
        }
    if(stat_columns.length){
        $("#" + stat_id).dataTable({
          "data": stat_data,
          "columns": stat_columns,
          "paging":   false,
          "searching": false,
          "language": language
      });
    }
    $("#" + text_id).val(text);
}