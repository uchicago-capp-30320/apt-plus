import pytest
from playwright.sync_api import expect, Page


@pytest.fixture(scope="function", autouse=True)
def test_address(page: Page, live_server):
    """
    Fixture to go to the test address to test map functionality. Since the
    map functionality is not mutating the state of the page, can use a single
    fixture to control the search with known parameters.
    """
    page.goto(live_server.url)
    page.locator("#addressInput").fill("1606 E Hyde Park Blvd, Chicago IL 60615")
    page.locator("#searchButton").click()
    yield page


@pytest.mark.parametrize(
    ("button_id", "icon_class"),
    [
        ("#groceriesButton", ".map-grocery"),
        ("#busStopsButton", ".map-busstop"),
    ],
)
def test_display_elements(page: Page, button_id, icon_class):
    """
    Check that there are elements displayed with different colors.
    """
    # Check no displayed icons to start with
    expect(page.locator(icon_class)).to_have_count(0)

    # Click button
    button = page.locator(button_id)
    button.wait_for(state="attached")
    expect(button).not_to_have_class("is-loading")
    button.click()

    # Expect displayed at least 1
    expect(page.locator(icon_class).first).to_be_visible()

    # Turn off visibility
    button.click()
    expect(page.locator(icon_class)).to_have_count(0)


@pytest.mark.parametrize(
    ("button_id", "icon_class", "num_count"),
    [
        ("#groceriesButton", ".map-grocery", 1),
        ("#busStopsButton", ".map-busstop", 7),
    ],
)
def test_correct_num_elements(page: Page, button_id, icon_class, num_count):
    """
    Check the correct number of elements are displayed for the default settings
    """
    # Click button
    button = page.locator(button_id)
    button.wait_for(state="attached")
    expect(button).not_to_have_class("is-loading")
    button.click()

    # Expect displayed at be the correct count for the address.
    expect(page.locator(icon_class)).to_have_count(num_count)


def test_mouse_over(page: Page):
    """
    Check that the pop-up exists and includes expected text
    """
    # Click button
    button = page.locator("#groceriesButton")
    button.wait_for(state="attached")
    expect(button).not_to_have_class("is-loading")
    button.click()

    # Hover over element and expect a pop-up, then text in the pop-up
    target = page.locator(".map-grocery")
    target.hover()
    popup = page.locator(".maplibregl-popup")
    expect(popup).to_be_visible()
    popup_content = page.locator(".maplibregl-popup-content")  # MapLibre stores separately
    expect(popup_content).to_contain_text("Whole Foods Market")


def test_dist_change_works(page: Page):
    """
    Modifies the distances, checks if that works
    """
    # Click button
    button = page.locator("#groceriesButton")
    button.wait_for(state="attached")
    expect(button).not_to_have_class("is-loading")
    button.click()

    # Check the number of elements
    expect(page.locator(".map-grocery")).to_have_count(1)

    # Modify the distance and confirm new set
    distance_selector = page.locator("#distanceFilter")
    distance_selector.select_option("10")
    expect(page.locator(".map-grocery")).to_have_count(2)

    # Select back and confirm original
    distance_selector.select_option("5")
    expect(page.locator(".map-grocery")).to_have_count(1)
