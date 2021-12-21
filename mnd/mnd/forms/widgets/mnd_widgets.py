from django.urls import reverse_lazy

from mnd.integration.mims.mims_service import mims_product_details
from rdrf.forms.widgets.widgets import LookupWidget
from rdrf.helpers.cde_data_types import CDEDataTypes


def _get_product_name(raw_value):
    product = mims_product_details(raw_value)
    return product.name if product else raw_value


class ProductLookupWidget(LookupWidget):
    SOURCE_URL = reverse_lazy('mims_product_search')
    SECONDARY_SOURCE = reverse_lazy('mims_product_details')

    @staticmethod
    def usable_for_types():
        return {CDEDataTypes.LOOKUP}

    @staticmethod
    def denormalized_value(raw_value):
        return _get_product_name(raw_value)

    def render(self, name, value, attrs, renderer=None):
        return """
            <input type="text" name="%s_" id="id_%s" class="skip-serialize"/>
            <input type="hidden" name="%s" id="id_%s_" value="%s"/>
            <div class="product-attributes">
                <label>Active ingredients</label><textarea id="id_%s_ingredients" disabled></textarea>
                <label>Therapeutic classes</label><textarea id="id_%s_mims" disabled> </textarea>
            </div>
            <script type="text/javascript">
                lookupValue($("#id_%s"), '%s', '%s', ['ingredients', 'mims']);
                $("#id_%s").keyup(function() {
                    if (!this.value) {
                        $("[name='%s']").val('');
                    } else {
                        dependentLookup($(this), '%s', '%s', ['ingredients', 'mims']);
                    }
                });
            </script>
        """ % (name, name,
               name, name, value or '',
               name, name,
               name, value or '', self.SECONDARY_SOURCE,
               name,
               name,
               self.SOURCE_URL, self.SECONDARY_SOURCE)


class CMILookupWidget(LookupWidget):
    SOURCE_URL = reverse_lazy('mims_product_search')
    SECONDARY_SOURCE = reverse_lazy('mims_cmi_details')

    @staticmethod
    def usable_for_types():
        return {CDEDataTypes.LOOKUP}

    @staticmethod
    def denormalized_value(raw_value):
        return _get_product_name(raw_value)

    def render(self, name, value, attrs, renderer=None):
        return """
            <input type="text" name="%s_" id="id_%s" class="skip-serialize"/>
            <input type="hidden" name="%s" id="id_%s_" value="%s"/>
            <div style="display:none" id="id_%s_med_info" class="med_info">
            </div>
            <script type="text/javascript">
                (function() {
                    var current = $("#id_%s");
                    var medInfo = $("#id_%s_med_info");
                    lookupCMI(current, '%s', '%s', medInfo);
                    current.keyup(function() {
                        if (!this.value) {
                            $("[name='%s']").val('');
                        } else {
                            cmiLookup($(this), '%s', '%s', $(this).siblings(".med_info"));
                        }
                    });
                })();
            </script>
        """ % (name, name,
               name, name, value or '',
               name,
               name, name,
               value or '', self.SECONDARY_SOURCE,
               name,
               self.SOURCE_URL, self.SECONDARY_SOURCE)
