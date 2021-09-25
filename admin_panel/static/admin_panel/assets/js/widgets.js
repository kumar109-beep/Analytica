function addCommas(nStr)
{
    nStr += '';
    x = nStr.split('.');
    x1 = x[0];
    x2 = x.length > 1 ? '.' + x[1] : '';
    var rgx = /(\d+)(\d{3})/;
    while (rgx.test(x1)) {
        x1 = x1.replace(rgx, '$1' + ',' + '$2');
    }
    return x1 + x2;
}

function startCounter(){
	jQuery('.count').each(function (index) {
        var size = jQuery(this).text().split(".")[1] ? jQuery(this).text().split(".")[1].length : 0;
	    jQuery(this).prop('Counter',0).animate({
	        Counter: jQuery(this).text()
	    }, {
	        duration: 2000,
	        easing: 'swing',
	        step: function (now) {
	            jQuery(this).text(addCommas(parseFloat(now).toFixed(size)));
	        }
	    });
	});
}	

Chart.defaults.scale.ticks.display = false;

// polar white grid
Chart.defaults.polarArea.scale["gridLines"] =  { color: 'white', circular: true };

// Handle size of label in radar charts
Chart.defaults.radar.scale["pointLabels"] = {};
Chart.defaults.radar.scale["point"] =  { color: 'white' };
Chart.defaults.radar.scale["angleLines"] =  { color: 'white' };
Chart.defaults.radar.scale["gridLines"] =  { color: 'white' };
Chart.defaults.radar.scale.pointLabels["callback"] = {};
Chart.defaults.radar.scale.pointLabels["fontColor"] = "white";
Chart.defaults.radar.scale.pointLabels.callback = function(pointLabel, index, labels) {
    return pointLabel.length <= 12 ? pointLabel : pointLabel.substring(0,12)+"...";
} ;



function widgetChart(chart_type, chart_data, canvas_id, legend_name, fill_type)
{
    var background_transparency = .55;
    var d_set = {
        type :"",
        data: [],
        label: [],
        backgroundColor: Color('rgb(255,255,255)').alpha(0.55).rgbString(),
        borderColor: Color('rgb(255,255,255)').alpha(0.55).rgbString(),
        pointHoverBackgroundColor: 'red',
        pointBackgroundColor : 'white',
        pointStyle:'circle',
        fill : fill_type,
    };
    
    datasets = []
    if(chart_data.dataset)
    {
        labels = chart_data.labels;
        jQuery.each(chart_data.dataset, function(key, val){
            // temp_set = Object.create(d_set);
            temp_set =  jQuery.extend(true, {}, d_set);
            if ("data" in val)
                temp_set.data = Object.values(val.data);
            else
                temp_set.data = Object.values(val);
            temp_set.label = key.replace(/_/g, " ").toUpperCase();
            datasets.push(temp_set);
        })
    }
    else 
    {
        // temp_set = Object.create(d_set);
        temp_set =  jQuery.extend(true, {}, d_set);
        keys = Object.keys(chart_data);

        if(chart_type=== "pie" || chart_type=== "doughnut" || chart_data === "radar")
        {
            // console.log(keys);
        }
        else
        {
            temp_set.label = legend_name.replace(/_/g, " ").toUpperCase();
        }
        labels = Object.values(chart_data[keys[0]]);
        temp_set.data = Object.values(chart_data[keys[1]])
        datasets.push(temp_set);

    }
    
    canvas = jQuery("#"+canvas_id);
    canvas_parent = canvas.parent();
    canvas.remove();
    canvas_parent.append('<canvas id='+canvas_id +'> </canvas>')


    if(chart_type === "radar")
    {
        custom_tooltip = {
            mode: 'index',
            callbacks: {
                label: function(tooltipItem, data) {
                    return data.datasets[tooltipItem.datasetIndex].label + ' : ' + data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
                }
            }
        }
    }
    else
    {
        custom_tooltip = {
            mode: 'index',
        }
    }



    // console.log(datasets)

    var ctx = document.getElementById(canvas_id);
    var myChart = new Chart( ctx, {
        type: chart_type,
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            plugins: {
                // Change options for ALL labels of THIS CHART
                datalabels: {
                    display: false,
                }
            },
            scaleShowLabels: false,
            bezierCurve : false,
            maintainAspectRatio: true,
            legend: {
                display: false
            },
            responsive: true,
            scales: {
                xAxes: [ {
                    gridLines: {
                        color: 'transparent',
                        zeroLineColor: 'transparent'
                    },
                    ticks: {
                        fontSize: 2,
                        fontColor: 'transparent'
                    }
                } ],
                yAxes: [ {
                    display:false,
                    ticks: {
                        display: false,
                    }
                } ]
            },
            title: {
                display: false,
            },
            tooltips: custom_tooltip,
            animation: {
                animateRotate: true,
                easing: 'linear'
            },
            elements: {
                line: {
                    borderWidth: 1
                },
                point: {
                    radius: 4,
                    hitRadius: 10,
                    hoverRadius: 4
                }
            }
        }
    } );
}