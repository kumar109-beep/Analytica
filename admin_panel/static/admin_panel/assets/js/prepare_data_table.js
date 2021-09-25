
function prepare_data_table(data_table_parent, columns, custom_filters={})
        {
            let datatable_id = custom_filters.dataTableId ? custom_filters.dataTableId : 'master-details-data-table'
            
            // console.log(custom_filters, "danish", data_table_parent)
            dt_columns = [];
            w = jQuery('.overflow_handle').width();
            // console.log(w);
            console.log(columns);

            var table = `<table id="`+datatable_id+`" class="table table-striped table-bordered table-hover text-center"></table>`;
            data_table_parent.html(table);
            


            jQuery.each(columns, function (idx, vals) {
                // console.log(jQuery.type(vals), vals)
                if(jQuery.type(vals) === "object") 
                {
                    dt_columns.push(vals)
                }
                else if(jQuery.type(vals) === "string")
                {
                    dt_columns.push({title: vals.replace(/_/g, ' '), data:vals, visible: true, searchable:true });
                }
                else
                {
                    // console.log(vals)
                }
            });

            jQuery.each(hidden_fields, function (idx, vals) {
                dt_columns.push({title: vals.replace(/_/g, ' '), data:vals, visible: false, searchable:false });
            });
            

            dt_columns.push({title: "hash", data:"hash", visible:false, searchable:false});
            // Call Function to form data table

            console.warn(dt_columns)
            data_table(dt_columns, custom_filters);

            jQuery("thead", data_table_parent).addClass("text-capitalize");
            
            jQuery('.overflow_handle').css('width', w+'px');
        }