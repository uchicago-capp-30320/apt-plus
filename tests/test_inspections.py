import pytest
from apt_app.views.fetch_inspections import parse_address, _fetch_inspection_summaries
from scripts.inspections_utils import remove_trailing_code_citation, clean_json_string
from django.http import JsonResponse
import json
import textwrap


def test_parse_address():
    expected_upper = "5514 S BLACKSTONE AVE"
    assert parse_address("5514 S Blackstone Ave") == expected_upper
    assert parse_address(" 5514 S BLACKSTONE ave ") == expected_upper
    assert parse_address("5514 S BLACKSTONE AVE") == expected_upper
    assert parse_address("5514 S Blackstone Ave, Chicago, IL") == expected_upper
    assert parse_address("5514 S Blackstone Ave, Chicago, IL 60615") == expected_upper


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


trivial_only_addresses = ["5300 S HYDE PARK BLVD", "1001 E 53RD ST"]


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
        "summary",
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

    expected_keys = {"data_status", "summary", "start_date"}
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


def test_missing_address_param(client):
    response = client.get("/fetch_inspections/")
    assert response.status_code == 400, f"Response status code: {response.status_code} is not 400"


# ruff: noqa: E501
@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        (
            "Failed to maintain the exterior walls of a building or structure free from holes, breaks, loose or rotting boards or timbers and any other conditions which might admit rain or dampness to the walls.  (13-196-530(b), 13-196-641)",
            "Failed to maintain the exterior walls of a building or structure free from holes, breaks, loose or rotting boards or timbers and any other conditions which might admit rain or dampness to the walls.",
        ),
        (
            "Stop storing garbage and placing refuse containers improperly. (7-28-260)",
            "Stop storing garbage and placing refuse containers improperly.",
        ),
        (
            "Failed to provide porch which is more than two risers high with rails not less than three and one-half feet above the floor of the porch.  (13-196-570(b), 13-196-641",
            "Failed to provide porch which is more than two risers high with rails not less than three and one-half feet above the floor of the porch.",
        ),
        (
            "No codes here at all.",
            "No codes here at all.",
        ),
        (None, ""),
    ],
)
def test_remove_trailing_code_citation(input_text, expected_output):
    assert remove_trailing_code_citation(input_text) == expected_output


@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("""```json\n{\"key\": \"value\"}\n```""", '{"key": "value"}'),
        ('{"key": "value"}', '{"key": "value"}'),  # no need for parsing
        ("""```json\n{\n  \"a\": 1\n}\n```""", '{\n  "a": 1\n}'),
        ("""{\"foo\": \"bar\"}""", '{"foo": "bar"}'),  # no markdown
        ("""```json\n{\"foo\": \"bar\"}\n```\n""", '{"foo": "bar"}'),  # trailing newline
        ("""```json\n{\"foo\": \"bar\"}\n```extra""", '{"foo": "bar"}'),
        (
            """```json\n{\"foo\": \"bar\"}\n```\n\n""",
            '{"foo": "bar"}',
        ),  # multiple trailing newlines
    ],
)
def test_clean_json_string(input_str, expected):
    assert clean_json_string(input_str) == expected
