function lookupValue(element, value, secondary_source, suffixes) {
    var full_query = secondary_source + "?product=" + value;
    $.get(full_query, function(result) {
      var query = "[id$='" + suffixes[0] + "']";
      element.parent().find(query).val(result.activeIngredient);
      var query = "[id$='" + suffixes[1] + "']";
      element.parent().find(query).val(result.mims);
      element.val(result.name);
    });
  }


  function dependentLookup(element, source_url, secondary_source, suffixes) {
    element.autocomplete({
      source: source_url,
      minLength: 1,
      select: function(event, ui) {
        console.log("Selected", ui);
        element.next().val(ui.item.id);
        lookupValue(element, ui.item.id, secondary_source, suffixes);
      }
    }).data("ui-autocomplete")._renderItem = function(ul, item) {
      item.value = item.label;
      return $("<li>")
        .append("<a>" + item.label + "</a>")
        .appendTo(ul);
    };
  }

  function lookupCMI(element, value, secondary_source, target_el) {
    var full_query = secondary_source + "?product=" + value;
    target_el.parent().hide();
    target_el.attr("href", "");
    target_el.attr('disabled', '');
    $.get(full_query, function(result) {
      if (result.link) {
        target_el.attr("href", result.link);
        target_el.attr("target", "_blank");
        target_el.removeAttr('disabled');
        target_el.parent().show();
      }
      element.val(result.name);
    });
  }

  function cmiLookup(element, source_url, secondary_source, target_el) {
    element.autocomplete({
      source: source_url,
      minLength: 1,
      select: function(event, ui) {
        element.next().val(ui.item.id);
        lookupCMI(element, ui.item.id, secondary_source, target_el);
      }
    }).data("ui-autocomplete")._renderItem = function(ul, item) {
      item.value = item.label;
      return $("<li>")
        .append("<a>" + item.label + "</a>")
        .appendTo(ul);
    };
  }

  