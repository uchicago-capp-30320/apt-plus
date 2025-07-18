import pytest
from playwright.sync_api import expect, Page

# All tests run using a separate page config on the same browser instance
# as no authentication is needed.
# All tests use pytest-django's live_server object to launch a server.


@pytest.mark.playwright
def test_search_load(page: Page, live_server):
    """
    Home page loads with a visible search bar
    """
    page.goto(live_server.url)
    expect(page.locator("#search-box-bar")).to_be_visible()
    expect(page.locator("#addressInput")).to_be_visible()


@pytest.mark.playwright
def test_text_input(page: Page, live_server):
    """
    Search bar allows text input
    """
    page.goto(live_server.url)
    input = page.locator("#addressInput")
    input.fill("Test search")
    expect(input).to_have_value("Test search")


@pytest.mark.playwright
@pytest.mark.parametrize(
    "input_address, warning, plot",
    [
        ("1606 E Hyde Park Blvd, Chicago, IL 60615", False, True),
        ("233 S Wacker Dr, Chicago, IL 60606", True, True),
        ("1 World Trade Center, New York, NY 10007", True, False),
        ("4231 Fake St, Fake City, 99999", True, False),
    ],
)
def test_search_responses(page: Page, live_server, input_address, warning, plot):
    """
    Test a variety of addresses to show expected responses to search
    """
    page.goto(live_server.url)
    page.locator("#addressInput").fill(input_address)
    page.locator("#searchButton").click()

    # Check error pop-up occurs for errors states
    if warning:
        expect(page.locator("#search-error-message")).to_have_count(1)
    else:
        expect(page.locator("#search-error-message")).to_have_count(0)

    # Check that there's a single plotted address for each point
    if plot:
        expect(page.locator(".map-apt")).to_have_count(1)
    else:
        expect(page.locator(".map-apt")).to_have_count(0)


@pytest.mark.playwright
def test_multiple_search(page: Page, live_server):
    """
    Includes a test that only one element of search is available
    """
    # Search 1
    page.goto(live_server.url)
    page.locator("#addressInput").fill("1606 E Hyde Park Blvd")
    page.locator("#searchButton").click()
    expect(page.locator(".map-apt")).to_have_count(1)

    # Search 2
    page.locator("#addressInput").fill("5432 S Harper Ave")
    page.locator("#searchButton").click()
    expect(page.locator(".map-apt")).to_have_count(1)
