import pytest
from playwright.sync_api import expect, Page


def test_authenticated_fixture(authenticated):
    """
    Checks that the authenticated ficture is working
    """
    expect(authenticated.locator("#nav-log-off"))


# def test_log_in(page: Page, live_server):
#    '''
#    Runs through the log-in
#    '''
#    page.goto(live_server.url)
#    page.wait_for_load_state()
#
#    # Submit request
#    if page.locator("#djHideToolBarButton"):
#        page.locator("#djHideToolBarButton").click()
#    page.locator("#nav-log-in").click()
#    page.wait_for_load_state()
#    page.locator("#id_login").fill("test_email@aptpl.us")
#    page.locator("#id_remember").click() # Select remember me to save cookie
#    page.get_by_role("button", name="Sign In").click()
#
#    # Grab verification code and complete
#    page.wait_for_load_state()
#    code = get_verification_code_from_email()
#    page.locator("#id_code").fill(code)
#    page.get_by_role("button", name="Confirm").click()
#
#    # Save cookies after redirect completed
#    page.wait_for_load_state()
#    expect(page.locator("#nav-log-off"))
#
## Log-in through gmail
## Failed log-in
## Logout
## Updated bar
## Can't access authenticated page while not logged in
