import re
from playwright.sync_api import expect, Page

# All tests run using a separate page config on the same browser instance
# as no authentication is needed.
# All tests use pytest-django's live_server object to launch a server.


def test_search_load(page: Page, live_server):
    """
    Home page loads with a visible search bar
    """
    page.goto(live_server.url)
    expect(page.locator("#search-box-bar")).to_be_visible()
    expect(page.locator("#addressInput")).to_be_visible()


def test_text_input(page: Page, live_server):
    """
    Search bar allows text input
    """
    page.goto(live_server.url)
    input = page.locator("#addressInput")
    input.fill("Test search")
    expect(input).to_have_value("Test search")


# def test_search_not_found(page: Page):
# def test_search_not_chicago(page: Page):
# def test_search_not_HP(page: Page):
#    '''
#    '''
#
# def test_multiple_search(page: Page):
#    '''
#    Includes a test that only one element of search is available
#    '''
#
# def test_map_moves(page: Page):
#    '''
#    Tests that map is frozen prior to search and moveable after search
#    '''
