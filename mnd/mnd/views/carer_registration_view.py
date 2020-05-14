import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, reverse
from django.utils.decorators import method_decorator
from django.views import View


from registry.patients.models import Patient

from mnd.primary_carer.carer_state_machine import get_carer_state, get_current_state

from ..models import PrimaryCarer


logger = logging.getLogger(__name__)


class PatientCarerRegistrationView(View):

    def _render(self, request, result):
        if result.message:
            msg_func = messages.success if result.operation_result else messages.warning
            msg_func(request, result.message)
        return render(request, result.template, result.context)

    @method_decorator(login_required)
    def dispatch(self, request):
        if not request.user.is_patient:
            return HttpResponseForbidden()
        patient = request.user.user_object.first()
        primary_carer = PrimaryCarer.get_primary_carer(patient)
        state = get_current_state(primary_carer, patient)
        logger.info(f"State={type(state)}")
        result = state.process_action(request, request.method == 'GET')
        return self._render(request, result)


class CarerOperationsView(View):

    def get(self, request):
        if not request.user.is_carer:
            return HttpResponseForbidden()
        patients = request.user.patients_in_care.all()
        primary_carer = PrimaryCarer.objects.filter(email=request.user.email).first()
        return render(
            request,
            "registration/carer_self_operations.html",
            context={
                "carer": primary_carer,
                "patients": patients
            }
        )

    def post(self, request):
        if not request.user.is_carer:
            return HttpResponseForbidden()
        primary_carer = PrimaryCarer.objects.get(email=request.user.email)
        patient_id = request.POST.get('patient_id', None)
        if patient_id:
            patient = Patient.objects.get(pk=patient_id)
            state = get_carer_state(primary_carer, patient)
            state.process_action(request)
        return HttpResponseRedirect(reverse('patientslisting'))
