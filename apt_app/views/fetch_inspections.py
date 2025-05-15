from apt_app.models import Violation, InspectionSummary
import datetime
from django.http import JsonResponse, HttpRequest


def parse_address(in_address):
    """get the part of address that is before "Chicago IL 60XXX"""
    return in_address.split(",")[0].strip()


def _fetch_inspection_summaries(parsed_address):
    # TODO: need to add more error handling, but currently blocked by updating the backend data
    try:
        parsed_address = parse_address(parsed_address)
        cut_off_date = datetime.date(2020, 1, 1)

        violations = (
            Violation.objects.filter(address__istartswith=parsed_address)
            .filter(violation_date__gt=cut_off_date)
            .filter(inspection_category="COMPLAINT")
        )

        total_violations_count = violations.count()
        total_inspections_count = violations.distinct("inspection_number").count()

        inspection_summary = InspectionSummary.objects.filter(
            address__istartswith=parsed_address
        ).first()

        summary_json = inspection_summary.summary
        summary_json["total_violations_count"] = total_violations_count
        summary_json["total_inspections_count"] = total_inspections_count
        summary_json["cut_off_date"] = cut_off_date
        return JsonResponse(summary_json, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
