function load_widget_chart()
{    
    // properties = { group_by: ["gender"], head: ["hash"], data_type: ["size"] };
    // draw_dash_chart(properties, "gender_distribution", "pie", null, "No. of CHO", false);

    properties = { group_by: ["REGION"], head: ["hash"], data_type: ["size"] };
    draw_dash_chart(properties, "total_cho", "radar", null, "No. of SUB CENTER", false);
   
    properties = { group_by: [], head: ["hash"], data_type: ["size"] };
    draw_dash_chart(properties, "cho_gender_wise", "radar", null, "No. of SUB CENTER", false);

    properties = { group_by: ["mobile_status"], head: ["hash"], data_type: ["size"] };
    draw_dash_chart(properties, "cho_invalid_mobile", "pie", null, "No. of SUB CENTER", false);
    
    properties = { group_by: ["Age-Group"], head: ["hash"], data_type: ["size"] };
    draw_dash_chart(properties, "age", "bar", null, "No. of CHO",false);
    
    properties = { group_by: ["working_since_year"], head: ["hash"], data_type: ["size"] };
    draw_dash_chart(properties, "working_since", "doughnut", null, "No. of CHO",false);


}



function getChartDetails()
{ 
    return {
    
    "cho_gender_wise":`
                                        prepare_basic_chart(true);  
                                        head_operation = {"hash":"size"}
                                        configuration_set = { head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                        draw_chart(configuration_set);
                                        configuration_set.headDatasetConf = {   
                                            size_of_hash : {label : "No. of CHO"}, 
                                        }                            
                                
                                        `,//group_heads:["STATE"],
     "age":`
                                        prepare_basic_chart(true);  
                                        head_operation = {"hash":"size"}
                                        configuration_set = {head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                        
                                        
                                        
                                        
                                        configuration_set.headDatasetConf = {   
                                            size_of_hash : {label : "No. of CHO"}, 
                                        }


                                        
                                        draw_chart(configuration_set);
                                                                     
                                
                                        `,
     "cho_invalid_mobile":`
                                        prepare_basic_chart(true);  
                                        head_operation = {"hash":"size"}
                                        configuration_set = { head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                        configuration_set.headDatasetConf = {   
                                            size_of_hash : {label : "No. of CHO"}, 
                                        }


                                        
                                        draw_chart(configuration_set);                                                                   
                                
                                        `,



"total_cho":`
                                        prepare_basic_chart(true);  
                                        head_operation = {"hash":"size"}
                                        configuration_set = { head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                        configuration_set.headDatasetConf = {   
                                            size_of_hash : {label : "No. of CHO"}, 
                                        }


                                        
                                        draw_chart(configuration_set);                                                                   
                                
                                        `,
"working_since":`
                                        prepare_basic_chart(true);  
                                        head_operation = {"hash":"size"}
                                        configuration_set = { head: Object.keys(head_operation), data_type: Object.values(head_operation), filters:[] };
                                        configuration_set.headDatasetConf = {   
                                            size_of_hash : {label : "No. of CHO"}, 
                                        }


                                        
                                        draw_chart(configuration_set);                                                                   
                                
                                        `,
                                                                        
            }
        }

