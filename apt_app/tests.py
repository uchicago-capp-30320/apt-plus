def test_dry_run():
    """A super simple test to verify the GitHub Actions workflow runs."""
    assert True


def test_server_available():
    """Test that the root URL ('/') responds with HTTP 200."""
    from django.test import Client

    client = Client()
    response = client.get("/")

    assert response.status_code == 200
