import datetime
import logging

from rdrf.models.definition.models import CommonDataElement
from .dynamic_data_mapping import generate_pdf_field_mappings

logger = logging.getLogger(__name__)


def _get_form_values(dyn_data):
    form_values = {}
    for form_dict in dyn_data["forms"]:
        for section_dict in form_dict["sections"]:
            section_code = section_dict["code"]
            if not section_dict["allow_multiple"]:
                for cde_dict in section_dict["cdes"]:
                    cde_code = cde_dict["code"]
                    form_values[(section_code, cde_code, 0)] = cde_dict["value"]
            else:
                items = section_dict["cdes"]
                for idx, section in enumerate(items):
                    for cde_dict in section:
                        cde_code = cde_dict["code"]
                        form_values[(section_code, cde_code, idx + 1)] = cde_dict["value"]
    return form_values


def generate_dynamic_data_fields(registry, patient):
    form_values = {}
    max_ts = None
    for context_model in patient.context_models:
        dyn_data = patient.get_dynamic_data(registry, context_id=context_model.id)
        if not dyn_data:
            continue
        form_ts = dyn_data.get("timestamp", None)
        if form_ts:
            as_dt = datetime.datetime.strptime(form_ts[:10], '%Y-%m-%d')
            if not max_ts:
                max_ts = as_dt
            elif as_dt > max_ts:
                max_ts = as_dt
        form_values.update(_get_form_values(dyn_data))

    cde_codes = [code for (__, code, __) in form_values.keys()]
    with_pv_groups = CommonDataElement.objects.filter(code__in=cde_codes, pv_group__isnull=False)
    cde_values_mapping = {
        cde.code: cde.pv_group.cde_values_dict for cde in with_pv_groups
    }

    updated_form_values = {}
    for key, value in form_values.items():
        section, code, section_index = key
        if code in cde_values_mapping and value:
            if not isinstance(value, list):
                updated_form_values[(section, code, section_index)] = cde_values_mapping[code].get(value, value)

    form_values.update(updated_form_values)

    data = generate_pdf_field_mappings(form_values)
    if max_ts:
        data["date_updated_af_date"] = max_ts.strftime("%d/%m/%Y")
    return data
