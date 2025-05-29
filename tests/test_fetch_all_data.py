import pytest
from apt_app.views.fetch_all_data import (
    _fetch_all_data,
    match_address_in_chicago,
    coordinates_in_hyde_park,
)
from django.http import JsonResponse
import json

# address inside hyde park area
inside_hyde_park_lst = ["5514 S BLACKSTONE AVE", "1401 E 55TH ST"]


@pytest.fixture(params=inside_hyde_park_lst)
def address_inside_hyde_park(request, db) -> JsonResponse:
    return _fetch_all_data(request.param)


def test_address_inside_hyde_park(address_inside_hyde_park):
    """
    Test that the response of the endpoint is a 200 for an address inside Hyde Park.
    """
    assert address_inside_hyde_park.status_code == 200, (
        f"Response status code: {address_inside_hyde_park.status_code} is not 200"
    )
    response_content = json.loads(address_inside_hyde_park.content)
    assert response_content["has_data_inside_hyde_park"] is True, (
        f"Response status: {response_content['has_data_inside_hyde_park']} is not 'True'"
    )


# address inside chicago but not in hyde park
inside_chicago_not_hyde_park_lst = ["211 W Wacker Dr, Chicago, IL 60606"]


@pytest.fixture(params=inside_chicago_not_hyde_park_lst)
def address_inside_chicago(request, db) -> JsonResponse:
    return _fetch_all_data(request.param)


def test_address_inside_chicago(address_inside_chicago):
    """
    Test that the response of the endpoint is a 200 for an address inside
    Chicago but not inside Hyde Park.
    """
    assert address_inside_chicago.status_code == 200, (
        f"Response status code: {address_inside_chicago.status_code} is not 200"
    )
    response_content = json.loads(address_inside_chicago.content)
    assert response_content["has_data_inside_hyde_park"] is False, (
        f"Response status: {response_content['has_data_inside_hyde_park']} is not 'False'"
    )


# address inside IL but not in chicago
inside_illinois_not_chicago_lst = ["1010 E Edwards St, Springfield, IL 62703"]


@pytest.fixture(params=inside_illinois_not_chicago_lst)
def address_outside_chicago(request, db) -> JsonResponse:
    return _fetch_all_data(request.param)


def test_address_outside_chicago(address_outside_chicago):
    """
    Test that the response of the endpoint is a 400 for an address outside Chicago.
    """
    assert address_outside_chicago.status_code == 400, (
        f"Response status code: {address_outside_chicago.status_code} is not 400"
    )


FULL_MATCHED_ADDRESSES = [
    "5496 S HYDE PARK BLVD, CHICAGO, IL, 60615",
    "5514 S BLACKSTONE AVE, CHICAGO, IL, 60637",
]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "input_address, expected_address",
    [
        ("5496 S Hyde Park Blvd", FULL_MATCHED_ADDRESSES[0]),
        ("5496 South Hyde Park Blvd", FULL_MATCHED_ADDRESSES[0]),
        ("5496 South Hyde Park Boulevard", FULL_MATCHED_ADDRESSES[0]),
        ("5496 SOUTH HYDE PARK BLVD", FULL_MATCHED_ADDRESSES[0]),
        ("5514 s blackstone ave", FULL_MATCHED_ADDRESSES[1]),
        ("5514 S BLACKSTONE AVE", FULL_MATCHED_ADDRESSES[1]),
        ("5514 South Blackstone", FULL_MATCHED_ADDRESSES[1]),
        ("5514 South Blackstone Ave", FULL_MATCHED_ADDRESSES[1]),
        ("5514 South Blackstone Avenue", FULL_MATCHED_ADDRESSES[1]),
        ("5514 South Blackstone Avenue, Chicago", FULL_MATCHED_ADDRESSES[1]),
        ("5514 South Blackstone Avenue, Chicago, IL", FULL_MATCHED_ADDRESSES[1]),
        ("5514 South Blackstone Avenue, Chicago, IL, 60637", FULL_MATCHED_ADDRESSES[1]),
    ],
)
def test_match_address_in_chicago(input_address, expected_address):
    """
    Test that match_address_in_chicago() function is working properly.
    """
    matched_address, _, _ = match_address_in_chicago(input_address)
    assert matched_address == expected_address, "Address matching not succesful"


@pytest.mark.django_db
def test_coordinates_in_hyde_park():
    """
    Test that coordinates_in_hyde_park() function is working properly with
    coordinates inside hyde park.
    """
    returned_boolean = coordinates_in_hyde_park(41.79564852022823, -87.59599417834892)
    assert returned_boolean is True, "Address is inside hyde park but is not being recognized"


@pytest.mark.django_db
def test_coordinates_not_in_hyde_park():
    """
    Test that coordinates_in_hyde_park() function is working properly with
    coordinates outside hyde park (coordinates from Downtown Chicago).
    """
    returned_boolean = coordinates_in_hyde_park(41.88012315082984, -87.6299403280742)
    assert returned_boolean is False, "Address is outside hyde park but is not being recognized"


@pytest.mark.django_db
def test_endpoint_available(client):
    """
    Test that the endpoint is available
    """
    response = client.get("/fetch_all_data/", {"address": "5496 S Hyde Park Blvd"})
    assert response.status_code == 200, f"Response status code: {response.status_code} is not 200"
