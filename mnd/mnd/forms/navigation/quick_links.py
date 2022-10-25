from django.utils.translation import ugettext_lazy as _
from rdrf.forms.navigation.quick_links import (
    RegularMenuConfig, QuickLinks, make_link, make_entries
)


MIMSProductCache = make_link("admin:mnd_mimsproductcache_changelist", _("MIMS Product cache"))
MIMSCMICache = make_link("admin:mnd_mimscmicache_changelist", _("MIMS CMI cache"))


class MNDRegularMenuConfig(RegularMenuConfig):

    def admin_page_links(self):
        ret_val = super().admin_page_links()
        ret_val.update(make_entries(MIMSProductCache, MIMSCMICache))
        return ret_val


class MNDQuickLinks(QuickLinks):

    REGULAR_MENU_CONFIG = MNDRegularMenuConfig
