jQuery(function () {

  /* Functions */

  var loadForm = function () {
    var btn = jQuery(this);
    jQuery.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        jQuery("#modal-user").modal("show");
      },
      success: function (data) {
        jQuery("#modal-user .modal-content").html(data.html_form);
      }
    });
  };

  var saveForm = function () {
    var form = jQuery(this);
    jQuery.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          jQuery("#user-table tbody").html(data.html_user_list);
          jQuery("#modal-user").modal("hide");
        }
        else {
          jQuery("#modal-user .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };

  /* Binding */

  // Create user
  jQuery(".js-create-user").click(loadForm);
  jQuery("#modal-user").on("submit", ".js-user-create-form", saveForm);

  // Update user
  jQuery("#user-table").on("click", ".js-update-user", loadForm);
  jQuery("#modal-user").on("submit", ".js-user-update-form", saveForm);

jQuery("#user-table").on("click", ".js-delete-user", loadForm);
jQuery("#modal-user").on("submit", ".js-user-delete-form", saveForm);

});