var rules_plugins = {
  condition: 'AND',
  rules: [{
    id: 'name',
    operator: 'equal',
    value: 'Mistic'
  }, {
    condition: 'OR',
    rules: [{
      id: 'xcategory',
      operator: 'in',
      value: [1, 2]
    }, {
      id: 'in_stock',
      operator: 'equal',
      value: 0
    }]
  }]
};

$('#builder-plugins').queryBuilder({
  plugins: [
    'sortable',
    'filter-description',
    'unique-filter',
    'bt-tooltip-errors',
    'bt-selectpicker',
    'bt-checkbox',
    'invert',
    'not-group'
  ],

  filters: [{
    id: 'danish',
    label: 'Datepicker',
    type: 'date',
    validation: {
      format: 'YYYY/MM/DD'
    },
    plugin: 'datepicker',
    plugin_config: {
      format: 'yyyy/mm/dd',
      todayBtn: 'linked',
      todayHighlight: true,
      autoclose: true
    }
  },{
    id: 'name',
    label: 'Name',
    type: 'string',
    unique: true,
    description: 'This filter is "unique", it can be used only once',
  }, {
    id: 'xcategory',
    label: 'xCategory',
    type: 'integer',
    input: 'checkbox',
    values: {
      1: 'Books',
      2: 'Movies',
      3: 'Music',
      4: 'Goodies'
    },
    color: 'primary',
    description: 'This filter uses Awesome Bootstrap Checkboxes',
    operators: ['equal', 'not_equal', 'in', 'not_in', 'is_null', 'is_not_null']
  },
  {
    id: 'category',
    label: 'Selectize',
    type: 'string',
    plugin: 'selectize',
    plugin_config: {
      valueField: 'id',
      labelField: 'name',
      searchField: 'name',
      sortField: 'name',
      create: true,
      maxItems: 5,
      plugins: ['remove_button'],
      onInitialize: function() {
        var that = this;
        if (localStorage.demoData === undefined) {
          $.getJSON(baseurl + '/assets/demo-data.json', function(data) {
            localStorage.demoData = JSON.stringify(data);
            data.forEach(function(item) {
              that.addOption(item);
            });
          });
        }
        else {
          JSON.parse(localStorage.demoData).forEach(function(item) {
            that.addOption(item);
          });
        }
      }
    },
    valueSetter: function(rule, value) {
      rule.$el.find('.rule-value-container input')[0].selectize.setValue(value);
    }
  }, {
    id: 'in_stock',
    label: 'In stock',
    type: 'integer',
    input: 'radio',
    values: {
      1: 'Yes',
      0: 'No'
    },
    colors: {
      1: 'success',
      0: 'danger'
    },
    description: 'This filter also uses Awesome Bootstrap Checkboxes',
    operators: ['equal']
  }, {
    id: 'price',
    label: 'Price',
    type: 'double',
    validation: {
      min: 0,
      step: 0.01
    }
  }],

  rules: rules_plugins
});

$('#btn-reset').on('click', function() {
  $('#builder-plugins').queryBuilder('reset');
});

$('#btn-set').on('click', function() {
  $('#builder-plugins').queryBuilder('setRules', rules_plugins);
});

$('#btn-get').on('click', function() {
  var result = $('#builder-plugins').queryBuilder('getRules');

  if (!$.isEmptyObject(result)) {
    alert(JSON.stringify(result, null, 2));
  }
});
