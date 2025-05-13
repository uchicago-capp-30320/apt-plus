import pytest
from apt_app.views.inspections import parse_address, fetch_inspection_summaries


def test_address_parsing():
    assert parse_address("6128 S KIMBARK AVE, CHICAGO, IL, 60637") == "6128 S KIMBARK AVE"
    assert parse_address("6128 S KIMBARK AVE") == "6128 S KIMBARK AVE"
