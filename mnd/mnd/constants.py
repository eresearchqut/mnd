from django.utils.translation import gettext as _


CONTACT_METHOD_CHOICES = [
    ('', _("Preferred contact method")),
    ('phone', _("Phone")),
    ('sms', _("SMS")),
    ('person', _("Nominated person below")),
    ('email', _("Email")),
]


PLAN_MANAGER_CHOICES = [
    ('', _("NDIS Plan Manager")),
    ('self', _("Self")),
    ('agency', _("Agency")),
    ('other', _("Other")),
]

PRIMARY_CARER_RELATIONS = [
    ('', _("Primary carer relationship")),
    ('spouse', _("Spouse")),
    ('child', _("Child")),
    ('sibling', _("Sibling")),
    ('friend', _("Friend")),
    ('other', _("Other(specify)")),
]

