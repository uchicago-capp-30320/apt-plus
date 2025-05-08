import pytest
from apt_app.views import fetch_inspection_summaries, parse_address


def test_address_parsing():
    assert parse_address("6128 S KIMBARK AVE, CHICAGO, IL, 60637") == "6128 S KIMBARK AVE"
    assert parse_address("6128 S KIMBARK AVE") == "6128 S KIMBARK AVE"
