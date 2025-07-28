# Testing Document (WIP)
This doc is a WIP for collecting design choices and references used for setting up the testing framework.

https://nektosact.com/usage/index.html?highlight=secrets#secrets


## Playwright
**Set-up Examples**
https://github.com/Chris-May/django_playwright_pytest_example
https://github.com/AutomationPanda/playwright-python-tutorial/tree/main

**Docs**
https://betterstack.com/community/guides/testing/playwright-python-intro/
https://playwrightqa.blogspot.com/2024/10/how-to-automate-single-page.html

**Authentication**
https://playwright.dev/python/docs/auth
https://lewi.dev/blog/basic-http-auth-playwright/
https://medium.com/@anubhavsanyal/efficient-testing-playwrights-authentication-solution-ee858302e6b1
https://www.checklyhq.com/learn/playwright/authentication/

**To-do**
test_bus_routes -> add in bus_routes fixtures
test_bus_stops -> add in bus_stops fixtures (for frontend hits to that one)
test_frontend_map_display -> add in groceries / routes / bus stops / inspections(?) as fixtures
test_inspections -> add in inspections to fixtures
refactor: standardize what's being tested?
