from apt_app.models import Violation, InspectionSummary
import datetime
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_GET


def parse_address(in_address):
    # get the part of address that is before "Chicago IL 60XXX"
    return in_address.split(",")[0].strip()


@require_GET
def fetch_inspection_summaries(request: HttpRequest) -> JsonResponse:
    try:
        in_address = request.GET.get("address", "")

        in_address = parse_address(in_address)
        cut_off_date = datetime.date(2020, 1, 1)

        violations = (
            Violation.objects.filter(address__istartswith=in_address)
            .filter(violation_date__gt=cut_off_date)
            .filter(inspection_category="COMPLAINT")
        )

        total_violations_count = violations.count()
        total_inspections_count = violations.distinct("inspection_number").count()

        inspection_summary = InspectionSummary.objects.filter(
            address__istartswith=in_address
        ).first()

        summary_json = inspection_summary.summary
        summary_json["total_violations_count"] = total_violations_count
        summary_json["total_inspections_count"] = total_inspections_count
        summary_json["cut_off_date"] = cut_off_date
    except Exception:
        summary_json = {}

    return JsonResponse(summary_json)
