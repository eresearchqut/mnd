function showElement(selector) {
    selector.css('display', 'block');
    selector.closest('.row').removeClass('d-none');
}

function hideElement(selector) {
    selector.css('display', 'none');
    selector.closest('.row').addClass('d-none');
}

function makeRequired(selector, extraOpFn) {
    selector.attr('required','');
    if (typeof extraOpFn !== 'undefined') {
        extraOpFn(selector);
    }
}

function removeRequired(selector, extraOpFn) {
    selector.removeAttr('required');
    if (typeof extraOpFn !== 'undefined') {
        extraOpFn(selector);
    }
}

function show(selector, extraOpFn) {
    showElement(selector);
    makeRequired(selector, extraOpFn);
}

function hide(selector, extraOpFn) {
    hideElement(selector);
    removeRequired(selector, extraOpFn);
}

function showSelectors(selectors, extraOpFn) {
    for (idx = 0; idx < selectors.length; idx ++) {
        show(selectors[idx], extraOpFn);
    }
}

function hideSelectors(selectors, extraOpFn) {
    for (idx = 0; idx < selectors.length; idx ++) {
        hide(selectors[idx], extraOpFn);
    }
}

