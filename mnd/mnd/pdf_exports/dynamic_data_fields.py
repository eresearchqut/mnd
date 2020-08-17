import logging

from rdrf.models.definition.models import CommonDataElement
from .dynamic_data_mapping import field_mappings, values_mapping_cdes, checkbox_mapping_cdes

logger = logging.getLogger(__name__)


def _get_form_values(dyn_data):
    form_values = {}
    for form_dict in dyn_data["forms"]:
        form_name = form_dict["name"]
        for section_dict in form_dict["sections"]:
            section_code = section_dict["code"]
            if not section_dict["allow_multiple"]:
                for cde_dict in section_dict["cdes"]:
                    cde_code = cde_dict["code"]
                    form_values[(form_name, section_code, cde_code)] = cde_dict["value"]
            else:
                items = section_dict["cdes"]
                for cde_dict in items[0]:  # first section from multiple forms
                    cde_code = cde_dict["code"]
                    form_values[(form_name, section_code, cde_code)] = cde_dict["value"]
    return form_values


def generate_dynamic_data_fields(registry, patient):
    data = {}
    form_values = {}
    for context_model in patient.context_models:
        dyn_data = patient.get_dynamic_data(registry, context_id=context_model.id)
        if not dyn_data:
            continue
        form_values.update(_get_form_values(dyn_data))
    cde_codes = [code for (__, __, code) in form_values.keys()]
    with_pv_groups = CommonDataElement.objects.filter(code__in=cde_codes, pv_group__isnull=False)
    cde_values_mapping = {
        cde.code: cde.pv_group.cde_values_dict for cde in with_pv_groups
    }
    updated_form_values = {}
    for key, value in form_values.items():
        form, section, code = key
        if code in cde_values_mapping and value:
            if not isinstance(value, list):
                updated_form_values[(form, section, code)] = cde_values_mapping[code].get(value, value)
    form_values.update(updated_form_values)

    logger.info(f"form values= {form_values}")

    for key, field in field_mappings.items():
        __, __, cde_code = key
        if cde_code in values_mapping_cdes:
            mapping_func = values_mapping_cdes[cde_code]
            data[field] = mapping_func(form_values[key])
        elif cde_code in checkbox_mapping_cdes:
            value = form_values[key]
            mappings = checkbox_mapping_cdes[cde_code]
            if isinstance(value, list):
                for v in value:
                    if v in mappings:
                        data[mappings[v]] = "Yes"
            else:
                if value in mappings:
                    data[mappings[value]] = "Yes"
        else:
            data[field] = form_values[key]

    return data
