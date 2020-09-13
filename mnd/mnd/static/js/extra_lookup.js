function lookupValue(element, value, secondary_source, suffixes) {
    var full_query = secondary_source + "?product=" + value;
    $.get(full_query, function(result) {
      var query = "[id$='" + suffixes[0] + "']";
      element.parent().find(query).val(result.activeIngredient);
      var query = "[id$='" + suffixes[1] + "']";
      element.parent().find(query).val(result.mims);
      element.val(result.productName);
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
  