import logging

from django.contrib import messages
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.translation import ugettext as _

from rdrf.routing.login_router import RouterView

from mnd.models import CarerRegistration

logger = logging.getLogger(__name__)


class MNDRouterView(RouterView):

    def additional_checks(self, request):
        user = request.user
        if not (user.is_authenticated and user.is_patient):
            return
        carer_registration = (
            CarerRegistration.objects.filter(
                status=CarerRegistration.REGISTERED, carer__patient=user.user_object.first()
            ).first()
        )
        if carer_registration:
            primary_carer = carer_registration.carer
            url = reverse('approve_carer_registration')
            msg = _(f"Outstanding carer approval: {primary_carer.first_name} {primary_carer.last_name} - {primary_carer.email}")
            link = _(f"<a href='{url}'> Click here to approve </a>")
            final_msg = f"{msg} {link}"
            messages.info(request, mark_safe(final_msg))
