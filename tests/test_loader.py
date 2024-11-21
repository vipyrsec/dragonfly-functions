"""Stub test file."""

from dataclasses import dataclass
from unittest.mock import Mock

import pytest

from loader import loader
from loader.constants import Settings


@dataclass
class MockPackage:
    """Mock package data."""

    title: str
    version: str


ENV = {
    "BASE_URL": "https://example.com",
    "AUTH0_DOMAIN": "example-auth.com",
    "USERNAME": "test username",
    "PASSWORD": "test password",
    "CLIENT_ID": "test client id",
    "CLIENT_SECRET": "test client secret",
    "AUDIENCE": "test audience",
}


@pytest.fixture(autouse=True)
def mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock the environment variables."""
    for k, v in ENV.items():
        monkeypatch.setattr(Settings, k.lower(), v)


def test_build_authorization_header() -> None:
    """Test that building authorization header works properly."""
    expected = {"Authorization": "Bearer token"}
    actual = loader.build_authorization_header("token")

    assert expected == actual


def test_get_access_token() -> None:
    """Test that getting access token works properly."""
    json_return_mock = {"access_token": "abc"}
    attrs = {"post.return_value.json.return_value": json_return_mock}
    mock_client = Mock(**attrs)
    access_token = loader.get_access_token(http_client=mock_client)

    expected_url = f"https://{ENV['AUTH0_DOMAIN']}/oauth/token"
    expected_payload = {
        "client_id": ENV["CLIENT_ID"],
        "client_secret": ENV["CLIENT_SECRET"],
        "username": ENV["USERNAME"],
        "password": ENV["PASSWORD"],
        "audience": ENV["AUDIENCE"],
        "grant_type": "password",
    }

    mock_client.post.assert_called_with(expected_url, json=expected_payload)
    assert access_token == "abc"


def test_fetch_packages() -> None:
    """Test that getting packages from the RSS feed works properly."""
    mock_packages = [
        MockPackage(title="a", version="1.0.0"),
        MockPackage(title="b", version="1.0.1"),
    ]
    attrs = {"get_rss_feed.return_value": mock_packages}
    mock_pypi_client = Mock(**attrs)

    actual = loader.fetch_packages(pypi_client=mock_pypi_client)
    expected = [("a", "1.0.0"), ("b", "1.0.1")]

    assert actual == expected


def test_load_packages() -> None:
    """Test that loading packages into the Dragonfly API works properly."""
    mock_client = Mock()
    mock_client.post = Mock()
    mock_packages = [
        ("a", "1.0.0"),
        ("b", "1.0.1"),
    ]

    loader.load_packages(mock_packages, http_client=mock_client, access_token="test access token")

    expected_payload = [{"name": name, "version": version} for name, version in mock_packages]
    expected_headers = {"Authorization": "Bearer test access token"}
    mock_client.post.assert_called_once_with(
        f"{ENV['BASE_URL']}/batch/package",
        json=expected_payload,
        headers=expected_headers,
    )


def test_main(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that everything works together."""
    mock_packages = [
        ("a", "1.0.0"),
        ("b", "1.0.1"),
    ]

    mock_http_client = Mock()
    mock_pypi_client = Mock()

    fetch_packages_mock = Mock(return_value=mock_packages)
    load_packages_mock = Mock()
    monkeypatch.setattr("loader.loader.fetch_packages", fetch_packages_mock)
    monkeypatch.setattr("loader.loader.load_packages", load_packages_mock)

    loader.main(http_client=mock_http_client, pypi_client=mock_pypi_client)
    fetch_packages_mock.assert_any_call(pypi_client=mock_pypi_client)
    load_packages_mock.assert_any_call(mock_packages, http_client=mock_http_client, access_token="DEVELOPMENT")
