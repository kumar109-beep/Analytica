jQuery('#zoomBtn').click(function() {
  jQuery('.zoom-btn-sm').toggleClass('scale-out');
  if (!jQuery('.zoom-card').hasClass('scale-out')) {
    jQuery('.zoom-card').toggleClass('scale-out');
  }
});

jQuery('.zoom-btn-sm').click(function() {
  var btn = jQuery(this);
  var card = jQuery('.zoom-card');

  if (jQuery('.zoom-card').hasClass('scale-out')) {
    jQuery('.zoom-card').toggleClass('scale-out');
  }
  if (btn.hasClass('zoom-btn-person')) {
    card.css('background-color', '#d32f2f');
  } else if (btn.hasClass('zoom-btn-doc')) {
    card.css('background-color', '#fbc02d');
  } else if (btn.hasClass('zoom-btn-tangram')) {
    card.css('background-color', '#388e3c');
  } else if (btn.hasClass('zoom-btn-report')) {
    card.css('background-color', '#1976d2');
  } else {
    card.css('background-color', '#7b1fa2');
  }
});
