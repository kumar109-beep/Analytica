// var advance_filter = "";
// var AJAX_CALL = {};
        // var myarray = ["district_name", "block_name", "sub_center_name"];
        // var select_box_value = {};

        // jQuery.each(myarray, function(idx, val){
        //     load_select_box(val);
        // })

        // function load_select_box(head)
        // {
        //     jQuery.ajax({
        //         url: load_select_box_url,
        //         type: "GET",
        //         data: {"head":head, "frame_name":data_frame_name},
        //         dataType: 'json',
        //         cache: true,
        //         success: function (data) {
        //             options = "";
        //             jQuery.each(data, function(idx, val){
        //                 options += "<option value='" + val + "'>" + val + "</option>"
        //             }) 
        //             select_box_value[head] = options;
        //         },
        //         error: function (data) {
        //             // alert("danish");
        //         }
        //     });
        // }

        // jQuery(document).ready(function() {
        	// var dynamic_form =  jQuery("#dynamic_form").dynamicForm("#dynamic_form","#plus5", "#minus5", {
		    //     limit:10,
		    //     formPrefix : "dynamic_form",
		    //     normalizeFullForm : false
		    // });

            // jQuery("#draw_chart").click(function(){
            //     jQuery("#chart_panel").fadeToggle();
            //     var labels  = [1,2,3,4,5,6,7,8,9];
            //     var dataset = [100,22,33,422,55,66,72,83,93];

            //     var x_label = jQuery("#x_axis").val();
            //     var y_label = jQuery("#y_axis").val();
                
            //     var ctx = document.getElementById( "intractive_chart" );
            //     var myChart = new Chart( ctx, {
            //         type: 'bar',
            //         data: {
            //             labels: labels,
            //             datasets: [
            //                 {
            //                     label: "Custom Legend",
            //                     data:  dataset,
            //                     borderColor: "rgba(19, 132, 150, 0.9)",
            //                     backgroundColor: "rgba(19, 132, 150, 0.3)"
            //                 }
            //             ]
            //         },
            //         options: {
            //             // plugins: {
            //             //     labels:plugin_label_conf
            //             // },
            //             animation: {
            //                 animateRotate: true,
            //                 animateScale: true
            //               },
            //             title: {
            //                 display: true,
            //                 text: 'ALL ',
            //                 fontFamily : 'Segoe UI'
            //             },
            //             tooltips: {
            //                 mode: 'index',
            //                 intersect: false
            //             },
            //             responsive: true,
            //             scales: {
            //                 xAxes: [{
            //                     scaleLabel: {
            //                         display: true,
            //                         labelString: x_label.replace(/_|name/g, "").toUpperCase(),
            //                         fontSize: 14,
            //                         fontFamily : 'Segoe UI'
            //                     },
            //                     ticks: {
            //                         autoSkip : false,
            //                         callback: function(value, index, values) {
            //                             return value;
            //                         }
            //                     },
            //                 }],
            //                 yAxes: [{
            //                     scaleLabel: {
            //                         display: true,
            //                         labelString: y_label.replace(/_|name/g, "").toUpperCase(),
            //                         fontSize: 14,
            //                         fontFamily : 'Segoe UI'
            //                     },
            //                     ticks: {
            //                         beginAtZero: true,
            //                         // max: 100
            //                     }
            //                 }]
            //             }
            //         }
            //     } );
            //     // jQuery("#intractive_chart").toggle();
            //     jQuery("#chart_panel").slideToggle();
            // })

		    // jQuery("#dynamic_form #minus5").on('click', function(){
		    // 	var initDynamicId = jQuery(this).closest('#dynamic_form').parent().find("[id^='dynamic_form']").length;
		    // 	if (initDynamicId === 2) {
		    // 		jQuery(this).closest('#dynamic_form').next().find('#minus5').hide();
		    // 	}
		    // 	jQuery(this).closest('#dynamic_form').remove();
            // });

            function init_sql_filter()
            {
                custom_filters = {}
                sql_filter = jQuery('#builder-basic').queryBuilder('getSQL');
                if(sql_filter != null)
                {
                    sql_string = sql_filter.sql;
                    jQuery.each(Object.keys(headers_with_type), function(index, attr){
                        var regex = new RegExp(attr, 'g');
                        sql_string =  sql_string.replace(regex, '`'+attr+'`');
                    })
                    custom_filters.sql_filter = sql_string;
                    prepare_data_table(data_table_parent, jQuery("#column_filter").val(), custom_filters );
                    return true
                }
                else
                {
                    return false
                }
            }
            
            jQuery("#filter_set").click(function(){
                if(init_sql_filter())
                    jQuery('#largeModal').modal('toggle');
            })

            

        var data_table_parent = "";
        // function prepare_data_table(data_table_parent, columns, custom_filters={})
        // {
        //     dt_columns = [];
        //     w = jQuery('.overflow_handle').width();
        //     console.log(w);
        //     console.log(columns);
            
        //     var table = `<table id="master-details-data-table" class="table table-striped table-bordered table-hover"></table>`;
        //     data_table_parent.html(table);
        //     jQuery.each(columns, function (idx, vals) {
        //         dt_columns.push({title: vals.replace(/_/g, ' '), data:vals});
        //     });

        //     dt_columns.push({'data':"hash"});
        //     // Call Function to form data table
        //     data_table(dt_columns, custom_filters);

        //     jQuery("thead", data_table_parent).addClass("text-capitalize");
            
        //     jQuery('.overflow_handle').css('width', w+'px');
        // }
        
        function init_data_table()
        {
            prepare_data_table(data_table_parent, jQuery("#column_filter").val() );
        }

        //Reset advane filter if columns chnage
        jQuery("#column_filter").change(function(){
            jQuery("#builder-basic").queryBuilder('destroy')
            load_advance_filter();
        })


        function load_advance_filter()
        {
            // let multi_select_allow = ["district_name", "block_name"];
            let multi_select_allow = [];
            filters = [];
            // jQuery.each(jQuery("#column_filter").val(), function(idx, val){
            jQuery("#column_filter > option:selected").each(function() {
                dataType = jQuery(this).attr('dtype'); 
                if(jQuery.inArray(dataType, multi_select_allow) != -1)
                {
                    filters.push({id:val, label:val, type:'string', input: 'select', multiple: true, values: {
                                    1: 'Books',
                                    2: 'Movies',
                                    3: 'Music',
                                    4: 'Tools',
                                    5: 'Goodies',
                                    6: 'Clothes'
                                    },
                                    operators: ['in', 'not_in'],
                                    plugin: 'chosen',
                                    validation: {allow_empty_value: false},
                                    valueSetter: function(rule, value) {
                                        if (!value) return;
                                        rule.$el.find('.rule-value-container select').val(value).change().trigger('chosen:updated');
                                    }
                                })
                }
                else if(dataType === "int64")
                {
                    filters.push({id:this.value, label:this.value, type:'integer'})
                }
                else
                {
                    filters.push({id:this.value, label:this.value, type:'string'})
                }
                
            });

            // jQuery("#column_filter > option:selected").each(function() {
            //     alert(this.text + ' ' + this.value);
            // });

            jQuery('#builder-basic').queryBuilder({
                plugins: ['bt-tooltip-errors'],
                filters: filters
            });
        }

        
    
        jQuery("#submit").click(function () { 
            if(! init_sql_filter())
                prepare_data_table(data_table_parent, jQuery("#column_filter").val(), custom_filters  );
        });
        
        // jQuery("#reset").click(function () { 
        //     // add_filter(filters.reverse().pop(), filters[0]);
        // })

        function draw_table(table_data)
        {   
            jQuery("#data_table_section").html(table_data);
        }

        jQuery("#customizer").click(function(){
            jQuery("#customizer_panel").slideToggle("slow");
        })

        // jQuery("#visualize").click(function(){
        //     // jQuery("#customizer_panel").slideToggle("slow");
        //     console.log(AJAX_CALL);
        //     ajax_call(AJAX_CALL.url, AJAX_CALL.params);

        // })


// function ajax_call(url, params)
//     {
//         return jQuery.ajax({
//             url: url,
//             type: 'GET',
//             data: params,
//             dataType: 'json',
//             success: function (data) {
//                 $x_axis = jQuery("#x_axis");
//                 $y_axis = jQuery("#y_axis");
//                 $x_axis.empty().append(jQuery("<option />").val("---X-AXIS---").text("---X-AXIS---"));
//                 $y_axis.empty().append(jQuery("<option />").val("---Y-AXIS---").text("---Y-AXIS---"));  
//                 jQuery.each(params.columns , function(idx, item) {
//                     $x_axis.append(jQuery("<option />").val(item.data).text(item.data));
//                     $y_axis.append(jQuery("<option />").val(item.data).text(item.data));
//                 });
//             },
//             error: function (data) {
//                 alert("Error");
//             }
//         });
//     }

function prepare_visualize() {
    var vis_data = jQuery("#master-details-data-table").DataTable().rows().data();
    var my_data = []
    my_data.push(Object.keys(vis_data[0]))
    var i =0;
    while(i != -1)
    {
        if(i in vis_data){
            my_data.push(Object.values(vis_data[i]));
            i += 1;
        }
        else
        {
            i= -1;
        }
    }
    var renderers = jQuery.extend(
                    jQuery.pivotUtilities.renderers,
                    jQuery.pivotUtilities.plotly_renderers,
                    jQuery.pivotUtilities.d3_renderers,
                    jQuery.pivotUtilities.export_renderers
                    );
    jQuery("#output").pivotUI(my_data, {
    hiddenAttributes: [""],
    renderers: renderers }, true);
}