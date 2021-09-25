// =#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=# Start Global Valibale #=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#
var tagline = "";
var chart_order = "" //["district_name", "block_name", "sub_center_name", "village_name"];
var activated_graph_x_axis;
var stage_capture = [];
var activated_function = "";
var modal_chart_id = "intractive_chart";
// Hold Nested Condition string and actual value
var condition_string = [];
var chart_filters = [];
var special_column_of_list = "";

var stack_bar_head_conf = {};
// Global Varibale to hold X, Y value which will use by contex menu
var X, Y, is_dataset_adde, myChart, X_label, Y_label;
var $menu = jQuery('#contextMenu');
var $drillDownOption = jQuery('#menu-item-drill-down');
var configuration_set = ""
var SORTABLE_DATA = {}
var ChartColor

// var DataFrame = dfjs.DataFrame;

chartColors = {
    blue: 'rgb(54, 162, 235)',
    red: 'rgb(255, 99, 132)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(75, 192, 192)',
    purple: 'rgb(153, 102, 255)',
    orange: 'rgb(255, 159, 64)',
    grey: 'rgb(201, 203, 207)',
    olive: 'rgb(128, 128, 0)',
    aqua: 'rgb(0, 255, 255)',
    teal: 'rgb(0, 128, 128)',
    darkgolden: 'rgb(184,134,11)',
    tan: 'rgb(210,180,140)',
    skyblue: 'rgb(135,206,235)',
    voilet: 'rgb(238,130,238)',
    slategray: 'rgb(112,128,144)',
    mistyrose: 'rgb(255,228,225)',
    khaki: 'rgb(240,230,140)',
};

var $chart_back_button = jQuery('#back_button');
var $data_table_parent = jQuery("#data_table_section");
var $chart_rendring_area = jQuery("#chart_rendring_area");

var DRAW_CHART_FUNCTIONS = ""

var dynamicColors = function() {
    var r = Math.floor(Math.random() * 255);
    var g = Math.floor(Math.random() * 255);
    var b = Math.floor(Math.random() * 255);
    return "rgb(" + r + "," + g + "," + b + ")";

    // return '#'+(Math.random()*0xFFFFFF<<0).toString(16);
};

Chart.defaults.global.plugins = {
    labels : false
};
// =#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#= End Global Valibale =#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#

// This function ensure that chart is draw when model is loaded
function draw_chart_layout(layout_function)
{
    jQuery('#largeModal').on('shown.bs.modal', function (e) {
        console.log("before preare call");
        eval(layout_function);
    })
}

jQuery('#largeModal').on('shown.bs.modal', function (e) {
    eval(DRAW_CHART_FUNCTIONS);
})




// Start Cards Generation for Analytics page

function genCard(card_conf, base_drill)
{

    var filter_html = "";
    jQuery.each(card_conf.filters, function(idx, filter){
        filter_html += (`<li class="list-group-item"><span class="ti-arrows-vertical"></span> <input type="checkbox"  value="` + filter +`", name="filter[]" checked> ` + filter.replace(/_/g, " ") +`</li>`);
    });

    jQuery.each(base_drill, function(idx, filter){
        if(filter === "state_name" || filter === "region_name" || filter === "STATE")
        {
            filter_html += (`<li class="list-group-item"><span class="ti-arrows-vertical"></span> <input type="checkbox"  value="` + filter +`", name="filter[]"> ` + filter.replace(/_/g, " ").replace(" name", "") +`</li>`);
        }
        else
        {
            filter_html += (`<li class="list-group-item"><span class="ti-arrows-vertical"></span> <input type="checkbox"  value="` + filter +`", name="filter[]" checked> ` + filter.replace(/_/g, " ").replace(" name", "") +`</li>`);
        }
    });

    var widget_heading_html = "";
    jQuery.each(card_conf.counts, function(idx, count){
        console.log(idx, count)
        if(jQuery.isNumeric(count))
        {
            count = (count % 1 == 0)? count : count.toFixed(2);
            widget_heading_html += ` <span class="count">` + count +`</span>` + ((card_conf.count_text[idx].split(" ")[0].length == 1)? "" : " ") + card_conf.count_text[idx] ;
        }
        else
        {
            widget_heading_html += count + ((card_conf.count_text[idx].split(" ")[0].length == 1)? "" : " ") + card_conf.count_text[idx] ;
        }
        
        
    });
    
    return  `<div class="col-sm-6 col-lg-4">
                <div class="card_size card text-white bg-flat-color-`+ (jQuery(".card_size").length + 1) +`">
                    <div class="card-body pb-0" chartfor="`+ card_conf.chartfor +`">
                        <div class="dropdown explore_button">
                            <button class="btn bg-transparent dropdown-toggle theme-toggle text-light" type="button" id="dropdownMenuButton1" data-toggle="dropdown">
                                <i class="fa fa-gears"></i>
                            </button>
                            <div class="dropdown-menu custom_modification" style="left: -98px !important;" aria-labelledby="dropdownMenuButton1">
                                <div class="dropdown-menu-content">
                                    <a class="dropdown-item"><b>Filter Hierarchy</b></a>
                                    <ul class="sortable list-group text-capitalize">
                                        `
                                        + filter_html +
                                        `
                                    </ul>
                                </div>
                            </div>
                        </div>
                        <div class="view_detail_chart">
                            <h4 class="mb-0">
                                `
                                + widget_heading_html +
                                `
                            </h4>
                            <p class="text-light">`+ card_conf.count_tagline +` &nbsp; </p>
                            <div class="chart-wrapper px-0" >
                                <canvas id="`+ card_conf.chartfor +`"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`;
}

// End Card Generation Function




function adjuest_filter(filter_list, request_type)
{
    var filtrable_drill_down = ['region_name','district_name'];
    jQuery.each(filtrable_drill_down, function(idx, fdd){
        if(jQuery.inArray(fdd, filter_list) == -1) {
            return filter_list
        }
    })
    var remove_attr = "";
    if(request_type === "District")
    {
        remove_attr = "region_name"
    }

    var result = filter_list.filter(function(elem){
        return elem != remove_attr
    });

    return result;
}



// jQuery('.dropdown-item').click(function(e) {
    // jQuery('.mt-3').on('click', 'view_detail_chart', function(e) {
    
// jQuery('.view_detail_chart').click(function(e) {
jQuery('.mt-3').on('click', '.view_detail_chart', function(e) {

    tagline = (jQuery(this).find('p').text());
    // Enable sclae ticks for widget charts
    Chart.defaults.scale.ticks.display = true;
    stack_bar_head_conf = {};
    jQuery("#onchart_label").prop("checked", false);
    jQuery(".chart_label_type").hide();
    jQuery("#chart_select").val("")
    jQuery("#intractive_chart_table_area").html("")
    $chart_rendring_area.show();
    special_column_of_list = "";
    var ele = jQuery(this).parent();
    chart_order = []
    jQuery.each(ele.find("li input[name='filter[]']:checked").serializeArray(), function(idx, val){
        chart_order.push(val.value);
    })
    $data_table_parent.hide();
    condition_string = [];
    chart_filters = [];
    jQuery("#largeModal").modal('show');
    activated_graph_x_axis = chart_order[0];
    stage_capture = [];
    $drillDownOption.show();
    jQuery("#drill_down_menu").removeClass("menu-item-disabled"); 
    chart_for = ele.attr('chartfor');
       
    chart_conrol = {

        "worker_count": `                   prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                            configuration_set.modify_dataset = { rename_data_set : {size_of_hash:"No of "+frame_name} }

                                            
                                            draw_chart(configuration_set)`,
    
        "worker_caste": `
                                            prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["caste"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set)
                                            `,
    
        "asha_on_population": `             
                                            prepare_basic_chart(true);  
                                            head_operation = {"population":"sum", "hash":"size"}
                                            configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], sort_by:"mean_of_population" };
                                            configuration_set.modify_dataset = { rename_data_set : {size_of_hash:"No of Asha", sum_of_population:"required no of asha"} }
                                            configuration_set.modify_dataset.data_set_operation = {sum_of_population:{operator : "/", value:1000} }
                                            console.log(configuration_set);
                                            draw_chart(configuration_set);
        
                                            `,
    
        "age_distribution": `               prepare_basic_chart(false);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                            configuration_set.modify_dataset = { rename_data_set : {size_of_hash:"No of "+frame_name} }
                                            draw_chart(configuration_set);
                                            `,
    
        "available_mobile": `               prepare_basic_chart(false);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[{attr:"mobile_status", operator:"==", value:"Invalid"}] };
                                            configuration_set.modify_dataset = { rename_data_set : {size_of_hash:"No of "+frame_name} }
                                            draw_chart(configuration_set) 
                                            jQuery("#largeModalLabel").text(frame_name.toUpperCase()+" Invalid Mobile Numbers");
                                            `,
    
        "asha_avarage_distribution": `
        
                                            
                                            prepare_basic_chart(true);  
                                            head_operation = {"population":"mean"}
                                            configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], sort_by:"mean_of_population" };
                                            draw_chart(configuration_set);
                                            set_threshold_values({ id: 'hline1', mode: "horizontal", scale_id: "y-axis-0", value: 1500, label_text: "Maximum Allowed" , color:"red" });
                                            set_threshold_values({ id: 'hline2',mode: "horizontal", scale_id: "y-axis-0", value: 1000, label_text: "Minimum Allowed", color:"green" });
                                         `,
    
        "asha_engagement": `                
                                            prepare_basic_chart(false);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                            configuration_set.modify_dataset = { rename_data_set : {size_of_hash:"No of "+frame_name} }
                                            draw_chart(configuration_set);
                                            jQuery("#largeModalLabel").text(frame_name.toUpperCase()+" Enrollment Distribution");
                                            `,
    
        "educational_overview": `
                                            
        prepare_basic_chart(true);  
        head_operation = {"hash":"size"}
        configuration_set = {group_heads:["educational_qualification"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };

        // configuration_set.headDatasetConf = { total : {
        //                                         type: "line",
        //                                         backgroundColor: "transparent",
        //                                         borderColor: "#272C33",
        //                                         borderWidth : 1,
        //                                         } }


        draw_chart(configuration_set);
        
                                            `,
    
        "worker_vs_population":             `prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                            configuration_set.modify_dataset = { rename_data_set : {size_of_hash:"No of "+frame_name} }
                                            draw_chart(configuration_set);
                                            `,
    
        "asha_per_worker": `                prepare_basic_chart(false);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[{attr:"sub_center_name", operator:"!=", value: "At PHC"}, {attr:"sub_center_name", operator:"!=", value: "At CHC"}] };
                                            configuration_set.modify_dataset = { rename_data_set : {size_of_hash:"No of "+frame_name} }
                                            draw_chart(configuration_set) 
                                            jQuery("#largeModalLabel").text("ASHA per "+frame_name.toUpperCase());
                                            
                                            `,
    
        "job_type": `
                                            prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["job_type"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set)
                                            `,
    
        "current_payment": `                prepare_basic_chart(false);  
                                            head_operation = {"subtotal":"sum"}
                                            configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                            draw_chart(configuration_set);
                                            `,
    
        "head_payment_distribution": `      
                                            heads = Object.keys(headers_with_type).filter(function(x){ return x.endsWith("_total") })
                                            data_types = Array(heads.length).fill("sum")
                                            prepare_basic_chart(true);  
                                            configuration_set = {head: heads, data_type: data_types, filters:[] };
                                            draw_chart(configuration_set);
                                            `,
    
        "avg_current_payment": `            
                                            prepare_basic_chart(false);  
                                            head_operation = {"subtotal":"mean"}
                                            configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                            draw_chart(configuration_set)
                                            `
                                            ,
    
        "amount_distribution_in_worker": `  
        
                                            prepare_basic_chart(false);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                            draw_chart(configuration_set)
                                            `,
    
        "current_not_paid": `     
                                            prepare_basic_chart(false);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], get_data_frame_function : worker + "_not_paid_frame" };
                                            draw_chart(configuration_set)
                                            `,
    
    
        "bcpm_status": `                    
                                            prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["bcpm_status"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set);
                                            `,
    
    
        "moic_status": ` 
                                            prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["moic_status"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set);
                                            `,
    
    
        "bam_status": `                     
                                            prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["bam_status"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set);
                                            `,
    
        "worker_claimed_current": `         
                                            prepare_basic_chart(false);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], get_data_frame_function : worker + "_not_paid_frame" };
                                            draw_chart(configuration_set)
                                            `,
    
    
        "bcpm_performance": `           
                                            prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["bcpm_performance"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set);    
                                            `,
    
    
        "moic_performance": `               prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["moic_performance"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set); 
                                            `,
    
    
        "bam_performance": `                prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["bam_performance"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set); 
                                            `,
    
        "anm_at_phc": `                     
                                            prepare_basic_chart(false);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[{attr:"sub_center_name", operator:"==", value: "At PHC"}], };
                                            draw_chart(configuration_set)
                                            `,
    
    
        "anm_at_chc": `
                                        prepare_basic_chart(false);  
                                        head_operation = {"hash":"size"}
                                        configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[{attr:"sub_center_name", operator:"==", value: "At CHC"}], };
                                        draw_chart(configuration_set)
        
                                        `,
    
    
        "bank_engagement": `           
                                            prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["ctype"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set); 

                                            configuration_set.headDatasetConf = {   HCMC_size_of_hash : {label : "No. of HCMC"}, 
                                                                                    HSCMC_size_of_hash : {label : "No. of HSCMC"},
                                                                                    VHC_size_of_hash : {label : "No. of VHC"}
                                                                                }

                                            `,

        "committee_chairman": `
                                            prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["ctype"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                            
                                            configuration_set.headDatasetConf = {   HCMC_size_of_hash : {label : "No. of HCMC"}, 
                                                                                    HSCMC_size_of_hash : {label : "No. of HSCMC"},
                                                                                    VHC_size_of_hash : {label : "No. of VHC"}
                                                                                }
                                            draw_chart(configuration_set);
                                            `,

        "committee_co_chairman": `
                                            prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["ctype"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                            
                                            configuration_set.headDatasetConf = {   HCMC_size_of_hash : {label : "No. of HCMC"}, 
                                                                                    HSCMC_size_of_hash : {label : "No. of HSCMC"},
                                                                                    VHC_size_of_hash : {label : "No. of VHC"}
                                                                                }
                                            draw_chart(configuration_set);
                                            `,
    
    
        "nhp_total_committee_population": `
                                            prepare_basic_chart(true);  
                                            head_operation = {"Population Covered":"sum"}
                                            configuration_set = {group_heads:["ctype"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set);

                                            configuration_set.headDatasetConf = {   'HCMC_sum_of_Population Covered' : {label : "Population at HCMC"}, 
                                                                                    'HSCMC_sum_of_Population Covered' : {label : "Population at HSCMC"},
                                                                                    'VHC_sum_of_Population Covered' : {label : "Population at VHC"}
                                                                                }


                                            `,
    
    
        "nhp_committee_type": `             
                                            prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["ctype"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set);

                                            configuration_set.headDatasetConf = {   HCMC_size_of_hash : {label : "No. of HCMC"}, 
                                                                                    HSCMC_size_of_hash : {label : "No. of HSCMC"},
                                                                                    VHC_size_of_hash : {label : "No. of VHC"}
                                                                                }

                                            `,
    
        "nhp_committee_enrollment": `       prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["ctype"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set);

                                            configuration_set.headDatasetConf = {   HCMC_size_of_hash : {label : "No. of HCMC"}, 
                                                                                    HSCMC_size_of_hash : {label : "No. of HSCMC"},
                                                                                    VHC_size_of_hash : {label : "No. of VHC"}
                                                                                }

                                            `,
    
    
        "nhp_population_per_committee": `   
                                            prepare_basic_chart(true);  
                                            head_operation = {"Population Covered":"mean"}
                                            configuration_set = {group_heads:["ctype"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set);

                                            configuration_set.headDatasetConf = {   'HCMC_mean_of_Population Covered' : {label : "Average Population at HCMC"}, 
                                                                                    'HSCMC_mean_of_Population Covered' : {label : "Average Population at HSCMC"},
                                                                                    'VHC_mean_of_Population Covered' : {label : "Average Population at VHC"}
                                                                                }
                                        `,
    
    
        "nhp_committee_otg_amount": `       
                                            prepare_basic_chart(true);  
                                            head_operation = {"OTG Amount":"sum"}
                                            configuration_set = {group_heads:["ctype"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set);
                                        `,
    
    
        "nhp_total_committee_member": ` 
                                            prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["ctype"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set);

                                            configuration_set.headDatasetConf = {   HCMC_size_of_hash : {label : "Members at HCMC"}, 
                                                                                    HSCMC_size_of_hash : {label : "Members at HSCMC"},
                                                                                    VHC_size_of_hash : {label : "Members at VHC"}
                                                                                }

                                            `,
    
        "nhp_education_distribution": `     prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["Educational Qualification"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set);

                                            configuration_set.headDatasetConf = {   Graduate_size_of_hash : {label : "Graduate Members"}, 
                                                                                    'Not Educated_size_of_hash' : {label : "Not Educated Members"},
                                                                                    'PG or Higher_size_of_hash' : {label : "PG or Higher Members"},
                                                                                    'Up to 10th Std._size_of_hash' : {label : "Up to 10th Std. Members"},
                                                                                    'Up to 12th Std._size_of_hash' : {label : "Up to 12th Std. Members"},
                                                                                }


                                            `,
    
        "nhp_invalid_mobile": `             
                                            prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["ctype"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[{attr:"Mobile number", operator:"==", value:"Invalid"}], };
                                            draw_chart(configuration_set);

                                            configuration_set.headDatasetConf = {   HCMC_size_of_hash : {label : "Invalid Mobiles at HCMC"}, 
                                                                                    HSCMC_size_of_hash : {label : "Invalid Mobiles at HSCMC"},
                                                                                    VHC_size_of_hash : {label : "Invalid Mobiles at VHC"}
                                                                                }

                                            `,
    
        "sex_distribution": `               
                                            prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["Sex"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set);

                                            configuration_set.headDatasetConf = {   F_size_of_hash : {label : "Female Members"}, 
                                                                                    M_size_of_hash : {label : "Male Members"},
                                                                                }

                                            `,
    
        "nhp_age_distribution": `           
                                            prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["ctype"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                            draw_chart(configuration_set)

                                            configuration_set.headDatasetConf = {   HCMC_size_of_hash : {label : "Members at HCMC"}, 
                                                                                    HSCMC_size_of_hash : {label : "Members at HSCMC"},
                                                                                    VHC_size_of_hash : {label : "Members at VHC"}
                                                                                }

                                            `,
    
    
        "nhp_member_designation": `         
                                            prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["Designation"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set);
                                            
                                            configuration_set.headDatasetConf = {   ASHA_size_of_hash : {label : "ASHA"}, 
                                            
                                                                                }

                                            `,
    
    
        "rbf_completion": `                 prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["ctype"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set);
                                            `,
    
        "rbf_distribution": `               prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["ctype"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set);`,
    
        "rbf_project_amount": `             prepare_basic_chart(true);  
                                            head_operation = {"OTG Amount":"sum"}
                                            configuration_set = {group_heads:["ctype"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            draw_chart(configuration_set); 
                                            
                                            set_threshold_values({ id: 'hline1', mode: "vertical", scale_id: "x-axis-0", value: 4.75, label_text: "Late RBF" , color:"red" });
                                            `,
        
        "late_rbf": `                       prepare_basic_chart(true);  
                                            head_operation = {current_rbf:"sum", hash:"size"}

                                            heads = Object.keys(headers_with_type).filter(function(x){ return x.endsWith("_status") })
                                            data_types = Array(heads.length).fill("size")
                                            configuration_set = {group_heads:["ctype"], head: heads, data_type: data_types, filters:[] };
                                            //configuration_set = {group_heads:["ctype"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                            
                                            configuration_set.headDatasetConf = {   HCMC_sum_of_current_rbf : {label : "HCMC Cmpleted RBF", stack:1}, 
                                                                                    HCMC_size_of_hash : {label : "HCMC Ongoing RBF", stack:2},

                                                                                    HSCMC_sum_of_current_rbf : {label : "HSCMC Cmpleted RBF", stack:1}, 
                                                                                    HSCMC_size_of_hash : {label : "HSCMC Ongoing RBF", stack:2},

                                                                                    VHC_sum_of_current_rbf : {label : "VHC Cmpleted RBF", stack:1}, 
                                                                                    VHC_size_of_hash : {label : "VHC Ongoing RBF", stack:2},
                                                                                }
                                            draw_chart(configuration_set); 
                                            
                                            `,
    
        "rbf_activity_all": `               prepare_basic_chart(true);  
                                            head_operation = {"Activity Estimated funds required to conduct this activity":"sum"}
                                            configuration_set = {group_heads:["Activity Type"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            
                                            configuration_set.find_replace_label = {from: " Total of Activity Estimated funds required to conduct this activity", by:""}
                                            
                                            draw_chart(configuration_set);   
                                            `,
    
    
        "rbf_activity_ongoing": `           prepare_basic_chart(true);  
                                            head_operation = {"Activity Estimated funds required to conduct this activity":"sum"}
                                            configuration_set = {group_heads:["Activity Type"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[{attr:"rbf_state", operator:"==", value: "Ongoing"}], };
                                            configuration_set.find_replace_label = {from: " Total of Activity Estimated funds required to conduct this activity", by:""}

                                            draw_chart(configuration_set);  
                                            `,
    
    
        "rbf_activity_completed": `         prepare_basic_chart(true);  
                                            head_operation = {"Activity Estimated funds required to conduct this activity":"sum"}
                                            configuration_set = {group_heads:["Activity Type"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[{attr:"rbf_state", operator:"==", value: "Completed"}], };
                                            configuration_set.find_replace_label = {from: " Total of Activity Estimated funds required to conduct this activity", by:""}

                                            draw_chart(configuration_set);
                                            `,
    
    
        "all_activity_by_rbf": `            prepare_basic_chart(true);  
                                            head_operation = {"Activity Estimated funds required to conduct this activity":"sum"}
                                            configuration_set = {group_heads:["Activity Type"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            configuration_set.find_replace_label = {from: " Total of Activity Estimated funds required to conduct this activity", by:""}

                                            draw_chart(configuration_set);
                                            `,
    
    
        "ongoing_activity_by_rbf": `        prepare_basic_chart(true);  
                                            head_operation = {"Activity Estimated funds required to conduct this activity":"sum"}
                                            configuration_set = {group_heads:["Activity Type"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[{attr:"rbf_state", operator:"==", value: "Ongoing"}], };
                                            configuration_set.find_replace_label = {from: " Total of Activity Estimated funds required to conduct this activity", by:""}

                                            draw_chart(configuration_set);
                                            `,
    
    
        "completed_activity_by_rbf": `      prepare_basic_chart(true);  
                                            head_operation = {"Activity Estimated funds required to conduct this activity":"sum"}
                                            configuration_set = {group_heads:["Activity Type"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[{attr:"rbf_state", operator:"==", value: "Completed"}], };
                                            configuration_set.find_replace_label = {from: " Total of Activity Estimated funds required to conduct this activity", by:""}
                                            draw_chart(configuration_set);`,
    
    
        "all_activity_mean": `              prepare_basic_chart(true);  
                                            head_operation = {"Activity Estimated funds required to conduct this activity":"mean"}
                                            configuration_set = {group_heads:["Activity Type"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[], };
                                            configuration_set.find_replace_label = {from: " Average of Activity Estimated funds required to conduct this activity", by:""}
                                            draw_chart(configuration_set);
                                            `,
    
    
        "ongoing_activity_mean": `          prepare_basic_chart(true);  
                                            head_operation = {"Activity Estimated funds required to conduct this activity":"mean"}
                                            configuration_set = {group_heads:["Activity Type"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[{attr:"rbf_state", operator:"==", value: "Ongoing"}] };
                                            configuration_set.find_replace_label = {from: " Average of Activity Estimated funds required to conduct this activity", by:""}

                                            draw_chart(configuration_set);
                                            `,
    
    
        "completed_activity_mean": `        prepare_basic_chart(true);  
                                            head_operation = {"Activity Estimated funds required to conduct this activity":"mean"}
                                            configuration_set = {group_heads:["Activity Type"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[{attr:"rbf_state", operator:"==", value: "Completed"}] };
                                            configuration_set.find_replace_label = {from: " Average of Activity Estimated funds required to conduct this activity", by:""}

                                            draw_chart(configuration_set);
                                            `,
    
        "rbf_approve_vs_expense": `
                                            prepare_basic_chart(false);  
                                            head_operation = {"NHP Fund":"sum", "Approved Budget":"sum", "Six monthly Expenditure (Rs)":"sum"}
                                            configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                            
                                            configuration_set.headDatasetConf = {   "sum_of_NHP Fund" : {label : "Fund recived from NHP (₹)", stack:1}, 
                                                                                    
                                                                                    "sum_of_Approved Budget" : {label : "Approved Budget (₹)", stack:2},

                                                                                    "sum_of_Six monthly Expenditure (Rs)" : {label : "Expenditure (₹)", stack:3}
	
                                                                                }
                                            draw_chart(configuration_set);
                                            `,

        "rbf_approve_activity_based": `
                                            prepare_basic_chart(true);  
                                            head_operation = {"Approved Budget":"sum"}
                                            configuration_set = {group_heads:["Activity Category"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                            
                                            draw_chart(configuration_set);
                                            `,

        "rbf_expense_activity_based": `
                                            prepare_basic_chart(true);  
                                            head_operation = {"Six monthly Expenditure (Rs)":"sum"}
                                            configuration_set = {group_heads:["Activity Category"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                            draw_chart(configuration_set);
                                            `,




        "rbf_approve_vs_expense_activity_based": `
                                                prepare_basic_chart(false);  
                                                head_operation = {"Approved Budget":"sum", "Six monthly Expenditure (Rs)":"sum"}
                                                configuration_set = {group_heads:["ctype"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                                draw_chart(configuration_set);

                                                `,

        "rbf_totalfund_vs_expense_vs_balance": `
                                                prepare_basic_chart(false);  
                                                head_operation = {"total_fund_amount_parted":"sum", "Approved Budget":"sum", "Six monthly Expenditure (Rs)":"sum", "Balance in Total":"sum"}
                                                configuration_set = { head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                                
                                                configuration_set.headDatasetConf = {"sum_of_total_fund_amount_parted" : {label : "Total Fund (₹)", stack:1}, 
                                                                                    
                                                                                    "sum_of_Approved Budget" : {label : "Approved Budget (₹)", stack:2},

                                                                                    "sum_of_Six monthly Expenditure (Rs)" : {label : "Expenditure (₹)", stack:3},

                                                                                    "sum_of_Balance in Total" : {label : "Remaning Balance (₹)", stack:4},
	
                                                                                }
                                                draw_chart(configuration_set);

                                                `,
    
    
        "rbf_quarter_1_spent": `            prepare_basic_chart(true);  
                                            head_operation = {"Quarter 1 Expenditure":"sum"}
                                            configuration_set = {group_heads:["activity_type"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                            draw_chart(configuration_set);
                                `,
    
    
        "rbf_quarter_2_spent": `            prepare_basic_chart(true);  
                                            head_operation = {"Quarter 2 Expenditure":"sum"}
                                            configuration_set = {group_heads:["activity_type"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                            draw_chart(configuration_set);
                                `,
    
    
    
        "not_approve_six_month_expense": `  prepare_basic_chart(true);  
                                            head_operation = {"Six monthly Expenditure (Rs)":"sum"}
                                            configuration_set = {group_heads:["activity_type"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[{attr:"activity_type", operator:"==", value: "Not Approved"}] };
                                            draw_chart(configuration_set);
                                            `,

    
        "rbf_quarter_1_spent_not_approved": `prepare_basic_chart(true);  
                                            head_operation = {"Quarter 1 Expenditure":"sum"}
                                            configuration_set = {group_heads:["Activity Category"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[{attr:"activity_type", operator:"==", value: "Not Approved"}] };
                                            draw_chart(configuration_set);
                                            `,
    
    
    
        "rbf_quarter_2_spent_not_approved": `
                                            prepare_basic_chart(true);  
                                            head_operation = {"Quarter 2 Expenditure":"sum"}
                                            configuration_set = {group_heads:["Activity Category"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[{attr:"activity_type", operator:"==", value: "Not Approved"}] };
                                            draw_chart(configuration_set);
        
                                            `,



        'all_rbf_status'                    : `
                                            prepare_basic_chart(true);  
                                            head_operation = {"hash":"size"}
                                            configuration_set = {group_heads:["rbf_state"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                          
                                            configuration_set.find_replace_label = {from: " No. of nhp report", by:" RBF"}
                                            
                                            draw_chart(configuration_set);

                                            `,

        'indicator_summry'             :   `
                                            prepare_basic_chart(false);
                                            
                                            head_operation = {"target_met_percent":"mean"}
                                            
                                            configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[{attr:"invalid_entry", operator:"==", value: "Valid"}] };
                                            draw_chart(configuration_set);
                                            
                                            `,


        'all_indicator'             :   `
                                            prepare_basic_chart(false);


                                            let label_conf = {}
                                            if (frame_name.indexOf("VHC") == 0)
                                            {
                                                loop_size = 8

                                                label_conf =    {   
                                                                "mean_of_indicator_1": {label : "I1: Conducted 3 BCC"},
                                                                "mean_of_indicator_2": {label : "I2: Complete ASHA Kit"},
                                                                "mean_of_indicator_3": {label : "I3: Conducted monthly VHND"},
                                                                "mean_of_indicator_4": {label : "I4: Birth Registered"},
                                                                "mean_of_indicator_5": {label : "I5: MCP Card"},
                                                                "mean_of_indicator_6": {label : "I6: 4 ANC"},
                                                                "mean_of_indicator_7": {label : "I7: JSY Benefit"},
                                                                "mean_of_indicator_8": {label : "I8: Birth Weighed by ASHA"},
                                                                }
                                            }
                                            else if (frame_name.indexOf("HSCMC") == 0)
                                            {
                                                loop_size = 8

                                                label_conf = {
                                                                "mean_of_indicator_1": {label : "I1: Three BCC"},
                                                                "mean_of_indicator_2": {label : "I2: Medicines, Equipments & Sanitation"},
                                                                "mean_of_indicator_3": {label : "I3: VHND Conducted"},
                                                                "mean_of_indicator_4": {label : "I4: Birth Registered"},
                                                                "mean_of_indicator_5": {label : "I5: BP Checked"},
                                                                "mean_of_indicator_6": {label : "I6: Four ANC"},
                                                                "mean_of_indicator_7": {label : "I7: JSY Benefits"},
                                                                "mean_of_indicator_8": {label : "I8: Full immunization (9M-11M)"},
                                                                }
                                            }
                                            else if (frame_name.indexOf("HCMC") == 0)
                                            {
                                                loop_size = 5

                                                label_conf = {
                                                                "mean_of_indicator_1": {label : "I1: Medicines, Equipment & Sanitation"},
                                                                "mean_of_indicator_2": {label : "I2: HIV Test"},
                                                                "mean_of_indicator_3": {label : "I3: Four ANC"},
                                                                "mean_of_indicator_4": {label : "I4: JSY Benefits"},
                                                                "mean_of_indicator_5": {label : "I5: Weighed at birth"},
                                                            }
                                            }

                                            
                                            head_operation = {}
                                            for(i=1; i<=loop_size; i++)
                                            {
                                                head_operation["indicator_"+i] = "mean"
                                            }
                                            configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[{attr:"invalid_entry", operator:"==", value: "Valid"}] };
                                            draw_chart(configuration_set);
                                            console.log(label_conf)
                                            configuration_set.headDatasetConf = label_conf;
                                            
                                            `,
    }

    let stages = ["Action_Plan_status", "Fund_Status_status", "IPR_-_1_status", "DVR_-_1_status", "IPR_-_2_status", "DVR_-_2_status", "Six_Monthly_Expenditure_status"]
    jQuery.each(stages, function(idx, unit){
        chart_conrol[unit] = `
                                prepare_basic_chart(true);  
                                head_operation = {"hash":"size"}
                                configuration_set = {group_heads:["` + unit + `"], head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                            
                                configuration_set.find_replace_label = {from: " No. of nhp report", by:" RBF"}
                                
                                draw_chart(configuration_set);

                                `
    })

    DRAW_CHART_FUNCTIONS = chart_conrol[chart_for]

});



function order_chart(event, ui)
{
    jQuery("#chart_attribute_set_order li").each(function(idx, a){

        dataset = a.textContent.trim()
        is_ascending = a.firstChild.nextElementSibling.className.indexOf("asc") != -1 ? true: false;

        for (i = 0; i < SORTABLE_DATA[dataset].length; i++) 
        {   
            for (j = 0; j < SORTABLE_DATA[dataset].length; j++)
            {
                if(is_ascending ? (SORTABLE_DATA[dataset][i] < SORTABLE_DATA[dataset][j]) : (SORTABLE_DATA[dataset][i] > SORTABLE_DATA[dataset][j]))
                {
                    jQuery.each(SORTABLE_DATA, function(key, vals){
                        temp = SORTABLE_DATA[key][i];
                        SORTABLE_DATA[key][i] = SORTABLE_DATA[key][j];
                        SORTABLE_DATA[key][j] = temp;
                    })
                }
            }
        }

        myChart.labels = SORTABLE_DATA["labels"];
        jQuery.each(myChart.data.datasets, function(idx, dataset){
            myChart.data.datasets[idx].data = SORTABLE_DATA[dataset.label.trim()]
        })

        myChart.update()
    })
}
// =================================================================================================================================

// =============================== Start Core Chart Fucntions ===============================================

var menu = document.querySelector('.menu');

function showMenu(x, y){
    console.log(x,y)
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
    menu.classList.add('menu-show');
}

function hideMenu(){
    menu.classList.remove('menu-show');
}

function onContextMenu(e){
    // e.preventDefault();
    showMenu(e.pageX, e.pageY);
    document.addEventListener('mousedown', onMouseDown, false);
}

function onMouseDown(e){
    console.log(e)
    hideMenu();
    // eval(e.originalTarget.offsetParent.attributes.onclick.value)
    eval(e.target.offsetParent.attributes.onclick.value)
    document.removeEventListener('mousedown', onMouseDown);
}




var legendClick = Chart.defaults.global.legend.onClick;

function showlist_chart(xaxix, attribute)
{
    group_by_filter = {}
    jQuery.each(configuration_set.headDatasetConf, function(key, val){
        group_by_filter[val.label] = key.replace(/[_](size|sum|mean)_of_.*/g, "")
    })

    if (configuration_set.group_heads && attribute != "TOTAL")
    {
        let value = group_by_filter[attribute]
        if(value)
        {
            configuration_set.filters.push({attr:configuration_set.group_heads[0], operator:"=="  ,value:value})
            configuration_set.attribute_filter =  true;
        }
        else
        {
            console.warn(attribute)
        }
    }


    console.log("==================================")
    console.log(configuration_set.group_heads, attribute, group_by_filter)
    console.log("==================================")
    
    if (configuration_set.group_heads)
    {
        // attribute = attribute.replace(/[_](size|sum|mean)_of_.*/g, "");
    }
    
    // console.log(attribute)
    configuration_set.filters.push({attr:configuration_set.group_by[0], operator:"=="  ,value:xaxix})
    $data_table_parent.show();
    jQuery("#query_statement").text(getChartTitle())
    EXPORT_EXCEL_NAME = tagline + "(" +getChartTitle() +")";
    $chart_rendring_area.hide();
    let custom_filters = {filters:configuration_set.filters};
    let headers = []
    if(FRAME_TO_CHART_REPORT_COLUMN[frame_name] != undefined)
    {
        headers = Object.create(FRAME_TO_CHART_REPORT_COLUMN[frame_name])
        headers =  jQuery.merge(headers, configuration_set.head)
        headers =  jQuery.merge(headers, configuration_set.group_by)

        headers = Array.from(new Set(headers));
        headers.splice(headers.indexOf("hash"),1);

        console.warn(headers)

    }
    else
    {
        headers = Object.keys(headers_with_type);
    }
    
    
    prepare_data_table(jQuery("#record_table"), headers, custom_filters);

}


function hidelist_chart()
{
    $data_table_parent.hide();
    configuration_set.filters.pop();
    if(configuration_set.attribute_filter)
    {
        configuration_set.attribute_filter =  true;
        configuration_set.filters.pop()
    }
    $chart_rendring_area.show();
}


function back_chart()
{   
    // configuration_set.attribute 
    // configuration_set.group_by = [configuration_set.filters.pop().attr];
    configuration_set.group_by = [configuration_set.filters.pop().attr];

    jQuery("#drill_down_menu").removeClass("menu-item-disabled"); 
    if(configuration_set.filters.length == 0)
        $chart_back_button.hide();

    draw_chart(configuration_set);

}

function drilldown_chart(attribute)
{
    configuration_set.filters.push({attr:configuration_set.group_by[0], operator:"=="  ,value:attribute})
    let next_level = jQuery.inArray(configuration_set.group_by[0], chart_order) + 1;

    if(next_level == (chart_order.length-1))
    {
        jQuery("#drill_down_menu").addClass("menu-item-disabled"); 
    }  
    next_level = chart_order[next_level];
    configuration_set.group_by = [next_level]
    draw_chart(configuration_set);
    $chart_back_button.show();
}

function prepare_basic_chart(is_stack, plugin_label_conf=false )
{
    jQuery("#largeModalLabel").text(tagline);
    //Handle Stackig button
    if(is_stack)
    {
        jQuery("#stack_toggle").prop("checked", true);
    }
    else
    {
        jQuery("#stack_toggle").prop("checked", false);  
    }
    $chart_back_button.hide();
    is_dataset_adde = false;
    var barChartData = {
        labels: [],
        datasets: []
    };
    if(myChart)
    {
        myChart.destroy();
        console.log("Old Chart Destroyed");
    }
    var ctx = document.getElementById(modal_chart_id).getContext('2d');
    myChart = new Chart(ctx, {
        type: 'bar',
        data: barChartData,
        options: {

            onClick: (evt, item) => {
                if(! myChart.getElementAtEvent(evt).length)
                {
                    // console.log("There isn't any Data at this point");
                    // $menu.hide();
                    return 0;
                }

                onContextMenu(evt);

                let click_info = {}
                click_info.dataset = {}
                // $menu.empty();
                jQuery("#data_list_menu").empty();
                let xaxis = item[0]._chart.data.labels[item[0]._index];
                
                jQuery("#drill_down_menu").attr("onclick", "drilldown_chart('" + xaxis + "')");
                
                // $menu.append(`<li id="menu-item-drill-down" class="menu-item" onclick="drill_down(xaxis)"> Drill Down</li>`);

                jQuery.each(item, function (k1, v1) { 
                    click_info.xaxis = v1._chart.data.labels[v1._index];

                    let data_label = v1._chart.data.datasets[k1].label;
                    let data_value = v1._chart.data.datasets[k1].data[v1._index]
                    click_info.dataset[data_label] = data_value;
                    

                    jQuery("#data_list_menu").append(`  <li class="menu-item" onclick="showlist_chart('`+ xaxis +`', '`+ data_label +`')">
                                                            <button type="button" class="menu-btn">
                                                                <i class="fa fa-list-alt"></i>
                                                                <span class="menu-text">` + data_label + `</span>
                                                            </button>
                                                        </li>
                                                        `);

                    // $menu.append(`<li id="menu-item-drill-down" class="menu-item" onclick="show_list('` + data_label +`')">` + data_label +` List</li>`);

                })
                console.log(click_info);
                
                x = evt.offsetX === undefined ? evt.originalEvent.layerX : evt.offsetX;
                y = evt.offsetY === undefined ? evt.originalEvent.layerY : evt.offsetY;
                showMenu(x, y);
            },

            legend: {
                // on click of a legend
                onClick: function (evt, item) {
                    legendClick.call(this, evt, item);
                    populate_chart_legend(myChart.legend.legendItems);
                }
            },
            plugins: {
                datalabels: {
                    backgroundColor: function(context) {
                        return context.dataset.borderColor;
                    },
                    formatter: "",
                    borderRadius: 4,
                    color: 'white',
                    font: {
                        weight: 'bold'
                    },
                    display: false,
                    clamp : true,
                },

                // sort:
                // {
                    // enable: true,
                    // sortFunction: (a,b) => { console.log(a,"danish",b)/** implement your own sort function here **/}
                // },

                
            },
            annotation: {
                drawTime: 'afterDatasetsDraw',
                events: ['click', 'dblclick', 'mouseover', 'mouseout'],
			    dblClickSpeed: 350, // ms (default)
                annotations: [
                    
                ]
            },
            animation: {
                animateRotate: true,
                animateScale: true
              },
            title: {
                display: true,
                text: '',
                fontFamily : 'Segoe UI'
            },
            tooltips: {
                mode: 'index',
                // intersect: false,
                callbacks: {
                    // label: function(tooltipItem, data) {
                    //     var label = data.datasets[tooltipItem.datasetIndex].label || '';
                    //     if (label) {
                    //         label += ': ';
                    //     }
                    //     if( isNaN(tooltipItem.yLabel) )
                    //         label += 0;
                    //     else
                    //         label += tooltipItem.yLabel;
                    //     return label;
                    // }

                    label : function(tooltipItem, data) {
                        var label = data.datasets[tooltipItem.datasetIndex].label || '';
                        nStr = tooltipItem.value;
                        // nStr = parseFloat(tooltipItem.value).toFixed(2);
                        nStr += '';
                        x = nStr.split('.');
                        x1 = x[0];
                        // x2 = x.length > 1 ? '.' + x[1] : '';
                        x2 = x.length > 1 ? '.' + (x[1].length > 2 ? x[1].substring(0,2): x[1]) : '';
                        var rgx = /(\d+)(\d{3})/;
                        while (rgx.test(x1)) {
                            x1 = x1.replace(rgx, '$1' + ',' + '$2');
                        }
                        return label + " = " +x1 + x2;
                    }
                }
            },
            responsive: true,
            scales: {
                xAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: "",
                        fontSize: 14,
                        fontFamily : 'Segoe UI'
                    },
                    stacked: is_stack,
                    ticks: {
                        autoSkip : false,
                        callback: function(value, index, values) {
                            return value;
                        }
                    },
                }],
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: "",
                        fontSize: 14,
                        fontFamily : 'Segoe UI'
                    },
                    stacked: is_stack,
                    ticks: {
                        beginAtZero: true,
                        // max: 100
                    }
                }]
            }
        }
    });
}


function set_x_y_scale_label(x,y)
{
    try 
    {
        myChart.options.scales.xAxes[0].scaleLabel.labelString = x.replace(/_/g, ' ').toUpperCase();
        myChart.options.scales.yAxes[0].scaleLabel.labelString = y.replace(/_/g, ' ').toUpperCase();
    }
    catch(err)
    {

    }
}

function set_threshold_values(threshold_conf)
{
    console.log(threshold_conf)
    myChart.options.annotation.annotations.push(
        {
            drawTime: 'afterDraw',
            id: threshold_conf.id,
            type: "line",
            mode: threshold_conf.mode,
            scaleID: threshold_conf.scale_id,
            value: threshold_conf.value,
            borderColor: "black",
            borderWidth: 3,
            borderDash: [5, 5],
            // borderDashOffset: 5,
            label: {
              backgroundColor: threshold_conf.color, //"red",
              content: threshold_conf.label_text,
              enabled: true
            },
            onClick: function(e) {
              // The annotation is is bound to the `this` variable
              console.log("Annotation", e.type, this);
            }
        }
    
    )
    myChart.update()
}


// function set_threshold_values(threshold)
// {
//     myChart.options.annotation.annotations.push(
//         {
//             id: "hline",
//             type: "line",
//             mode: "horizontal",
//             scaleID: "y-axis-0",
//             // mode: "vertical",
//             // scaleID: "y-axis-0",
//             value: 2700,
//             // value: "Lucknow",
//             borderColor: "black",
//             borderWidth: 5,
//             label: {
//               backgroundColor: "red",
//               content: "Test Label",
//               enabled: true
//             },
//             onClick: function(e) {
//               // The annotation is is bound to the `this` variable
//               console.log("Annotation", e.type, this);
//             }
//         }
    
//     )

//     myChart.update()
// }


function drill_down()
{
    index = jQuery.inArray(activated_graph_x_axis , chart_order);
    new_x_axis = chart_order[index + 1];
    return new_x_axis;
}

var report_filter = "";
function report()
{
    index = jQuery.inArray(activated_graph_x_axis , chart_order);
    new_x_axis = chart_order[index + 1];
    var temp = JSON.parse(properties.filters)
    temp.push({attr:activated_graph_x_axis, operator:"==", value:X});
    // temp.push(activated_graph_x_axis+"|"+X);
    report_filter = temp;
    alert("danis")
    console.log(temp, properties.get_data_frame_function, "danish")
    prepare_data_table(temp, properties.get_data_frame_function);
    return 0;
}

function remove_filter()
{
    var temp = Object.create(report_filter);
    console.log(temp);
    temp.shift();
    console.log(temp);
    // prepare_data_table(temp);
    return 0;
}


function handle_show_all()
{
    remove_filter();
    jQuery("#show_all").remove();
}


function save_chart_images()
{
    jQuery("#intractive_chart").get(0).toBlob(function(blob) {
        saveAs(blob, tagline+".png");
    });
}


$chart_back_button.click(function(){
    $drillDownOption.show();
    if($chart_rendring_area.is(":hidden"))
    {
        $data_table_parent.hide();
        $chart_rendring_area.show();
        if(!chart_filters.length)
        {
            $chart_back_button.hide();
        }
        // stop fucntion to proceed further becuse this back is just from switching to chart mode from table mode
        return 0
    }
    index = jQuery.inArray(activated_graph_x_axis , chart_order);
    old_index = index - 1;
    new_x = chart_order[old_index];
    if(new_x)
    {
        condition_string.pop();
        chart_filters.pop();
        if(jQuery.isEmptyObject(stack_bar_head_conf))
        {
            activated_function(new_x, chart_filters);
        }
        else
        {
            activated_function(new_x, stack_bar_head_conf, chart_filters);
        }
        activated_graph_x_axis = new_x;
        myChart.options.title.text = ("ALL " + new_x + " where " + condition_string.join(" and ")).replace(/_|name/g, "").toUpperCase();

        if(old_index == 0)
            $chart_back_button.hide();
    }
});


jQuery('.menu-item').click(function(){
    fn_name = jQuery(this).attr('function');
    trigger_intractive_function(fn_name);
});


function trigger_intractive_function(fn_name)
{
    $menu.hide();
    new_x = eval(fn_name);
    if(new_x)
    {
        condition_string.push(activated_graph_x_axis + " = " + X);
        temp_str = { attr : activated_graph_x_axis, operator: "==" , value : X };
        chart_filters.push( (temp_str) );
        // chart_filters.push(activated_graph_x_axis + "==" + "'" + X + "'");
        if(jQuery.isEmptyObject(stack_bar_head_conf))
        {
            activated_function(new_x, chart_filters);
        }
        else
        {
            activated_function(new_x, stack_bar_head_conf, chart_filters);
        }
        activated_graph_x_axis = new_x;
        myChart.options.title.text = ("ALL " + new_x + " where " + condition_string.join(" and ")).replace(/_|name/g, "").toUpperCase();
        $chart_back_button.show();

        if(! eval(fn_name))
        {
            $drillDownOption.hide();
        }
    }
    else
    {
        console.log("No More Filters");
    }
}



function advance_function()
{
    // var canvas = document.getElementById(modal_chart_id);
    // canvas.addEventListener('click', handleContextMenu, false);
    // canvas.addEventListener('mousedown', handleMouseDown, false);


    // myChart.ctx.click(function(e){
    //     if(! myChart.getElementAtEvent(e).length)
    //     {
    //         console.log("There isn't any Data at this point");
    //         $menu.hide();
    //         return 0;
    //     }
    //     e.preventDefault();
    //     e.stopPropagation();
    //     console.log(e)
    //     x = e.offsetX === undefined ? e.originalEvent.layerX : e.offsetX;
    //     y = e.offsetY === undefined ? e.originalEvent.layerY : e.offsetY;
    //     $menu.css({left:x,top:y});
    //     $menu.show();
    //     return(false);
    // })

    // function handleContextMenu(e){
    //     if(! myChart.getElementAtEvent(e).length)
    //     {
    //         console.log("There isn't any Data at this point");
    //         $menu.hide();
    //         return 0;
    //     }
    //     e.preventDefault();
    //     e.stopPropagation();
    //     console.log(e)
    //     x = e.offsetX === undefined ? e.originalEvent.layerX : e.offsetX;
    //     y = e.offsetY === undefined ? e.originalEvent.layerY : e.offsetY;
    //     $menu.css({left:x,top:y});
    //     $menu.show();
    //     return(false);
    // }
    
    function handleMouseDown(evt){
        if(! myChart.getElementAtEvent(evt).length)
        {
            console.log("There isn't any Data at this point");
            $menu.hide();
            return 0;
        }
        // console.log(json.stringify() myChart.getElementAtEvent(evt));
        var activePoint = myChart.getElementAtEvent(evt)[0];
        var data = activePoint._chart.data;
        var datasetIndex = activePoint._datasetIndex;
        var label = data.labels[activePoint._index];
        var value = data.datasets[datasetIndex].data[activePoint._index];
        X = label;
        Y = value;

        // console.log( activePoint._model.datasetLabel );
        // Enbale only one click drill down
        if(evt.which == 1)
        {
            // trigger_intractive_function("drill_down()");
        }
        $menu.hide();
    }
}




function hexToRgbA(hex){
    var c;
    if(/^#([A-Fa-f0-9]{3}){1,2}$/.test(hex)){
        c= hex.substring(1).split('');
        if(c.length== 3){
            c= [c[0], c[0], c[1], c[1], c[2], c[2]];
        }
        c= '0x'+c.join('');
        return 'rgb('+[(c>>16)&255, (c>>8)&255, c&255].join(',')+')';
        // return 'rgba('+[(c>>16)&255, (c>>8)&255, c&255].join(',')+',0.5)';
    }
    throw new Error('Bad Hex');
}



function generateDataSet(dataSetConf)
{
    if(dataSetConf.borderColor == undefined)
    {
        clr = hexToRgbA(ChartColor.pop());
    }
    else
    {
        clr = dataSetConf.borderColor;
    }
    
    
    return jQuery.extend({
        label: dataSetConf.label,
        type: "",
        backgroundColor: Color(clr).alpha(0.2).rgbString(),
        borderColor: clr,
        borderWidth: 1,
        pointHoverRadius: 15,
        pointHoverBackgroundColor: 'yellow',
        // stack : 'stack 0', 
        data: [],
    },dataSetConf);

}

function add_data(chart_data)
{
    console.log(chart_data);

    myChart.data.labels = chart_data.labels

    jQuery.each(chart_data.dataset, function(dataset_name, data){
        myChart.data.datasets.push()
        // console.log(dataset_name, "==>", data)
    })


}






// function add_data(labels, records)
function old_add_data(c_data)
{   
    // console.log(c_data, "danish")
    labels      = c_data.labels;
    records     = c_data.dataset;
    myChart.data.labels = labels;
    var set = 0;
    var chart_type = "";
    if(Array.isArray(records))
    {
        if(! is_dataset_adde)
            jQuery.each(labels, function(idx, label){
                // console.log(label);
                addDataSet(label, {chart_type: chart_type});
            })
        // Adding Data from that dataset
        myChart.data.datasets[set].data = (records);


        var use_border_color_set = []//Object.values(window.chartColors).splice(0,records.length);
        var use_background_color_set = [];
        // jQuery.each(use_border_color_set, function(idx, clr){
        //     use_background_color_set.push(Color(clr).alpha(0.5).rgbString())
        // })
        jQuery.each(records, function(){
            clr = dynamicColors();
            use_border_color_set.push(clr);
            use_background_color_set.push(Color(clr).alpha(0.5).rgbString())
        })
        myChart.data.datasets[set].borderColor = use_border_color_set;
        myChart.data.datasets[set].backgroundColor = use_background_color_set;
    }
    else
    {   
        console.log(records, "888888888")
        jQuery.each(records, function(label, dataset){
            if(! Array.isArray(dataset))
            {
                chart_type = dataset.chart_type
                dataset = dataset.data;
                // console.log(chart_type);
            }
            //Adding Dataset to Chart
            if(! is_dataset_adde)
                addDataSet(label.toUpperCase(), {chart_type: chart_type});
            // Adding Data from that dataset
            myChart.data.datasets[set].data = (dataset);
            // increse dataset count
            set++;
        })
    }
    is_dataset_adde = true;
    myChart.update();

    populate_chart_legend(myChart.legend.legendItems);
}

//Add dataset attribute to charts
// function addDataSet(label, chart_type)
function addDataSet(label, data_set_conf)
{
    var colorNames = Object.keys(window.chartColors);
    var colorName = colorNames[myChart.data.datasets.length % colorNames.length];
    var dsColor = window.chartColors[colorName];

    var x = Math.floor((Math.random() * 10) + 1);

    var newDataset = {
        label: label,
        type: data_set_conf.chart_type,
        backgroundColor: Color(dsColor).alpha(0.2).rgbString(),
        borderColor: dsColor,
        borderWidth: 1,
        pointHoverRadius: 15,
        pointHoverBackgroundColor: 'yellow',
        // stack : 'stack 0', 
        data: [],

    };

    if (data_set_conf.stack_level)
    {
        newDataset.stack = data_set_conf.stack_level
    }

    myChart.data.datasets.push(newDataset);
}


function remove_data()
{
    myChart.data.labels.splice(-1, 1); // remove the label first
    myChart.data.datasets.forEach(function(dataset) {
        dataset.data.pop();
    });
    myChart.update();
}

// ========================================================================================================
// ========================================================================================================
// ========================================================================================================
// ========================================================================================================
// ========================================================================================================
// =============================== End Core Chart Fucntions ===============================================
// ========================================================================================================
// ========================================================================================================
// ========================================================================================================
// ========================================================================================================
// ========================================================================================================
// ========================================================================================================
// ========================================================================================================
// ========================================================================================================
// ========================================================================================================
// ========================================================================================================




// ================================== Start Worker Count Distribution Functions ================================

function sanitize_worker_count_chart_data(data, x_axis_attr)
{
    // console.log(data)
    set_x_y_scale_label(x_axis_attr, "number_of_"+frame_name);
    number_of_worker = Object.values(data["size_of_"+x_axis_attr]);
    label = Object.values(data[x_axis_attr]);
    dataset = {};
    dataset["number_of_"+frame_name] = {data:number_of_worker, chart_type:"line"};
    data = {"labels" : label, "dataset": dataset };
    return data;

}


function render_worker_count_distribution(x_axis_attr, filters=[])
{
    properties = { group_by: [x_axis_attr], head: [x_axis_attr], data_type: ["size"], filters:JSON.stringify(filters) };
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_worker_count_chart_data(data, x_axis_attr);
        add_data(chart_data);
    });
}



function sanitize_worker_mean_chart_data(data, x_axis_attr)
{
    // console.log(data)
    set_x_y_scale_label(x_axis_attr, "number_of_"+frame_name);
    number_of_worker = Object.values(data["mean_of_Population Covered"]);
    label = Object.values(data[x_axis_attr]);
    dataset = {};
    dataset["number_of_"+frame_name] = {data:number_of_worker, chart_type:"line"};
    data = {"labels" : label, "dataset": dataset };
    return data;

}




function render_worker_mean_distribution(x_axis_attr, filters=[])
{
    properties = { group_by: [x_axis_attr], head: ["Population Covered"], data_type: ["mean"], filters:JSON.stringify(filters) };
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_worker_mean_chart_data(data, x_axis_attr);
        add_data(chart_data);
    });
}







function sanitize_render_sum_distribution(data, x_axis_attr)
{
    // console.log(data)
    set_x_y_scale_label(x_axis_attr, "number_of_"+frame_name);
    number_of_worker = Object.values(data["sum_of_OTG Amount"]);
    label = Object.values(data[x_axis_attr]);
    dataset = {};
    dataset["number_of_"+frame_name] = {data:number_of_worker, chart_type:"line"};
    data = {"labels" : label, "dataset": dataset };
    return data;

}




function render_sum_distribution(x_axis_attr, filters=[])
{
    special_column_of_list = ["OTG Amount"]
    properties = { group_by: [x_axis_attr], head: ["OTG Amount"], data_type: ["sum"], filters:JSON.stringify(filters) };
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_render_sum_distribution(data, x_axis_attr);
        add_data(chart_data);
    });
}



// ================================== End Worker Count Distribution Functions ================================




// ================================== Start Caste Distribution Functions ================================
function sanitize_caste_distribution_chart_data(chart_data, x_axis_attr)
{
    set_x_y_scale_label(x_axis_attr, "number_of_"+frame_name);
    var gen_data_set = [];
    var sc_data_set = [];
    var st_data_set = [];
    var obc_data_set = [];
    var na_data_set = [];
    var master_record = {};
    jQuery.each(chart_data[x_axis_attr] , function(idx, one_x_axis_attr){
        var record = {};
        if(one_x_axis_attr in master_record)
        {
            master_record[one_x_axis_attr][chart_data.caste[idx]] =chart_data.size_of_caste[idx];
        }
        else
        {
            record[chart_data.caste[idx]] = chart_data.size_of_caste[idx];
            master_record[one_x_axis_attr] = record;
        }
    })

    label = Object.keys(master_record);

    jQuery.each(master_record, function(one_x_axis_attr, dataset){
        // Iterate for fix 4 castes
        castes_set = ["Gen", "SC", "ST", "OBC", "N/A"];
        // console.log(dataset);
        jQuery.each(castes_set, function(idx, caste) {  
            if(caste in dataset)
            {
                push_caste_data(caste, dataset[caste]);
            }
            else
            {
                push_caste_data(caste, null);
            }

        })
    })
    //Fucntion for pushing data in caste stack 
    function push_caste_data(caste, val)
    {
        // console.log(caste, val);
        switch (caste) { 
            case "Gen": 
                gen_data_set.push(val);
                break;
            case "SC": 
                sc_data_set.push(val);
                break;
            case "ST": 
                st_data_set.push(val);	
                break;
            case "OBC": 
                obc_data_set.push(val);
                break;
            default :
                na_data_set.push(val)
        }
    
    }
    console.log(na_data_set);

    chart_data = {"labels" : label, "dataset": { "gen" :gen_data_set, "obc":obc_data_set, "sc":sc_data_set, "st":st_data_set, "n/a":na_data_set } };

    return chart_data;

}


function render_caste_distribution(x_axis_attr, filters=[]){
    special_column_of_list = ["caste"]
    properties = { group_by: [special_column_of_list[0], x_axis_attr], head: ["caste"], data_type: ["size"], sort_by:x_axis_attr, filters:JSON.stringify(filters) };
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_caste_distribution_chart_data(data, x_axis_attr);
        add_data(chart_data);
    });
}


// ================================== End Caste Distribution Functions ================================



// ================================== Start Asha required vs Availbale Functions ================================

function sanitize_required_vs_available_worker_chart_data(data, x_axis_attr)
{
    set_x_y_scale_label(x_axis_attr, "number_of_"+frame_name);
    population_set = Object.values(data.sum_of_population);
    var required_number_of_worker = [];
    jQuery.each(population_set, function(idx, one_data){    
        required_number_of_worker.push( Math.round(one_data/1000));
    })
    // total_worker = Object.values(data[frame_name+"_id_count_by_"+x_axis_attr]);
    total_worker = Object.values(data["size_of_"+frame_name+"_id"]);
    label = Object.values(data[x_axis_attr]);
    // console.log(frame_name);
    dataset = {};
    dataset["total_"+frame_name] = {data : total_worker, chart_type:"line"}
    dataset["required_number_of_"+frame_name] = {data: required_number_of_worker, chart_type:"line"}
    data = {"labels" : label, dataset : dataset };
    return data;

}


function render_required_vs_available_worker_distribution(x_axis_attr, filters=[])
{
    properties = { group_by: [x_axis_attr], head: ["population", frame_name+"_id"], data_type: ["sum", "size"], "filters":JSON.stringify(filters) };
    // properties = { counts_of_attr_n_by:[frame_name+"_id|"+x_axis_attr], sort_by: x_axis_attr, head: ["population"], group_by:[x_axis_attr], data_type: ["sum"], filters:JSON.stringify(filters) };
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_required_vs_available_worker_chart_data(data, x_axis_attr);
        add_data(chart_data);
    });
}



// ================================== End Asha required vs Availbale Functions ================================




// ================================== Start Educational Distribution  ================================

function sanitize_education_distribution_chart_data(chart_data, x_axis_attr)
{
    set_x_y_scale_label(x_axis_attr, "number_of_"+frame_name);
    var hs_data_set = [];
    var im_data_set = [];
    var gr_data_set = [];
    var pg_data_set = [];
    var master_record = {};
    jQuery.each(chart_data[x_axis_attr] , function(idx, one_x_axis_attr){
        var record = {};
        if(one_x_axis_attr in master_record)
        {
            master_record[one_x_axis_attr][chart_data.educational_qualification[idx]] =chart_data.size_of_educational_qualification[idx];
        }
        else
        {
            record[chart_data.educational_qualification[idx]] = chart_data.size_of_educational_qualification[idx];
            master_record[one_x_axis_attr] = record;
        }
    })

    // console.log(master_record);
    label = Object.keys(master_record);

    jQuery.each(master_record, function(one_x_axis_attr, dataset){

        education_set = ["High School", "Intermediate", "Graduate", "Post Graduate"];
        // console.log(dataset);
        jQuery.each(education_set, function(idx, education) {  
            if(education in dataset)
            {
                push_education_data(education, dataset[education]);
            }
            else
            {
                push_education_data(education, null);
            }

        })
    })
    //Fucntion for pushing data in caste stack 
    function push_education_data(educational_qualification, val)
    {
        switch (educational_qualification) { 
            case "High School": 
                hs_data_set.push(val);
                break;
            case "Intermediate": 
                im_data_set.push(val);
                break;
            case "Graduate": 
                gr_data_set.push(val);	
                break;
            case "Post Graduate": 
                pg_data_set.push(val);
                break;
            default:
                // console.log("val", "====cc=====");
        }
    
    }

    chart_data = {"labels" : label, "dataset": { "post_graduate":pg_data_set, "graduate":gr_data_set, "intermediate":im_data_set, "high_school" :{"chart_type":"bar", "data":hs_data_set}} };

    return chart_data;


}


function render_education_distribution(x_axis_attr, filters=[])
{
    special_column_of_list = ["educational_qualification"]
    properties = { group_by: [special_column_of_list[0], x_axis_attr], head: ["educational_qualification"], sort_by:x_axis_attr, data_type: ["size"] , filters:JSON.stringify(filters)};
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_education_distribution_chart_data(data, x_axis_attr);
        add_data(chart_data);
    });
}

// ================================== End Educational Distribution  ================================



// ================================== Start Population per Worker Functions ================================

function sanitize_population_per_worker_chart_data(data, x_axis_attr)
{
    set_x_y_scale_label(x_axis_attr, "Population");
    population_set = Object.values(data.sum_of_population);
    var population_per_worker = [];
    total_worker = Object.values(data["size_of_"+frame_name+"_id"]);

    jQuery.each(population_set, function(idx, one_data){    
        population_per_worker.push( Math.round(one_data/total_worker[idx]));
    })

    label = Object.values(data[x_axis_attr]);

    dataset = {};
    dataset["population_per_"+frame_name]   = {"chart_type":"line", "data":population_per_worker};
    dataset["standard"]                     = {"chart_type":"line", "data":Array(population_per_worker.length).fill(1000)};
    dataset["maximum_allowed"]              = {"chart_type":"line", "data":Array(population_per_worker.length).fill(1500)};
    data = {"labels" : label, dataset : dataset };
    return data;

}



function render_population_per_worker_distribution(x_axis_attr, filters=[])
{
    special_column_of_list = ["population"]
    properties = { group_by: [x_axis_attr], head: ["population", frame_name+"_id"], data_type: ["sum", "size"], "filters":JSON.stringify(filters)};
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_population_per_worker_chart_data(data, x_axis_attr);
        add_data(chart_data);
    });
}



// ================================== End Population per Worker Functions ================================






// ================================== Start Active Mobile of Worker Functions ================================

function sanitize_active_mobile_chart_data(data, x_axis_attr)
{
    set_x_y_scale_label(x_axis_attr, "number_of_"+frame_name);
    if ("size_of_mobile_status" in data)
    {
        mobile_set = Object.values(data.size_of_mobile_status);
        label = Object.values(data.mobile_status);
        data = {"labels" : label, "dataset":  mobile_set };
        // myChart.options = {};

        myChart.options = {
            
            title: {
                display: true,
                text: 'ALL DISTRICT'
            }
        };
        return data;
    }
    else
    {
        number_of_worker = Object.values(data["size_of_"+x_axis_attr]);
        label = Object.values(data[x_axis_attr]);
        data = {"labels" : label, "dataset": {"Invalid Number" :number_of_worker} };
        return data;

    }

}

function render_active_mobile_distribution(x_axis_attr, filters=[])
{
    properties = { group_by: [x_axis_attr], head: [x_axis_attr], data_type: ["size"], filters:JSON.stringify(filters)};
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        // console.log(data);
        chart_data = sanitize_active_mobile_chart_data(data, x_axis_attr);
        add_data(chart_data);
    });
}



// ================================== End Active Mobile of Worker Functions ================================








// ================================== Start Worker Enrollment Functions ================================

function sanitize_worker_enrollment_chart_data(data, x_axis_attr)
{
    set_x_y_scale_label(x_axis_attr, "number_of_"+frame_name);
    label = Object.values(data[x_axis_attr]);
    number_of_worker_set = Object.values(data["size_of_"+x_axis_attr]);
    dataset = {};
    dataset["number_of_"+frame_name] = {"data":number_of_worker_set, chart_type:"line"};
    data = {"labels" : label, "dataset": dataset};
    return data;
}


function render_worker_enrollment_distribution(x_axis_attr, filters=[])
{
    special_column_of_list = ["working_since"]
    properties = { sort_by:x_axis_attr, group_by:[x_axis_attr], head: [x_axis_attr], data_type: ["size"], filters:JSON.stringify(filters) };
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_worker_enrollment_chart_data(data, x_axis_attr);
        add_data(chart_data);
    });
}






// ================================== End Worker Enrollment Functions ================================














// ================================== Start Age Distribution of Worker Functions ================================

function sanitize_age_distribution_main_chart_data(chart_data, x_axis_attr)
{
    special_column_of_list = ["age"]
    set_x_y_scale_label(x_axis_attr, "number_of_"+frame_name);
    labels = Object.values(chart_data[x_axis_attr]);
    data = Object.values(chart_data["size_of_"+x_axis_attr]);
    dataset = {};
    dataset["number_of_"+frame_name] = data
    return({labels:labels, dataset: dataset})

}

function render_age_distribution(x_axis_attr, filters=[])
{
    properties = { sort_by:x_axis_attr, group_by:[x_axis_attr], head: [x_axis_attr], data_type: ["size"], filters:JSON.stringify(filters) };
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_age_distribution_main_chart_data(data, x_axis_attr);
        add_data(chart_data);
    });
}



// ================================== End Age Distribution of Worker Functions ================================




// ================================== Start Categorize Population per Worker Functions ================================

function sanitize_categorize_population_per_worker_chart_data(data, x_axis_attr)
{
    set_x_y_scale_label(x_axis_attr, "number_of_"+frame_name);
    label = Object.values(data[x_axis_attr]);
    data = Object.values(data["size_of_"+x_axis_attr]);
    special_column_of_list = ["population"]
    dataset = {};
    dataset["number_of_"+frame_name]   = {"chart_type":"line", "data":data};
    data = {"labels" : label, dataset : dataset };
    return data;

}


function render_categorize_population_per_worker_distribution(x_axis_attr, filters=[])
{
    properties = {head: [x_axis_attr, "asha_id"], group_by:[x_axis_attr], data_type: ["size", "size"], filters:JSON.stringify(filters) };
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_categorize_population_per_worker_chart_data(data, x_axis_attr);
        add_data(chart_data);
    });
}



// ================================== End Categorize Population per Worker Functions ================================





// ================================== Start Asha per Sangini Functions ================================

function sanitize_render_asha_per_sangini_chart_data(data, x_axis_attr)
{
    set_x_y_scale_label(x_axis_attr, "number_of_"+frame_name);
    label = Object.values(data[x_axis_attr]);
    data = Object.values(data["size_of_"+x_axis_attr]);
    special_column_of_list = ["mapped_asha"];
    dataset = {};
    dataset["number_of_"+frame_name]   = {"chart_type":"line", "data":data};
    data = {"labels" : label, dataset : dataset };
    return data;

}


function render_asha_per_sangini(x_axis_attr, filters=[])
{
    properties = { sort_by:x_axis_attr, head: [x_axis_attr], group_by:[x_axis_attr], data_type: ["size"], filters:JSON.stringify(filters) };
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_render_asha_per_sangini_chart_data(data, x_axis_attr);
        add_data(chart_data);
    });
}



// ================================== End Asha per Sangini Functions  ================================




// ================================== Start Permanent vs Contractual ANM Functions ================================

function sanitize_permanent_vs_contractual_anm_chart_data(chart_data, x_axis_attr)
{
    set_x_y_scale_label(x_axis_attr, "number_of_"+frame_name);
    var na_data_set = [];
    var cont_data_set = [];
    var perm_data_set = [];

    var master_record = {};
    jQuery.each(chart_data[x_axis_attr] , function(idx, one_x_axis_attr){
        var record = {};
        if(one_x_axis_attr in master_record)
        {
            master_record[one_x_axis_attr][chart_data.job_type[idx]] =chart_data.size_of_job_type[idx];
        }
        else
        {
            record[chart_data.job_type[idx]] = chart_data.size_of_job_type[idx];
            master_record[one_x_axis_attr] = record;
        }
    })

    label = Object.keys(master_record);

    jQuery.each(master_record, function(one_x_axis_attr, dataset){
        // Iterate for fix 4 job_types
        job_types_set = ["Permanent", "Contractual", "N/A"];
        // console.log(dataset);
        jQuery.each(job_types_set, function(idx, job_type) {  
            if(job_type in dataset)
            {
                push_job_type(job_type, dataset[job_type]);
            }
            else
            {
                push_job_type(job_type, null);
            }

        })
    })
    //Fucntion for pushing data in job_type stack 
    function push_job_type(job_type, val)
    {
        console.log(job_type, val);
        switch (job_type) { 
            case "Permanent": 
                perm_data_set.push(val);
                break;
            case "Contractual": 
                cont_data_set.push(val);
                break;
            case "N/A": 
                na_data_set.push(val);	
                break;
        }
    
    }
    chart_data = {"labels" : label, "dataset": { "na":na_data_set, "Permanent":perm_data_set, "Contractual" :cont_data_set} };

    return chart_data;

}

function render_permanent_vs_contractual_anm(x_axis_attr, filters=[])
{
    special_column_of_list = ["job_type"]
    properties = { group_by: [special_column_of_list[0], x_axis_attr], head: special_column_of_list, data_type: ["size"], sort_by:x_axis_attr, filters:JSON.stringify(filters) };
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        // console.log(data);
        chart_data = sanitize_permanent_vs_contractual_anm_chart_data(data, x_axis_attr);
        add_data(chart_data);
    });
}



// ================================== End Permanent vs Contractual ANM Functions ================================


// ================================== Start Current Month ASHA Payment Functions ================================

function sanitize_render_head_wise_current_payment_chart_data(data, x_axis_attr)
{
    set_x_y_scale_label(x_axis_attr, "Total Amount");
    label = Object.values(data[x_axis_attr]);
    delete data[x_axis_attr]

    dataset = {};
    jQuery.each(data, function(idx, val){
        temp_label = idx.replace('sum_of_', "")
        dataset[temp_label] =  Object.values(val);
    })
    if(worker === "asha")
    {
        special_column_of_list = ['aaa_total','addpay_total', 'child_total', 'encep_total', 'family_total', 'hrp_total', 'immu_total', 'jsy_total', 'kalajaar_total', 'leprosy_total', 'lymp_total', 'malaria_total', 'mdr_total', 'niddcp_total', 'rksk_total', 'rntcp_total', 'subtotal']
    }
    else if(worker === "sangini")
    {
        special_column_of_list = ["refilling_of_drug_kit", "monitoring_of_asha_payment", "mother/child_death_registration" , "asha_visits", "cluster_meeting", 'subtotal']
    }
    data = {"labels" : label, dataset : dataset };
    return data;

}


function render_head_wise_current_payment(x_axis_attr, filters=[])
{
    if(worker === "asha")
    {
        special_column_of_list = Object.keys(headers_with_type).filter(function(x){ return x.endsWith("_total") })
        // special_column_of_list = ['aaa_total','addpay_total', 'child_total', 'encep_total', 'family_total', 'hrp_total', 'immu_total', 'jsy_total', 'kalajaar_total', 'leprosy_total', 'lymp_total', 'malaria_total', 'mdr_total', 'niddcp_total', 'rksk_total', 'rntcp_total']
    }
    else if(worker === "sangini")
    {
        special_column_of_list = ["refilling_of_drug_kit", "monitoring_of_asha_payment", "mother/child_death_registration" , "asha_visits", "cluster_meeting"]
    }
    data_type = Array(special_column_of_list.length).fill("sum")
    properties = { group_by: [x_axis_attr], head: special_column_of_list, data_type: data_type, sort_by:x_axis_attr, filters:JSON.stringify(filters) };
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_render_head_wise_current_payment_chart_data(data, x_axis_attr);
        // add_data(chart_data.labels, chart_data.dataset);
        add_data(chart_data);
    });
}


// ================================== End Current Month ASHA Payment Functions ================================



// ================================== Start Current Month ASHA Payment Functions ================================

function sanitize_render_current_month_payment_chart_data(data, x_axis_attr)
{
    set_x_y_scale_label(x_axis_attr, "Total Amount");
    label = Object.values(data[x_axis_attr]);
    delete data[x_axis_attr]
    dataset = {};
    dataset["claimed_amount"] = {data:Object.values(data["sum_of_subtotal"]), chart_type:"line"}; 
    data = {"labels" : label, dataset : dataset };
    return data;

}


function render_current_month_payment(x_axis_attr, filters=[])
{
    special_column_of_list = ['subtotal']
    properties = {group_by: [x_axis_attr], head: ["subtotal"], data_type: ["sum"], filters:JSON.stringify(filters)};
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_render_current_month_payment_chart_data(data, x_axis_attr);
        add_data(chart_data);
    });
}


// ================================== End Current Month ASHA Payment Functions ================================


// ================================== Start Avg Current Month ASHA Payment Functions ================================

function sanitize_render_avg_current_month_payment_chart_data(data, x_axis_attr)
{
    set_x_y_scale_label(x_axis_attr, "Amount / Count");
    label = Object.values(data[x_axis_attr]);
    delete data[x_axis_attr];
    // subtotal = Object.values(data.sum_of_subtotal);
    // worker_count = Object.values(data["nunique_of_" + worker + "_id"]);
    // data["avg_amount"] = []
    // jQuery.each(worker_count, function(idx, val){
    //     data["avg_amount"].push(Math.ceil(subtotal[idx]/val))
    // })
    // delete data.sum_of_subtotal;

    data["avg_amount"] =  Object.values(data.mean_of_subtotal);
    dataset = {};

    dataset["number_of_asha"] = {data : Object.values(data["nunique_of_" + worker +"_id"]) , chart_type:"line"} ;

    if(worker === "asha")
        standard_amount = 4500;
    else if(worker === "sangini")
        standard_amount = 6250;
    dataset["standard_amount"] = {data : Array(label.length).fill(standard_amount) , chart_type:"line"} ;
    dataset["avg_amount"] = {data : Object.values(data["avg_amount"]) , chart_type:"line"} ;
    data = {"labels" : label, dataset : dataset };
    return data;

}


function render_avg_current_month_payment(x_axis_attr, filters=[])
{
    special_column_of_list = ["subtotal"]
    properties = {group_by: [x_axis_attr], head: ["subtotal", worker + "_id"], data_type: ["mean", "nunique"], filters:JSON.stringify(filters)};
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_render_avg_current_month_payment_chart_data(data, x_axis_attr);
        add_data(chart_data);
    });
}


// ================================== End Avg Current Month ASHA Payment Functions ================================





// ================================== Start Avg Current Month ASHA Payment Functions ================================

function sanitize_render_amount_distribution_in_worker_chart_data(data, x_axis_attr)
{
    set_x_y_scale_label(x_axis_attr, "Number of "+worker);
    label = Object.values(data[x_axis_attr]);
    worker_count = Object.values(data["size_of_" + worker +"_id"]);
    
    // Logic to prevent lexicographically sort
    if(  label[0].indexOf("-") != -1)
    {
        var sortor = {}
        jQuery.each(label, function(idx, val){
            sortor[ parseInt(val.split("-")[0].replace(",", "")) ] = idx
        })
        sortor = Object.values(sortor)
        sort_label = []
        sort_worker_count = []
        jQuery.each(sortor, function(idx, val){
            sort_label.push(label[val])
            sort_worker_count.push(worker_count[val])
        })
        label = sort_label;
        worker_count = sort_worker_count;
    }
    
    dataset = {};
    dataset["number_of_"+worker] = {data : worker_count, chart_type:"line"} ;
    data = {"labels" : label, dataset : dataset };

    return data;

}


function render_amount_distribution_in_worker(x_axis_attr, filters=[])
{
    special_column_of_list = ["subtotal"]
    properties = {group_by: [x_axis_attr], head: [worker + "_id"], data_type: ["size"], sort_by:x_axis_attr, filters:JSON.stringify(filters)};
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_render_amount_distribution_in_worker_chart_data(data, x_axis_attr);
        add_data(chart_data);
    });
}


// ================================== End Avg Current Month ASHA Payment Functions ================================



// ================================== Start Current Month ASHA not paid Functions ================================

function sanitize_render_current_month_not_paid_chart_data(data, x_axis_attr)
{
    set_x_y_scale_label(x_axis_attr, "Number of "+ worker);
    label = Object.values(data[x_axis_attr]);
    delete data[x_axis_attr]
    dataset = {};
    dataset["no_of_" + worker] = Object.values(data["size_of_"+ worker + "_id"]); 
    data = {"labels" : label, dataset : dataset };
    return data;

}


function render_current_month_not_paid(x_axis_attr, filters=[])
{
    properties = {group_by: [x_axis_attr], head: [worker + "_id"], data_type: ["size"],  get_data_frame_function : worker + "_not_paid_frame", filters:JSON.stringify(filters) };
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_render_current_month_not_paid_chart_data(data, x_axis_attr);
        add_data(chart_data);
    });
}


// ================================== End Current Month ASHA not paid Functions ================================







// ================================== Start Head payment distribution Functions ================================

function sanitize_head_payment_ditribution_chart_data(data, x_axis_attr)
{
    console.log(data)
    set_x_y_scale_label(x_axis_attr, "Total Amount");
    delete data[x_axis_attr]

    label = [];
    dataset = {};

    new_data = []
    jQuery.each(data, function(idx, val){
        // console.log(val);
        temp_label = idx.replace('sum_of_', "");
        label.push(temp_label.toUpperCase());
        new_data.push(val[0]);
    })
    data = {"labels" : label, dataset : {"Amount" : new_data}  };
    console.log(data);
    return data;
}


// function render_current_month_not_paid(x_axis_attr, filters=[])
// {
//     properties = {group_by: [x_axis_attr], head: ["asha_id"], data_type: ["size"],  get_data_frame_function : "asha_not_paid_frame()", filters:JSON.stringify(filters) };
//     jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
//         chart_data = sanitize_head_payment_ditribution_chart_data(data, x_axis_attr);
//         add_data(chart_data);
//     });
// }


// ================================== End Head payment distribution Functions ================================








// ================================== Start Current Month BCPM Status Functions ================================

function sanitize_render_current_month_payment_status_chart_data(data, x_axis_attr)
{
    console.log(data)
    set_x_y_scale_label(x_axis_attr, "Number of BCPM");
    label = Object.values(data[x_axis_attr]);
    delete data[x_axis_attr]

    size_attr = Object.keys(data)[0];
    console.log(size_attr);
    dataset = {};
    dataset["Compleed"] = {data:Object.values(data[size_attr]), chart_type:"line"};
    data = {"labels" : label, dataset : dataset };
    console.log(data);
    return data;
}



function sanitize_render_stack_bar_chart_data(chart_data, x_axis_attr, uniq_attr)
{
    console.log(uniq_attr)
    // set_x_y_scale_label(x_axis_attr, use_key"number_of_worker");
    var master_record = {};
    var base_key = stack_bar_head_conf["operation_col"];
    

    use_key = stack_bar_head_conf["operation"] + "_of_" + base_key;
    if(stack_bar_head_conf["operation"] === "size")
        set_x_y_scale_label(x_axis_attr, "number_of_"+frame_name);
    else
        set_x_y_scale_label(x_axis_attr, use_key);

    // console.log(use_key)

    // console.log(chart_data)

    master_set = uniq_attr;
    jQuery.each(chart_data[x_axis_attr] , function(idx, one_x_axis_attr){
        var record = {};
        if(one_x_axis_attr in master_record)
        {
            master_record[one_x_axis_attr][chart_data[stack_bar_head_conf["group_head"]][idx]] =chart_data[use_key][idx];
        }
        else
        {
            record[chart_data[stack_bar_head_conf["group_head"]][idx]] = chart_data[use_key][idx];
            master_record[one_x_axis_attr] = record;
        }
    })
    
    label = Object.keys(master_record);
    
    var final_result = {};

    // prepare record set varibales (array)
    jQuery.each(master_set, function(idx,val){
        final_result[val] = [];
    })

    var total_data = [];
    var mean_data = [];
    jQuery.each(master_record, function(one_x_axis_attr, dataset){
        avail_attr = Object.keys(dataset)
        not_avail_attr = jQuery(master_set).not(avail_attr).get();

        var total = 0;
        jQuery.each(avail_attr, function(idx, val){
            final_result[val].push(dataset[val]);
            console.log(dataset[val])
            total = total + dataset[val];
        })

        total_data.push(total);
        mean_data.push(total/avail_attr.length);

        jQuery.each(not_avail_attr, function(idx, val){
            final_result[val].push(null);
        })
    })
    final_result["total"] = {"chart_type":"line", "data":total_data};
    // final_result["average"] = {"chart_type":"line", "data":mean_data};
    chart_data = {"labels" : label, "dataset": final_result };
    console.log(chart_data)
    return chart_data;
}

function render_stack_bar_chart(x_axis_attr, stack_bar_head_conf, filters=[])
{   
    group_head = stack_bar_head_conf["group_head"]
    if(stack_bar_head_conf["operation_col"] == undefined)
    {
        operation_col = group_head;
        stack_bar_head_conf["operation_col"] = group_head;
    }
    else
    {
        operation_col = stack_bar_head_conf["operation_col"];
    }

    if(stack_bar_head_conf["operation"] == undefined)
    {
        operation = "size";
        stack_bar_head_conf["operation"] = "size";
    }
    else
    {
        operation = stack_bar_head_conf["operation"];
    }
    
    if(group_head != operation_col)
        special_column_of_list = [group_head, operation_col];
    else
        special_column_of_list = [group_head];

    properties = {group_by: [group_head], head: [operation_col], data_type: [operation], filters:JSON.stringify(filters), unique_by_columns:[ ]};
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        jQuery.when(get_column_uniq_attr(group_head)).done(function(uniq_attr){
            chart_data = sanitize_render_stack_bar_chart_data(data, x_axis_attr, Object.keys(uniq_attr));
            add_data(chart_data);

            myChart.data.datasets[myChart.data.datasets.length -1].backgroundColor = "transparent"
            myChart.update()
        })
    });
}

// ================================== End Current Month BCPM Status Functions ================================












































// ================================== Start Current Worker Claimed Functions ================================


function sanitize_render_worker_claimed_current_chart_data(data, x_axis_attr)
{
    set_x_y_scale_label(x_axis_attr, "Number of "+worker);
    label = Object.values(data[x_axis_attr]);
    delete data[x_axis_attr]
    dataset = {};
    dataset["no_of_"+worker] = Object.values(data["size_of_" + worker + "_id"]); 
    data = {"labels" : label, dataset : dataset };
    return data;

}


function render_worker_claimed_current(x_axis_attr, filters=[])
{
    properties = {group_by: [x_axis_attr], head: [worker + "_id"], data_type: ["size"], filters:JSON.stringify(filters) };
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_render_worker_claimed_current_chart_data(data, x_axis_attr);
        add_data(chart_data);
    });
}

// ================================== End Current Worker Claimed Functions ================================


jQuery("#chart_select").change(function (param) { 
    let custom_type = jQuery(this).val();
    jQuery.each(myChart.data.datasets, function(dataset_number, dataset){
        dataset.type = custom_type;
    })

    myChart.config.type = jQuery(this).val();
    myChart.update();
})

jQuery("#stack_toggle").click(function(){
    myChart.config.options.scales.xAxes[0].stacked = jQuery(this).is(":checked");
    myChart.config.options.scales.yAxes[0].stacked = jQuery(this).is(":checked");
    myChart.update();
})


function toggle_dataset_order(param)
{
    var class_name = jQuery(param).children("i:first").attr('class');

    jQuery(param).children("i:first").removeClass(class_name);

    if(class_name.indexOf("desc") != -1)
    {
        jQuery(param).children("i:first").addClass("fa fa-sort-amount-asc");
    }
    else
    {
        jQuery(param).children("i:first").addClass("fa fa-sort-amount-desc");
        
    }

    order_chart("", "")
}


function set_chart_sort()
{
    let sort_order = []
    jQuery('#chart_attribute_set_order').children('li').each(function(i) { 
        attr = jQuery(this).text();
        type = ( (jQuery(this).children('i').attr("class")).indexOf("desc") != -1) ? "desc" : "asc";
        console.log(attr, type);

        console.log(SORTABLE_DATA[attr], "danish")
        sort_order.push(attr + ":" +type)
    });

    configuration_set.sort_order = sort_order;

    draw_chart(configuration_set);
}

function populate_chart_legend(data)
{
    let $dropdown = jQuery("#legend_select");
    jQuery("#legend_select option").remove();


    if(configuration_set.sort_order == undefined)
    {
        populate_filter(data);
    }

    data.forEach(function(ds) {
        if(ds.hidden)
            $dropdown.append(jQuery("<option />").val(ds.datasetIndex).text(ds.text));
        else
            $dropdown.append(jQuery("<option />").val(ds.datasetIndex).text(ds.text).attr('selected','selected'));
    });

    jQuery(".selectpicker").selectpicker("refresh");
}

function populate_filter(data)
{
    let $attribute_set = jQuery("#chart_attribute_set");

    let $attribute_set_order = jQuery("#chart_attribute_set_order");

    jQuery("#chart_attribute_set li").remove();
    jQuery("#chart_attribute_set_order li").remove();

    data.forEach(function(ds) {
        $attribute_set.append(jQuery("<li />").addClass("my_li").text(ds.text).append(' <i class="fa fa-sort-amount-asc"></i>').attr("onclick", "toggle_dataset_order(this)"))
    });
    

}

jQuery('#onchart_label, input[name=label]').click(function(){
    // console.log(jQuery(this).attr('aria-pressed'));
    let is_active = jQuery("#onchart_label").is(":checked");
    // console.log(is_active)
    if(is_active)
    {
        jQuery('.chart_label_type').show();
        myChart.options.plugins.datalabels.display=true;
        label_type = jQuery('input[name=label]:checked').val()
        if(label_type.indexOf("percentage") != -1)
        {
            plug_label = `(value, ctx) => {
                let sum = 0;

                if(ctx.chart.data.datasets[ctx.datasetIndex].label === "total")
                {
                    return "Total = "+value;
                }

                if(label_type === "percentage_s")
                {
                    var dataArr = [];
                    var i = 0;
                    for (i = 0; i < Object.keys(ctx.chart.data.datasets).length; i++) {
                        if(ctx.chart.data.datasets[i].label != "total")
                        {
                            dataArr.push(ctx.chart.data.datasets[i].data[ctx.dataIndex]);
                        }
                        
                    } 
                }
                else if(label_type === "percentage_o")
                {
                    // if(ctx.chart.data.datasets[i].label != "total")
                    var dataArr = ctx.chart.data.datasets[ctx.datasetIndex].data;
                }
                dataArr.map(data => {
                    sum += data;
                });
                let percentage = (value*100 / sum).toFixed(2)+"%";
                return percentage;
            }`;
        }
        else
        {
            plug_label = `Math.round`;
        }
        myChart.options.plugins.datalabels.formatter=eval(plug_label);
    }
    else
    {
        myChart.options.plugins.datalabels.display=false
        jQuery('.chart_label_type').hide();
    }
    myChart.update();
})






// This varible specify which column of data frame render by default while rendring during chart report

var FRAME_TO_CHART_REPORT_COLUMN = {
    asha : ["asha_id", "name", "district_name", "block_name", "sub_center_name", "village_name"],
    sangini : ["sangini_id", "name", "district_name", "block_name", "sub_center_name", "village_name"],
    anm : ["anm_id", "name", "district_name", "block_name", "sub_center_name"],
    asha_payment : ["asha_id", "name", "district_name", "block_name", "sub_center_name", "village_name", "month", "year"],
    asha_payment_status : ["district_name", "block_name", "submit", "approved", "payment", "month", "year"],
    sangini_payment : ["sangini_id", "name", "district_name", "block_name", "sub_center_name", "village_name", "month", "year"],
    sangini_payment_status : ["district_name", "block_name", "submit", "approved", "payment", "month", "year"],

    committees: ["DISTRICT", "BLOCK","Name of Committee","ctype","Date of MOU","OTG Date","OTG Amount"],
    // committees: ["Name of Committee", "ctype", "Date of MOU", "OTG Amount", "OTG Date", "DISTRICT", "BLOCK",],
    members: ["DISTRICT", "BLOCK","Name of Committee","ctype","Name","Sex","Age","Designation","Representative"],
    rbf_Manager: ["DISTRICT", "BLOCK","Name of Committee","ctype","OTG Date","OTG Amount","current_rbf","rbf_0","rbf_0_status","rbf_1","rbf_1_status","rbf_2","rbf_2_status","rbf_3","rbf_3_status","rbf_4","rbf_4_status","rbf_5","rbf_5_status","rbf_6","rbf_6_status","rbf_7","rbf_7_status","rbf_8","rbf_8_status","rbf_9","rbf_9_status","rbf_10","rbf_10_status"],
    
    action_plan: ["DISTRICT", "BLOCK","Name of Committee","ctype","OTG Date","RBF Cycle","enrollmentDate","rbf_state","Activity Type","Activity Comments on Activity by Demonstrator","Activity Estimated funds required to conduct this activity","Activity Estimated time taken to conduct this activity","Activity Feedback by State Consultants","Activity How will the activity be conducted?","Activity Planned activities with the funds received / goals to be achieved"],
    
    fund_status_with_six_month_expenditure : ["DISTRICT","Name of Committee","ctype","RBF Cycle","RBF Amount","RBF Amount Date","Interest Credited from Bank - Amount","Interest Credited from Bank - Date","Previous balance - Amount","Previous balance - Date","Community Contribution Amount","Community Contribution Date","Interest Credited from Bank Q2 - Amount","Interest Credited from Bank Q2- Date","Fund received comments (if any)","Total Fund - Amount","Total Fund - Date","Approved Budget","Six monthly Expenditure (Rs)",],
    
    six_monthly_expenditure : ["DISTRICT", "BLOCK", "COMMUNITY HEALTH CENTER", "PRIMARY HEALTH CENTER", "SUB CENTER", "VILLAGE"],
};

// ============================================== Start Show Data Table of Records ===================================



    
// var advance_filter = {}
// function prepare_data_table(filters, df_function="")
// {
//     console.log(filters)
//     // reset advance filter
//     var advance_filter = {};
//     // $chart_back_button.show();
//     $chart_rendring_area.hide();
//     $data_table_parent.show();
//     var columns = Object.create(FRAME_TO_CHART_REPORT_COLUMN[frame_name]); //jQuery.merge( [ frame_name.split("_")[0]+"_id","name"], chart_order );
//     if(special_column_of_list)
//     {
//         columns = jQuery.merge( columns, special_column_of_list );
//     }
//     jQuery.each(filters, function(idx, filter){
        
//         advance_filter["dynamic_form[dynamic_form][" + idx + "][attribute]"] = filter.attr;
//         advance_filter["dynamic_form[dynamic_form][" + idx + "][condition]"] = filter.operator;
//         advance_filter["dynamic_form[dynamic_form][" + idx + "][value]"] = filter.value;
//     })
    
//     dt_columns = [];
//     var show_all = ``;

//     if(chart_filters.join().indexOf("population_category") != -1){
//         show_all = `<label style="float:right;" onclick="handle_show_all()" id="show_all">Show All</label>`;
//     }
//     let close_button = `<button onclick="$chart_rendring_area.show(); $data_table_parent.hide();" type="button" class="btn btn-danger" style="position: absolute; right: 37px; z-index: 9999;">
//                             <i class="fa fa-times-circle"></i>
//                         </button>`;
//     var table = close_button + `<p class "text-center"><kbd>`+ filters[filters.length - 1].attr.toUpperCase() + myChart.options.title.text.replace("ALL ", " ") +`</kbd>` + show_all + `</p><table id="master-details-data-table" class="table table-striped table-bordered table-hover"></table>`;
//     $data_table_parent.html(table);

//     console.log(columns);
//     jQuery.each(columns, function (idx, vals) {
//         // dt_columns.push({'data':vals, "orderable": true});
//         dt_columns.push({title: vals.replace(/_/g, ' '), data:vals});
//     });
//     dt_columns.push({'data':'hash', "orderable": false});
//     // Call Function to form data table

//     data_table(dt_columns, {filter:advance_filter, get_data_frame_function:df_function } );
    
// }

// ============================================== End Show Data Table of Records ===================================
















// ================================== Start NHP avg population Functions ================================



function sanitize_render_multi_head(data, x_axis_attr)
{
    set_x_y_scale_label(x_axis_attr, "Total Amount");
    label = Object.values(data[x_axis_attr]);
    delete data[x_axis_attr]

    dataset = {};
    jQuery.each(data, function(idx, val){
        temp_label = idx.replace('sum_of_', "")
        dataset[temp_label] =  Object.values(val);
    })
    data = {"labels" : label, dataset : dataset };
    return data;

}

function render_multi_head(x_axis_attr, filters=[])
{

    data_type = Array(special_column_of_list.length).fill("sum")
    properties = { group_by: [x_axis_attr], head: special_column_of_list, data_type: data_type, sort_by:x_axis_attr, filters:JSON.stringify(filters) };
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_render_multi_head(data, x_axis_attr);
        // add_data(chart_data.labels, chart_data.dataset);
        add_data(chart_data);
    });
}



function modify_dataset(configuration) 
{  

    jQuery.each(configuration.rename_data_set, function(key, value) {
        console.log(key, value);

        // myChart.
    })

}




// Stand Alone Function Start //


function getChartTitle()
{
    title = 'ALL ' + configuration_set.group_by[0]
    jQuery.each(configuration_set.filters, function(idx, one_filter)
    {
        let str = idx==0 ? " where " : " and ";
        title = title + str +one_filter.attr + " " + one_filter.operator + " " + one_filter.value;
    });

    return title
    
}

function draw_chart(configuration_set)
{
    ChartColor = ["#3366cc","#dc3912","#ff9900","#109618","#990099","#0099c6","#dd4477","#66aa00","#b82e2e","#316395","#3366cc","#994499","#22aa99","#aaaa11","#6633cc","#e67300","#8b0707","#651067","#329262","#5574a6","#3b3eac","#b77322","#16d620","#b91383","#f4359e","#9c5935","#a9c413","#2a778d","#668d1c","#bea413","#0c5922","#743411", "#F88101", "#CC9966", "#A366FF", "#B2BD4D", "#34495E", "#4DBD74", "#F86C6B", "#FFC107", "#20A8D8" ]
    configuration_set.group_by = configuration_set.group_by ? configuration_set.group_by : [chart_order[0]];

    if(configuration_set.group_heads != undefined)
    {
        configuration_set.group_by
        configuration_set.group_by = jQuery.merge(configuration_set.group_by, configuration_set.group_heads)
    }

    myChart.options.title.text = getChartTitle().toUpperCase();

    myChart.options.scales.xAxes[0].scaleLabel.labelString = configuration_set.group_by[0].replace(/_/g, ' ').toUpperCase();

    configuration_set.filters = JSON.stringify(configuration_set.filters)
    jQuery.when(generate_chart_data_ajax(configuration_set)).done(function(data){
        console.log(data);
        key = configuration_set.group_by[0]

        // let NA_INDEX = Object.values(data[key]).indexOf("N/A")
        // delete data[key][NA_INDEX]
        let labels = Object.values(data[key]);
        delete data[key]

        // console.log(data)

        // jQuery.each(data, function(k, val){
        //     console.log(k)
        //     delete data[k][NA_INDEX]
        // })

        // console.log(data)

        let master_dataset = {labels: [], datasets : []};

        temp = {}
        let dataset = {}

        if (configuration_set.group_heads != undefined)
        {
            let group_head  = configuration_set.group_heads[0];
            let unique_attr = jQuery.unique(Object.values(data[group_head]).sort());

            let multi_label = {}
            jQuery.each(labels , function(key,value) {
                data_set_name =  data[group_head][key];
                if (!multi_label.hasOwnProperty(value)) {
                    // multi_label[value] = [key];
                    multi_label[value] = {};
                    jQuery.each(unique_attr, function(idx, val) {
                        multi_label[value][val] = -1;
                    })
                    multi_label[value][data_set_name] = key;
                } 
                else {
                    // multi_label[value].push(key)
                    multi_label[value][data_set_name] = key;
                }
            });
            
            dataset["total"] = [];
            jQuery.each(multi_label, function(one_label, data_set_info){
                // pushing labels
                master_dataset.labels.push(one_label)
                let total_sum = 0;
                jQuery.each(data_set_info, function(data_set, data_index){
                    // console.log(data_set, data_index)
                    jQuery.each(configuration_set.head, function(i, h) {
                        response_key = configuration_set.data_type[i] + "_of_" + h;
                        // response_key_values = Object.values(data[response_key]);
                        value = (data_index == -1) ? 0 : data[response_key][data_index]
                        new_key = data_set + "_" + response_key
                        total_sum += value;
                        if(! dataset.hasOwnProperty(new_key) )
                        {
                            dataset[new_key] = [value];
                        }
                        else
                        {
                            dataset[new_key].push(value);
                        }
                    })
                    
                })
                dataset["total"].push(total_sum);
            })
        }
        
        else
        {
            master_dataset.labels = labels
            jQuery.each(configuration_set.head, function(i, h) {
                response_key = configuration_set.data_type[i] + "_of_" + h;

                response_key_values = Object.values(data[response_key]);
                
                dataset[response_key] = response_key_values
            });
        }

        jQuery.each(dataset, function(dataset_name, dataset_data){
            if(dataset_name === "total")
            {
                dataset_conf = generateDataSet({
                    label: dataset_name,
                    type: "line",
                    backgroundColor: "transparent",
                    borderColor: "#272C33",
                    borderWidth : 1,
                })
            }
            else
            {
                dataset_conf = generateDataSet({label: dataset_name})
            }

            if(configuration_set.headDatasetConf)
            {
                if(configuration_set.headDatasetConf[dataset_name])
                {
                    dataset_conf = jQuery.extend(dataset_conf, configuration_set.headDatasetConf[dataset_name]);
                }
                else
                {
                    // dataset_conf.label = dataset_conf.label.replace(/(_)?(size|mean|sum)_of_(hash)?/g, " ")
                }
            }
            else
            {
                // dataset_conf.label = dataset_conf.label.replace(/(_)?(size|mean|sum)_of_(hash)?/g, " ")
            }

            basic_label_set = {"size_of_":"No. of ", "mean_of_": "Average of ", "sum_of_":"Total of "};

            jQuery.each(basic_label_set, function(key, val){
                        regex = new RegExp(key);
                        console.log(regex)
                        dataset_conf.label = dataset_conf.label.replace(regex, val);
                    })
            // dataset_conf.label = dataset_conf.label.replace("_of_", " "); 
            dataset_conf.label = dataset_conf.label.replace("hash", frame_name);
            dataset_conf.label = dataset_conf.label.replace(/_/g, " ");
            
            if (dataset_conf.label === "total")
            {
                dataset_conf.label = dataset_conf.label.toUpperCase()
            }

            if (configuration_set.find_replace_label)
            {
                dataset_conf.label = dataset_conf.label.replace(configuration_set.find_replace_label.from, configuration_set.find_replace_label.by);
            }
            
            // try 
            // {
            //     dataset_conf = jQuery.extend(dataset_conf, configuration_set.headDatasetConf[dataset_name])
            // }
            // catch(err)
            // {
            //     dataset_conf.label = dataset_conf.label.replace(/_(size|mean|sum)_of_.*/g, "")
            // }
            
            dataset_conf.data = dataset_data
            master_dataset.datasets.push(dataset_conf)
        })

        // if(configuration_set.modify_dataset != undefined)
        // {
        //     let data_set_operation = configuration_set.modify_dataset.data_set_operation;

        //     if( (data_set_operation != undefined) && (data_set_operation[response_key] != undefined) )
        //     {
        //         eval(`response_key_values = response_key_values.map(function(x) { return parseInt(x ` + data_set_operation[response_key].operator + data_set_operation[response_key].value + `); });`);
        //     }

        //     chart_key = (configuration_set.modify_dataset.rename_data_set[response_key] == undefined) ? response_key: configuration_set.modify_dataset.rename_data_set[response_key]
        // }
        // else
        // {
        //     chart_key = response_key;
        // }

        configuration_set.filters = JSON.parse(configuration_set.filters)

        myChart.data = master_dataset;
        myChart.update();

        populate_chart_legend(myChart.legend.legendItems);

        SORTABLE_DATA = {}
        jQuery.each(myChart.data.datasets, function(idx, one_data){
            SORTABLE_DATA[one_data.label.trim()] = one_data.data
        })
        SORTABLE_DATA["labels"] = myChart.data.labels
        // add_data(dataset);
    });

    // modify_dataset(configuration_set.modify_dataset)
}






// Stand Alone Function End // 







function sanitize_required_vs_available_worker_chart_data(data, x_axis_attr)
{
    set_x_y_scale_label(x_axis_attr, "number_of_"+frame_name);
    population_set = Object.values(data.sum_of_population);
    var required_number_of_worker = [];
    jQuery.each(population_set, function(idx, one_data){    
        required_number_of_worker.push( Math.round(one_data/1000));
    })
    // total_worker = Object.values(data[frame_name+"_id_count_by_"+x_axis_attr]);
    total_worker = Object.values(data["size_of_"+frame_name+"_id"]);
    label = Object.values(data[x_axis_attr]);
    // console.log(frame_name);
    dataset = {};
    dataset["total_"+frame_name] = {data : total_worker, chart_type:"line"}
    dataset["required_number_of_"+frame_name] = {data: required_number_of_worker, chart_type:"line"}
    data = {"labels" : label, dataset : dataset };
    return data;

}


function render_required_vs_available_worker_distribution(x_axis_attr, filters=[])
{
    properties = { group_by: [x_axis_attr], head: ["population", frame_name+"_id"], data_type: ["sum", "size"], "filters":JSON.stringify(filters) };
    // properties = { counts_of_attr_n_by:[frame_name+"_id|"+x_axis_attr], sort_by: x_axis_attr, head: ["population"], group_by:[x_axis_attr], data_type: ["sum"], filters:JSON.stringify(filters) };
    jQuery.when(generate_chart_data_ajax(properties)).done(function(data){
        chart_data = sanitize_required_vs_available_worker_chart_data(data, x_axis_attr);
        add_data(chart_data);
    });
}



// ================================== End NHP avg population Functions ================================

