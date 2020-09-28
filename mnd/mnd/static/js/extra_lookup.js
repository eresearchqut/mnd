function refreshHtml() {
  return '<div class="refresh" style="position:absolute;margin-left:-20px;margin-top:7px;">' +
         '   <i class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></i>' +
         '</div>';
}

function validInput() {
  return '<div class="valid" style="position:absolute;margin-left:-20px;margin-top:7px;">' +
         '   <span style="color:green;"><i class="glyphicon glyphicon-ok-sign" style="font-size:1.2em;"></i></span>' +
         '</div>';
}

function invalidInput() {
  return '<div class="invalid" style="position:absolute;margin-left:-20px;margin-top:7px;">' +
         '   <span style="color:red;"><i class="glyphicon glyphicon-exclamation-sign" style="font-size:1.2em;" ' +
         '         title="Information for this product not found !"></i></span> ' +
         '</div>';
}

function addRefreshIcon(element) {
  if ( !element.parent().find(".refresh").length) {
    element.before(refreshHtml());
  }
}

function addValidityIcon(element, isValid) {
  var className = isValid ? ".valid" : ".invalid";
  var classFunc = isValid ? validInput : invalidInput;
  if ( !element.parent().find(className).length) {
    element.before(classFunc());
  }
}

function removeValidityIcon(element) {
  element.parent().find('.valid').remove();
  element.parent().find('.invalid').remove();
}

function removeRefreshIcon(element) {
  element.parent().find('.refresh').remove();
}

function setDependentValues(element, result, suffixes) {
  var query = "[id$='" + suffixes[0] + "']";
  element.parent().find(query).val(result.activeIngredient || '');
  var query = "[id$='" + suffixes[1] + "']";
  element.parent().find(query).val(result.mims || '');
  addValidityIcon(element, result.activeIngredient !== undefined);
}

function lookupValue(element, value, secondary_source, suffixes) {
  if (value !== undefined && value.trim() != '') {
    var full_query = secondary_source + "?product=" + value;
    addRefreshIcon(element);
    $.get(full_query, function(result) {
      setDependentValues(element, result, suffixes);
      element.val(result.name || value);
      removeRefreshIcon(element);
    });
  }
}


function dependentLookup(element, source_url, secondary_source, suffixes) {
  element.autocomplete({
    source: source_url,
    minLength: 4,
    select: function(event, ui) {
      removeValidityIcon(element);
      element.next().val(ui.item.id);
      lookupValue(element, ui.item.id, secondary_source, suffixes);
    },
    search: function(){
      removeValidityIcon(element);
      addRefreshIcon(element);
    },
    response: function(){
      removeRefreshIcon(element);
      element.next().val(element.val());
      setDependentValues(element, {}, suffixes);
    },
  }).data("ui-autocomplete")._renderItem = function(ul, item) {
    item.value = item.label;
    return $("<li>").append("<a>" + item.label + "</a>").appendTo(ul);
  };
}

function hideMedicineInfo(target_el) {
  target_el.parent().hide();
  target_el.attr("href", "");
  target_el.attr('disabled', '');
}

function showMedicineInfo(target_el, link) {
  target_el.attr("href", link);
  target_el.attr("target", "_blank");
  target_el.removeAttr('disabled');
  target_el.parent().show();
}

function lookupCMI(element, value, secondary_source, target_el) {
  if (value !== undefined && value.trim() != '') {
    var full_query = secondary_source + "?product=" + value;
    hideMedicineInfo(target_el);
    addRefreshIcon(element);
    $.get(full_query, function(result) {
      result.link ? showMedicineInfo(target_el, result.link): hideMedicineInfo(target_el);
      element.val(result.name || value);
      removeRefreshIcon(element);
      addValidityIcon(element, result.name !== undefined);
    });
  }
}

function cmiLookup(element, source_url, secondary_source, target_el) {
  element.autocomplete({
    source: source_url,
    minLength: 4,
    select: function(event, ui) {
      removeValidityIcon(element);
      element.next().val(ui.item.id);
      lookupCMI(element, ui.item.id, secondary_source, target_el);
    },
    search: function(){
      removeValidityIcon(element);
      addRefreshIcon(element);
    },
    response: function(){
      removeRefreshIcon(element);
      addValidityIcon(element, false);
      element.next().val(element.val());
    },
  }).data("ui-autocomplete")._renderItem = function(ul, item) {
      item.value = item.label;
      return $("<li>").append("<a>" + item.label + "</a>").appendTo(ul);
  };
}
