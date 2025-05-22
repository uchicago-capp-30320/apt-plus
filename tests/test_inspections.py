import pytest
from apt_app.views.fetch_inspections import parse_address, _fetch_inspection_summaries
from django.http import JsonResponse
import json

# available = addresses exist and have summaries (for non-trivial violations)
available_addresses = ["5514 S BLACKSTONE AVE", "1401 E 55TH ST"]


# ref: https://docs.pytest.org/en/stable/how-to/fixtures.html#parametrizing-fixtures
@pytest.fixture(params=available_addresses)
def available_response(request, db) -> JsonResponse:
    return _fetch_inspection_summaries(request.param)


def test_available_response_format(available_response):
    """
    Test that the response is in the correct format
    """
    expected_keys = {
        "data_status",
        "summary",
        "note",
        "total_violations_count",
        "total_inspections_count",
        "start_date",
        "summarized_issues",
        "start_date",
    }
    assert available_response.status_code == 200, (
        f"Response status code: {available_response.status_code} is not 200"
    )
    response_content = json.loads(available_response.content)
    assert response_content["data_status"] == "available", (
        f"Response status: {response_content['data_status']} is not 'available'"
    )
    # Check if all expected keys appear in the response
    response_keys = set(response_content.keys())
    assert expected_keys <= response_keys, (
        f"Expected keys {expected_keys - response_keys} are missing in the response"
    )

    # Check if 'summarized_issues' is a list and contains expected structure
    assert isinstance(response_content.get("summarized_issues"), list)
    for occasion in response_content.get("summarized_issues", []):
        assert "date" in occasion, f"Occasion {occasion} does not have a 'date' key"
        assert "issues" in occasion, f"Occasion {occasion} does not have an 'issues' key"
        issues = occasion["issues"]
        assert isinstance(issues, list), f"Occasion {occasion} has a non-list 'issues' key"
        for issue in issues:
            assert "emoji" in issue, (
                f"Occasion {occasion} has an issue {issue} that does not have an 'emoji' key"
            )
            assert "description" in issue, (
                f"Occasion {occasion} has an issue {issue} that does not have a 'description' key"
            )


trivial_only_addresses = ["1451 E 55TH ST"]


@pytest.fixture(params=trivial_only_addresses)
def trivial_only_response(request, db) -> JsonResponse:
    return _fetch_inspection_summaries(request.param)


def test_trivial_only_response_format(trivial_only_response):
    """
    Test that the response is in the correct format
    """
    assert trivial_only_response.status_code == 200, (
        f"Response status code: {trivial_only_response.status_code} is not 200"
    )
    response_content = json.loads(trivial_only_response.content)
    assert response_content["data_status"] == "trivial_only", (
        f"Response status: {response_content['data_status']} is not 'trivial_only'"
    )

    expected_keys = {
        "data_status",
        "note",
        "total_violations_count",
        "total_inspections_count",
        "start_date",
    }
    response_keys = set(response_content.keys())
    assert expected_keys <= response_keys, (
        f"Expected keys {expected_keys - response_keys} are missing in the response"
    )


no_violations_addresses = ["100 N NON EXISTENT ST"]


@pytest.fixture(params=no_violations_addresses)
def no_violations_response(request, db) -> JsonResponse:
    return _fetch_inspection_summaries(request.param)


def test_no_violations_response_format(no_violations_response):
    """
    Test that the response is in the correct format
    """
    assert no_violations_response.status_code == 200, (
        f"Response status code: {no_violations_response.status_code} is not 200"
    )
    response_content = json.loads(no_violations_response.content)
    assert response_content["data_status"] == "no_violations", (
        f"Response status: {response_content['data_status']} is not 'no_violations'"
    )

    expected_keys = {"data_status", "note", "start_date"}
    response_keys = set(response_content.keys())
    assert expected_keys <= response_keys, (
        f"Expected keys {expected_keys - response_keys} are missing in the response"
    )


@pytest.mark.django_db
def test_endpoint_available(client):
    """
    Test that the endpoint is available
    """
    response = client.get("/fetch_inspections/", {"address": "5514 S BLACKSTONE AVE"})
    assert response.status_code == 200, f"Response status code: {response.status_code} is not 200"
