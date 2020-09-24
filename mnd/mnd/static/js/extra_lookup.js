function refreshHtml() {
  return '<div class="refresh" style="position:absolute;margin-left:-20px;margin-top:7px;">' +
         '   <i class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></i>' +
         '</div>';
}

function addRefreshIcon(element) {
  if ( !element.parent().find(".refresh").length) {
    element.before(refreshHtml());
  }
}

function removeRefreshIcon(element) {
  element.parent().find('.refresh').remove();
}

function lookupValue(element, value, secondary_source, suffixes) {
    var full_query = secondary_source + "?product=" + value;
    addRefreshIcon(element);
    $.get(full_query, function(result) {
      var query = "[id$='" + suffixes[0] + "']";
      element.parent().find(query).val(result.activeIngredient || '');
      var query = "[id$='" + suffixes[1] + "']";
      element.parent().find(query).val(result.mims || '');
      element.val(result.name || '');
      removeRefreshIcon(element);
    });
  }


  function dependentLookup(element, source_url, secondary_source, suffixes) {
    element.autocomplete({
      source: source_url,
      minLength: 4,
      select: function(event, ui) {
        console.log("Selected", ui);
        element.next().val(ui.item.id);
        lookupValue(element, ui.item.id, secondary_source, suffixes);
      },
      search: function(){
        addRefreshIcon(element);
      },
      response: function(){
        removeRefreshIcon(element);
      },
    }).data("ui-autocomplete")._renderItem = function(ul, item) {
      item.value = item.label;
      return $("<li>")
        .append("<a>" + item.label + "</a>")
        .appendTo(ul);
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
    var full_query = secondary_source + "?product=" + value;
    hideMedicineInfo(target_el);
    addRefreshIcon(element);
    $.get(full_query, function(result) {
      result.link ? showMedicineInfo(target_el, result.link): hideMedicineInfo(target_el);
      element.val(result.name || '');
      removeRefreshIcon(element);
    });
  }

  function cmiLookup(element, source_url, secondary_source, target_el) {
    element.autocomplete({
      source: source_url,
      minLength: 4,
      select: function(event, ui) {
        element.next().val(ui.item.id);
        lookupCMI(element, ui.item.id, secondary_source, target_el);
      },
      search: function(){
        addRefreshIcon(element);
      },
      response: function(){
        removeRefreshIcon(element);
      },
    }).data("ui-autocomplete")._renderItem = function(ul, item) {
      item.value = item.label;
      return $("<li>")
        .append("<a>" + item.label + "</a>")
        .appendTo(ul);
    };
  }

  