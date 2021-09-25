$.noConflict();

jQuery(document).ready(function($) {

	"use strict";

	[].slice.call( document.querySelectorAll( 'select.cs-select' ) ).forEach( function(el) {
		new SelectFx(el);
	} );

	jQuery('.selectpicker').selectpicker;


	$('#menuToggle').on('click', function(event) {
		$('body').toggleClass('open');
		Cookies.set('left_panel_state', jQuery('body').attr('class'));
	});

	$('.search-trigger').on('click', function(event) {
		event.preventDefault();
		event.stopPropagation();
		$('.search-trigger').parent('.header-left').addClass('open');
	});

	$('.search-close').on('click', function(event) {
		event.preventDefault();
		event.stopPropagation();
		$('.search-trigger').parent('.header-left').removeClass('open');
	});

	var worker = "";
	//Client Side Menu Handler
	if(! Cookies.get('left_panel_state'))
	{
		var blink_element = '<span class="active_dot">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>'
		var path = window.location.pathname.split('/');
		path = path[path.length - 2];
		var $tab = "";
		if((path === worker + "_payment") || (path === worker + "_payment_pre")){
			$tab = jQuery("#health_worker_payment");
		}
		else if(path === worker + "_payment_status"){
			$tab = jQuery("#health_worker_payment_performance");
		}
		else if(path === worker){
			$tab = jQuery("#health_worker");
		}
		else if(worker === "panel_management") {
			$tab = jQuery("#panel_management");
		}
		else if(worker === "survey") {
			$tab = jQuery("#survey_panel");
		}
		// $tab.parent().addClass("active");
		// $tab.click();
		
	}
});
