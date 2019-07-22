from mnd.models import PrivateHealthFund
from django.http.response import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def load_private_health_funds(request):

    funds = PrivateHealthFund.objects.all().values('code', 'name')
    result = {
        "funds": [{
            "code": f['code'],
            "name": f['name']
        } for f in funds]
    }
    return JsonResponse(result)
