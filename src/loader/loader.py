"""Main entrypoint for the loader."""

from httpx import Client
from letsbuilda.pypi import PyPIServices

from loader.constants import SKIP_AUTH, Settings


def build_authorization_header(access_token: str) -> dict[str, str]:
    """Build authorization headers using the access token."""
    return {"Authorization": "Bearer " + access_token}


def get_access_token(*, http_client: Client) -> str:
    """Get an access token from Auth0."""
    payload = {
        "client_id": Settings.client_id,
        "client_secret": Settings.client_secret,
        "username": Settings.username,
        "password": Settings.password,
        "audience": Settings.audience,
        "grant_type": "password",
    }

    res = http_client.post(f"https://{Settings.auth0_domain}/oauth/token", json=payload)
    res.raise_for_status()
    json = res.json()
    return json["access_token"]  # type: ignore[no-any-return]


def fetch_packages(*, pypi_client: PyPIServices) -> list[tuple[str, str]]:
    """Return a list of name, version tuples in the updated packages RSS feed."""
    packages = pypi_client.get_rss_feed(PyPIServices.PACKAGE_UPDATES_FEED_URL)

    # All packages in the feed are guaranteed to have both a name and version
    return [(package.title, package.version) for package in packages if package.version is not None]


def load_packages(packages: list[tuple[str, str]], *, http_client: Client, access_token: str) -> None:
    """Load all of the given packages into the Dragonfly API, using the given HTTP session and access token."""
    payload = [{"name": name, "version": version} for name, version in packages]
    headers = build_authorization_header(access_token)

    res = http_client.post(f"{Settings.base_url}/batch/package", json=payload, headers=headers)
    res.raise_for_status()


def main(*, http_client: Client, pypi_client: PyPIServices) -> None:
    """Run the loader."""
    access_token = "DEVELOPMENT" if SKIP_AUTH else get_access_token(http_client=http_client)

    packages = fetch_packages(pypi_client=pypi_client)

    load_packages(packages, http_client=http_client, access_token=access_token)
