def primary_carer_str(primary_carer):
    if primary_carer:
        return f"{primary_carer.first_name} {primary_carer.last_name} ({primary_carer.email})"
    else:
        return "unset"
