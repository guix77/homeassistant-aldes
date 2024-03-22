"""Sample API Client."""
from typing import Dict
from .const import ALDESMode
import aiohttp


class AldesApi:
    """Aldes API client."""

    _API_URL_TOKEN = "https://aldesiotsuite-aldeswebapi.azurewebsites.net/oauth2/token"
    _API_URL_PRODUCTS = "https://aldesiotsuite-aldeswebapi.azurewebsites.net/aldesoc/v5/users/me/products"  # pylint: disable=line-too-long
    _AUTHORIZATION_HEADER_KEY = "Authorization"
    _TOKEN_TYPE = "Bearer"

    def __init__(
        self, username: str, password: str, session: aiohttp.ClientSession
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self._session = session
        self._token = ""

    async def authenticate(self) -> None:
        """Get an access token."""
        data: Dict = {
            "grant_type": "password",
            "username": self._username,
            "password": self._password,
        }

        async with self._session.post(self._API_URL_TOKEN, data=data) as response:
            json = await response.json()
            if response.status == 200:
                self._token = json["access_token"]
            else:
                raise AuthenticationException()

    async def change_mode(
        self, modem, mode: ALDESMode
    ):
        """Change mode."""
        async with await self._request_with_auth_interceptor(
            self._session.post,
            f"{self._API_URL_PRODUCTS}/{modem}/commands",
            json={
                "jsonrpc": "2.0",
                "method": "changeMode",
                "id": 1,
                "params": [
                    mode.value
                ]
            },
        ) as response:
            return await response.json()

    async def fetch_data(self):
        """Fetch data."""
        async with await self._request_with_auth_interceptor(
            self._session.get, self._API_URL_PRODUCTS
        ) as response:
            return await response.json()

    async def set_target_temperature(
        self, modem, thermostat_id, thermostat_name, target_temperature
    ):
        """Set target temperature."""
        async with await self._request_with_auth_interceptor(
            self._session.patch,
            f"{self._API_URL_PRODUCTS}/{modem}/updateThermostats",
            json=[
                {
                    "ThermostatId": thermostat_id,
                    "Name": thermostat_name,
                    "TemperatureSet": int(target_temperature),
                }
            ],
        ) as response:
            return await response.json()

    async def _request_with_auth_interceptor(self, request, url, **kwargs):
        """Provide authentication to request."""
        initial_response = await request(
            url,
            headers={self._AUTHORIZATION_HEADER_KEY: self._build_authorization()},
            **kwargs,
        )
        if initial_response.status == 401:
            initial_response.close()
            await self.authenticate()
            return request(
                url,
                headers={self._AUTHORIZATION_HEADER_KEY: self._build_authorization()},
                **kwargs,
            )
        return initial_response

    def _build_authorization(self) -> str:
        """Build authorization."""
        return f"{self._TOKEN_TYPE} {self._token}"


class AuthenticationException(Exception):
    """Exception"""
