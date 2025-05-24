from apt_app.models import Violation, InspectionSummary
import datetime
from django.http import JsonResponse, HttpRequest
import logging

# Get a logger for this module
logger = logging.getLogger(__name__)


def parse_address(in_address: str) -> str:
    """fetch the first part of address in uppercase, before "Chicago IL 60XXX"""
    try:
        return in_address.upper().split(",")[0].strip()
    except Exception as e:
        logger.error(f"Error parsing address: {e}")
        return ""


def _fetch_inspection_summaries(address, start_date=datetime.date(2020, 1, 1)) -> JsonResponse:
    """
    Fetch inspection summaries for a given address and cut-off date.

    Args:
        address (str): The address to fetch inspection summaries for.
        start_date (datetime.date): The cut-off date to count the number of inspections and \
            violations. Currently hardcoded to the default of 2020-01-01 for recency.

    ref:
    - https://docs.djangoproject.com/en/5.1/ref/models/class/#doesnotexist
    """

    # TODO: refine error handling
    try:
        if not address:
            return JsonResponse({"error": "Address is required"}, status=400)

        parsed_address = parse_address(address)
        if not parsed_address:
            return JsonResponse({"error": "Invalid address format"}, status=400)

        logger.info(f"Fetching violations for address: {parsed_address}")

        content = {"address": parsed_address, "start_date": start_date}

        violations = (
            Violation.objects.filter(address__istartswith=parsed_address)
            .filter(violation_date__gt=start_date)
            # TODO: need to probably remove or relax this filter -- to be not just complaint
            .filter(inspection_category="COMPLAINT")
        )

        total_violations_count = violations.count()
        total_inspections_count = violations.distinct("inspection_number").count()
        logger.info(
            f"Total violations: {total_violations_count}"
            f"Total inspections: {total_inspections_count}"
        )

        # first case: no violations found
        if total_violations_count == 0:
            content["data_status"] = "no_violations"
            content["summary"] = "no violation record found for this address"
            return JsonResponse(content, status=200)

        content["total_violations_count"] = total_violations_count
        content["total_inspections_count"] = total_inspections_count

        inspection_summary = InspectionSummary.objects.filter(
            address__istartswith=parsed_address
        ).first()  # TODO: need to use time-based sorting later
        summary_json = inspection_summary.summary
        logger.debug(f"Inspection summary JSON: {summary_json}")

        # second case: violations found but considered trivial and thus not summarized
        if not summary_json:
            content["data_status"] = "trivial_only"
            content["summary"] = (
                f"{total_violations_count} trivial violations were recorded on "
                f"{total_inspections_count} occasions and omitted here for brevity."
            )
            return JsonResponse(content, status=200)

        # third case: violations found and summarized
        content = content | summary_json
        content["data_status"] = "available"
        return JsonResponse(content, status=200)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)
