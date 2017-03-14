$(document).ready(function() {
    $("#table_info").parent().hide();
    var handleDatepicker = function() {
        $('#datepicker-default').datepicker({
            todayHighlight: true
        });
        $('#datepicker-inline').datepicker({
            todayHighlight: true
        });
        $('.input-daterange').datepicker({
            todayHighlight: true
        });
        $('#datepicker-disabled-past').datepicker({
            todayHighlight: true
        });
        $('#datepicker-autoClose').datepicker({
            todayHighlight: true,
            autoclose: true
        });
    };
    handleDatepicker();
    renderSwitcher();
    $(".to_oracle").show();
    $(".to_mysql").hide();
    $(".to_oracle").parent().parent().show();
    $("#pubIp").change(function(){
        var pubIp = $("#pubIp option:selected").text();
        data = {"ipaddress": pubIp}
        $.post("/new/version/sql/review/get/db/port", data, function(result){
            if (result["errcode"] === 70001) {
                $("#port").empty();
                listLength = result["port_list"].length;
                $("#port").append("<option>port</option>");
                for (var i = 0; i < listLength; i++) {
                    var name = "<option>" + result["port_list"][i] + "</option>"
                    $("#port").append(name)
                }
            }
            else {
                print_message("alert_message", "alert-danger", result["message"]);
            }
        });
    });
    $("#port").change(function(){
        var pubIp = $("#pubIp option:selected").text();
        var port = $("#port option:selected").val();
        data = {"ipaddress": pubIp, "port": port}
        $.post("/new/version/sql/review/get/db/user/list", data, function(result){
            if(result["errcode"] === 80055){
                $("#objname").empty();
                var user_list = result["user_list"];
                for(var i=0; i < result["user_list"].length; i++){
                    var name = "<option>" + result["user_list"][i] + "</option>"
                    $("#objname").prepend(name)
                }
            }
            else {
              print_message("alert_message", "alert-danger", result["message"]);
            }
        });
      });
    $("input[name='optionstask']").click(function(){
        var rule_type = $("input[name='optionstask']:checked").val();
        var port = $("#port option:selected").val();
        if(!port){
          $("input[name='optionstask']:checked").prop("checked", false);
          return
        }
        $(".to_oracle").parent().parent().show();
        var flag = ""
        if (rule_type === "sqlplan"){
          flag = "sqlplan"
        }else if(rule_type === "text"){
          flag = "text";
        }else if(rule_type === "obj"){
          flag = "obj"
          $(".to_oracle").parent().parent().hide();
          $(".to_mysql").parent().parent().hide();
        }else if(rule_type === "sqlstat"){
          flag = "sqlstat"
        }
        if(port === "1521"){
          if(rule_type === "text"){
            $(".to_oracle").hide();
            $(".to_mysql").show();
          }
          else{
            $(".to_oracle").show();
            $(".to_mysql").hide();
          }
        }else{
          $(".to_oracle").hide();
          $(".to_mysql").show();
        }
        $.get("/new/version/sql/review/get/struct", {"flag": flag, "port": port}, function(result){
              if(result["errcode"] === 80050){
                var columns = [
                      {"title": "规则名称"},
                      {"title": "规则概要"},
                      {
                         "title": "规则状态",
                          "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                           $(nTd).addClass('selectTd').attr('name', oData.rule_name + '_' + sData);
                         }
                      },
                      {
                        "title": "权重",
                        "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                           $(nTd).addClass('inputWeigth').attr('name', oData.rule_name + '_' + sData);
                         }
                      },
                      {
                        "title": "最高分",
                         "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                           $(nTd).addClass('inputMax').attr('name', oData.rule_name + '_' + sData);
                         }
                      },
                       {"title": "规则类型"},
                         //  "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                         //   $(nTd).addClass('inputMax').attr('name', oData.rule_name + '_' + sData);
                         // }
                      {"title": "db type"},
                      {"title": "exclude_type"}
                   ]
                    genTable("table_info", "struct_table", result["data"], columns);
                    $("#table_info").parent().show();
                }
            });
      })
    $("#task_execute").click(function(){
        var pubIp = $("#pubIp option:selected").text();
        var port = $("#port option:selected").val();
        var objname = $("#objname option:selected").val();
        var startdate = $("input[name='start']").val();
        var stopdate = $("input[name='stop']").val();
        var rule_type = $("input[name='optionstask']:checked").val();
        var oracle_date = $(".to_oracle").val()
        var data = {
          "oracle_date": oracle_date,
          "ipaddress": pubIp,
          "port": port,
          "objname": objname,
          "startdate": startdate,
          "stopdate": stopdate,
          "rule_type": rule_type
        }
        $.post("/new/version/sql/review/task/publish", data, function(result){
          if(result["errcode"] === 80058){
            alert(result["message"])
          }
          else{
            print_message("alert_message", "alert-danger", result["message"]);
          }
        });
    })
})
function genTable(domid, table_id, data, columns){
    $("#" + domid).empty();
    $("#" + domid).append('<table class=\"table table-striped table-bordered\" id=\"' + table_id + '\"></table>')
    var table = $("#" + table_id).dataTable({
        "data": data,
        // "columns": columns    
        "columns" : columns,
         "fnDrawCallback": function (data, x) {
            $('#' + table_id + ' tbody td.inputMax').editable('/new/version/sql/review/rule/info');
            $('#' + table_id + ' tbody td.selectTd').editable('/new/version/sql/review/rule/info', {data:{"ON": "ON", "OFF": "OFF"}, type: 'select', submit: 'OK'});
            // $('#' + table_id + ' tbody td.inputType').editable('/new/version/sql/review/rule/info');
        }
    });
    return table;
}
