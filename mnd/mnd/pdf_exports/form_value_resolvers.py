from rdrf.models.definition.models import CommonDataElement
from ..integration.mims.mims_service import mims_product_details


class FormValueResolver:

    def __init__(self, cde_codes):
        self.cdes = CommonDataElement.objects.filter(code__in=cde_codes)
        self.cde_values_mapping = {
            cde.code: cde.pv_group.cde_values_dict for cde in self.cdes.filter(pv_group__isnull=False)
        }
        self.mims_products = {cde.code for cde in self.cdes.filter(widget_name='ProductLookupWidget')}
        self.mims_cmis = {cde.code for cde in self.cdes.filter(widget_name='CMILookupWidget')}

    def resolve(self, code, value):
        if value:
            if code in self.cde_values_mapping and not isinstance(value, list):
                return self.cde_values_mapping[code].get(value, value)
            if code in self.mims_products or code in self.mims_cmis:
                if details := mims_product_details(value):
                    return details.name

        return value
