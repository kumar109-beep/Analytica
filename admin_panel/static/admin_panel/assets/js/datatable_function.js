var EXPORT_EXCEL_NAME = "Export Data"

function isValidDate(dateString) {
    // var regEx = /^\d{4}-\d{2}-\d{2}$/;
    var regEx = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/;
    dateString = String(dateString);
    if(!dateString.match(regEx)) 
        return false;  // Invalid format
    else
        return true;
    // var d = new Date(dateString);
    // // console.log(d)
    // var dNum = d.getTime();
    // if(!dNum && dNum !== 0) return false; // NaN value, Invalid date
    // console.log(d.toISOString().slice(0,19), dateString)
    // return d.toISOString().slice(0,19) === dateString;
}

jQuery.fn.dataTable.ext.errMode = 'none';


function rbf_manager_formatter(row, data, idx, key)
{
    var CurrentDate = moment();
    // console.log(row, data, idx, key, "absar")
    var regEx = /^rbf_\d+$/;
    if (key.match(regEx))
    // if (key.indexOf("rbf_") >= 0)
    {
        rbf_comp = key.split('_');
        prev_rbf = 'rbf_'+(parseInt(rbf_comp[1])-1)

        rbf_status = data[key + "_status"]

        let icon = "";

        if(rbf_status == undefined)
        {
            console.log("Kindly Select the Current RBF column as well for proper Formatting   ")
        }
        else if(isValidDate(rbf_status.substring(0,19)))
        {
            rbf_status = moment(rbf_status.substring(0,19), "YYYY-MM-DDTHH:mm:ss").format('DD-MMM-YYYY HH:mm');
            icon = '<i class="fa fa-check-circle-o"></i>';
            jQuery(row).find('td:eq(' +idx+ ')').css('font-weight', 'bold');
        }
        else if(rbf_status === "N/A")
        {
            icon = '<i class="fa fa-clock-o"></i>';
            if (CurrentDate >= moment(data[key], "YYYY-MM-DD"))
            {
                console.log(data[key], "Suppose to Start")
                jQuery(row).find('td:eq(' +idx+ ')').addClass('blinking');
                rbf_status = "This cycle suppose to be started"
                icon = '<i style="color:red" class="fa fa-bell-o"></i>';
            }
        }
        else
        {
            icon = '<i class="fa fa-times-circle-o"></i>';
            jQuery(row).find('td:eq(' +idx+ ')').css('font-weight', 'bold');
        }

        jQuery(row).find('td:eq(' +idx+ ')').css('white-space', 'nowrap').append("<br />"+icon)

        if(rbf_status === "N/A")
        {
            rbf_status = "Not Created Yet";
        }
        
        rbf_status = " (" + rbf_status + ")";

        if(data[prev_rbf])
        {
            if(data[prev_rbf] != 'NaT')
            {
                let startDate = moment(data[prev_rbf], "YYYY-MM-DD");
                let endDate   = moment(data[key], "YYYY-MM-DD");
                let result =  endDate.diff(startDate, 'days');
                if(result == 184)
                {
                    jQuery(row).find('td:eq(' +idx+ ')').css("background-color", "#20A8D8").attr("title","On Time " + rbf_status);
                }
                else if(result < 184)
                {
                    jQuery(row).find('td:eq(' +idx+ ')').css("background-color", "#F86C6B").attr("title","Early " + rbf_status);
                }
                else if(result > 184)
                {
                    jQuery(row).find('td:eq(' +idx+ ')').css("background-color", "#FFC107").attr("title","Late " + rbf_status);
                }
                else //If Null date
                {
                    jQuery(row).find('td:eq(' +idx+ ')').attr("title","User Miss this Cycle "+ rbf_status);
                }
            }
            else
            {   
                jQuery(row).find('td:eq(' +idx+ ')').attr("title","Can't define performance as previous RBF not filled "+ rbf_status);
            }     
        }
        else
        {
            jQuery(row).find('td:eq(' +idx+ ')').css("background-color", "#4DBD74").attr("title","Started On "+ rbf_status);
        }
    }
}



function updateProgress (oEvent) {
    if (oEvent.lengthComputable) {
        jQuery("#data_table_section .btn, .btn-secondary, .btn-success").attr("disabled", true);
        jQuery('.export_xlsx_file').toggle();
        console.log('loading');
        var percentComplete = oEvent.loaded / oEvent.total * 100;
        console.log(percentComplete)
        // ...
    } else {
        console.log('something happening');
    }
}





var dataTable = "";

function data_table(columns, custom_data={}){
    let datatable_id = custom_data.dataTableId ? custom_data.dataTableId : 'master-details-data-table'
    custom_data.table_format_function = "rbf_manager_formatter"
    dataTable = jQuery('#' + datatable_id).DataTable( {
        autoWidth: false,
        fixedHeader: true,
        columns: columns,
        processing: true,
        stateSave: false,
        responsive: true,
        serverSide: true,
        deferRender: true,
        columnDefs: [
            // {//Add property for identifying the proper location of edit 
            //     "targets": [-1],
            //     "visible": false,
            //     "searchable": false
            // },
            // {
            //     render: function (data, type, row, meta){
            //         console.log(data, type, row, meta)
            //     }
            // }
            // {
            //     targets: -1,
            //     className: 'text-center'
            // }
            
            ],
        "ajax":{
            url : master_datatable_ajax_url,
            type: "post",  // method  ,by default get
            data: {csrfmiddlewaretoken: Cookies.get('csrftoken'), filters: JSON.stringify(custom_data.filters), sql_filter:custom_data.sql_filter, get_data_frame_function: custom_data.get_data_frame_function},
            beforeSend: function() {
                if (dataTable.hasOwnProperty('settings')) {
                    dataTable.settings()[0].jqXHR.abort();
                }
            },
            error: function(){  // error handling
                jQuery(".employee-grid-error").html("");
                jQuery("#employee-grid").append('<tbody class="employee-grid-error"><tr><th colspan="3">No data found in the server</th></tr></tbody>');
                jQuery("#employee-grid_processing").css("display","none");
            },  
        },
        rowCallback: function(row, data, index){
            // console.log(row, data, index, "danishabsar")
            let idx = 0;
            // jQuery.each(data, function(key, val)
            jQuery.each(columns, function(key, val)
            {
                key = val.data;
                val = data[key];
                if(headers_with_type[key] === "datetime64[ns]")
                {
                    x = moment(val, "YYYY-MM-DDTHH:mm:ss").format('DD-MMM-YYYY');
                    x = (x === "Invalid date") ? "" : x
                    jQuery(row).find('td:eq(' +idx+ ')').text(x);

                    eval(custom_data.table_format_function + `(row, data, idx, key)`)

                }

                if (jQuery.inArray(key, hidden_fields) == -1)
                {
                    idx++;
                }

                // idx++;/
            })
        },
        dom : 'lBf<"overflow_handle"t>ip',
        buttons: [
            {
                className:"btn-success",
                text : `<span style="display:none;" class="spinner-border spinner-border-sm export_xlsx_file" role="status" aria-hidden="true"></span>
                        <i class="fa fa-file-excel-o export_xlsx_file" />`,
                action: function ( e, dt, node, config ) {
                    let hold_params =  dt.ajax.params()
                    // hold_params['export'] = true;
                    hold_params['export'] = EXPORT_EXCEL_NAME;
                    var xhr = new XMLHttpRequest();

                    xhr.open('POST', dt.ajax.url(), true);

                    xhr.upload.onprogress = updateProgress;


                   

                    // xhr.responseType = 'arraybuffer';
                    xhr.responseType = 'blob';
                    xhr.onload = function () {
                        if (this.status === 200) {
                            var filename = "";
                            var disposition = xhr.getResponseHeader('Content-Disposition');
                            if (disposition && disposition.indexOf('attachment') !== -1) {
                                var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                                var matches = filenameRegex.exec(disposition);
                                if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
                            }
                            var type = xhr.getResponseHeader('Content-Type');

                            var blob;
                            if (typeof File === 'function') {
                                try {
                                    blob = new File([this.response], filename, { type: type });
                                } catch (e) { /* Edge */ }
                            }
                            if (typeof blob === 'undefined') {
                                blob = new Blob([this.response], { type: type });
                            }

                            if (typeof window.navigator.msSaveBlob !== 'undefined') {
                                // IE workaround for "HTML7007: One or more blob URLs were revoked by closing the blob for which they were created. These URLs will no longer resolve as the data backing the URL has been freed."
                                window.navigator.msSaveBlob(blob, filename);
                            } else {
                                var URL = window.URL || window.webkitURL;
                                var downloadUrl = URL.createObjectURL(blob);

                                if (filename) {
                                    // use HTML5 a[download] attribute to specify filename
                                    var a = document.createElement("a");
                                    // safari doesn't support this yet
                                    if (typeof a.download === 'undefined') {
                                        window.location = downloadUrl;
                                    } else {
                                        a.href = downloadUrl;
                                        a.download = filename;
                                        document.body.appendChild(a);
                                        a.click();
                                    }
                                } else {
                                    window.location = downloadUrl;
                                }

                                setTimeout(function () { URL.revokeObjectURL(downloadUrl); }, 100); // cleanup
                            }
                            jQuery("#data_table_section .btn, .btn-secondary, .btn-success").attr("disabled", false);
                            jQuery('.export_xlsx_file').toggle();
                        }
                    };
                    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
                    xhr.send(jQuery.param(hold_params));

                    // ======================
                }
            }

        ],
        "oLanguage": { "sSearch": "Search in all columns:" ,  "sLengthMenu": "Record Limit _MENU_" , "sProcessing": '<i class="fa fa-spinner fa-spin fa-3x fa-fw"></i><span class="sr-only">Loading..n.</span> '},
        lengthMenu: [
            [ 10, 25, 50, 100 ],
            [ '10 rows', '25 rows', '50 rows', '100 rows' ]
        ],
    } );
    // Store datatable set which is use for visualize data

    
    dataTable.MakeCellsEditable({
        "onUpdate": myCallbackFunction,
        "wrapperHtml" : `<div class="form-inline">{content}</div>`,
        "inputCss":'input-sm form-control-sm form-control',
        // "columns": [0,1,2,3],
        "allowNulls": {
            "columns": [3],
            "errorClass": 'error'
        },
        "confirmationButton": { // could also be true
            "confirmCss": 'btn btn-success btn-sm',
            "cancelCss": 'btn btn-danger btn-sm'
        },
        "inputTypes": [
            {
                "column": 0,
                "type": "text",
                "options": null
            },
            {
                "column":1, 
                "type": "list",
                "options":[
                    { "value": "1", "display": "Beaty" },
                    { "value": "2", "display": "Doe" },
                    { "value": "3", "display": "Dirt" }
                ]
            },
            {
                "column": 2,
                "type": "datepicker", // requires jQuery UI: http://http://jqueryui.com/download/
                "options": {
                    "icon": "http://jqueryui.com/resources/demos/datepicker/images/calendar.gif", // Optional
                    "format" : 'dd-M-yy',
                }
            }
             // Nothing specified for column 3 so it will default to text
            
        ]
    });












    AJAX_CALL = {url : dataTable.ajax.url(), params :dataTable.ajax.params() }

}

function myCallbackFunction (updatedCell, updatedRow, oldValue) {
    response = {}
    // console.log("The new value for the cell is: " + updatedCell.data());
    // console.log("The old value for that cell was: " + oldValue);
    // console.log( updatedRow.data(), updatedCell.index());

    if (oldValue === updatedCell.data())
    {
        return 0
    }
    var cols = dataTable.settings().init().columns;
    response["col_name"] = cols[updatedCell.index().column].data;

    response["old_val"] = oldValue;

    response["new_val"] = updatedCell.data();

    // response["frame"] = data_frame_name;
    response["frame"] = 1;

    response["user"] = 1;

    response["hash_code"] = updatedRow.data().hash;

    response["csrfmiddlewaretoken"] = Cookies.get('csrftoken')

    jQuery.ajax({
        // url: '/dashboard/request_edit/',
        url:'/dataframe/edits',
        // type: "GET",
        type: "POST",
        
        data: response,
        dataType: 'json',
        cache: true,
        success: function (data) {
            console.log(data)
        },
        error: function (data) {
            // alert("danish");
        }
    });


}

function destroyTable() {
    if (jQuery.fn.DataTable.isDataTable('#myAdvancedTable')) {
        table.destroy();
        table.MakeCellsEditable("destroy");
    }
}