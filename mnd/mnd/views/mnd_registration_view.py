from rdrf.views.registration_rdrf import RdrfRegistrationView


from ..registry.groups.registration.mnd_registration import MNDCarerRegistration
from ..forms.mnd_registration_form import MNDCarerRegistrationForm


class MNDRegistrationView(RdrfRegistrationView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.form_class = MNDCarerRegistrationForm

    def load_registration_class(self, request, form):
        return MNDCarerRegistration(request, form)

    def dispatch(self, request, *args, **kwargs):
        if request.method == "GET":
            for param, value in request.GET.items():
                self.initial[param] = value
        return super().dispatch(request, *args, **kwargs)