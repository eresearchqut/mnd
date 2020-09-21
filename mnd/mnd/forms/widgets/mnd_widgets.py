from django.urls import reverse_lazy

from rdrf.forms.widgets.widgets import LookupWidget
from rdrf.helpers.cde_data_types import CDEDataTypes


class ProductLookupWidget(LookupWidget):
    SOURCE_URL = reverse_lazy('mims_product_search')
    SECONDARY_SOURCE = reverse_lazy('mims_product_details')

    @staticmethod
    def usable_for_types():
        return {CDEDataTypes.STRING}

    def render(self, name, value, attrs, renderer=None):
        return """
            <input type="text" name="%s_" id="id_%s"/>
            <input type="hidden" name="%s" id="id_%s_" value="%s"/>
            <div>
                <label>Active ingredients</label><textarea id="id_%s_ingredients" disabled></textarea>
                <label>Mims classes</label><textarea id="id_%s_mims" disabled> </textarea>
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
        return {CDEDataTypes.STRING}

    def render(self, name, value, attrs, renderer=None):
        return """
            <input type="text" name="%s_" id="id_%s"/>
            <input type="hidden" name="%s" id="id_%s_" value="%s"/>
            <div style="display:none">
                <a id="id_%s_link" disabled>Medicine information</a>
            </div>
            <script type="text/javascript">
                lookupCMI($("#id_%s"), '%s', '%s', $("#id_%s_link"));
                $("#id_%s").keyup(function() {
                    if (!this.value) {
                        $("[name='%s']").val('');
                    } else {
                        cmiLookup($(this), '%s', '%s', $("#id_%s_link"));
                    }
                });
            </script>
        """ % (name, name,
               name, name, value or '',
               name,
               name, value or '', self.SECONDARY_SOURCE, name,
               name,
               name, self.SOURCE_URL, self.SECONDARY_SOURCE, name)
