from django.shortcuts import render
from django.views.generic.base import View
from rdrf.helpers.registry_features import RegistryFeatures
from rdrf.models.definition.models import Registry


class LandingView(View):
    def get(self, request):
        registry = Registry.objects.first()

        return render(request, 'rdrf_cdes/index.html', {
            "registry": registry,
            "registration_enabled": registry.has_feature(RegistryFeatures.REGISTRATION)
        })
