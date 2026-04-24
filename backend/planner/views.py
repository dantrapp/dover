import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from planner.services.planner import build_planner_response


@require_GET
def api_root_view(request):
    return JsonResponse(
        {
            "status": "ok",
            "service": "dover-hiring-planner-api",
            "endpoints": ["/api/options/", "/api/planner/"],
        }
    )


@require_GET
def options_view(request):
    return JsonResponse(
        {
            "stages": ["Pre-seed", "Seed", "Series A", "Series B", "Series C+"],
            "functions": [
                "Engineering",
                "GTM",
                "Product",
                "Design",
                "Ops",
                "People",
                "Clinical",
                "Other",
            ],
            "priorities": [
                "Need pipeline",
                "Need process help",
                "Need full-cycle recruiter",
                "Need a specialist search",
                "Not sure",
            ],
            "featuredCities": [
                "San Francisco, CA",
                "New York, NY",
                "Boston, MA",
                "Austin, TX",
                "Remote",
            ],
            "exampleRoles": [
                "Founding engineer",
                "Senior backend engineer",
                "Enterprise account executive",
                "Product designer",
                "Customer success manager",
            ],
        }
    )


@csrf_exempt
@require_POST
def planner_view(request):
    payload = json.loads(request.body or '{}')
    return JsonResponse(build_planner_response(payload))
