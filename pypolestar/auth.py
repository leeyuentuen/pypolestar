import logging
import json
import httpx

from datetime import datetime, timedelta


from .exceptions import PolestarAuthException

_LOGGER = logging.getLogger(__name__)

CLIENT_ID = "polmystar"


class PolestarAuth:
    """base class for Polestar authentication"""

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self._client_session = client or httpx.AsyncClient()

    async def get_token(self) -> None:
        code = await self._get_code()

        # get token
        params = {
            "query": "query getAuthToken($code: String!) { getAuthToken(code: $code) { id_token access_token refresh_token expires_in }}",
            "operationName": "getAuthToken",
            "variables": json.dumps({"code": code}),
        }

        headers = {"Content-Type": "application/json"}
        result = await self._client_session.get(
            "https://pc-api.polestar.com/eu-north-1/auth/",
            params=params,
            headers=headers,
        )
        if result.status_code != 200:
            _LOGGER.error(f"Error getting token {result.status}")
            raise PolestarAuthException(f"Error getting token")
        resultData = result.json()
        _LOGGER.debug(resultData)

        if resultData["data"]:
            self.access_token = resultData["data"]["getAuthToken"]["access_token"]
            self.refresh_token = resultData["data"]["getAuthToken"]["refresh_token"]
            self.token_expiry = datetime.now() + timedelta(
                seconds=resultData["data"]["getAuthToken"]["expires_in"]
            )
            # ID Token

        _LOGGER.debug(f"Response {self.access_token}")

    async def _get_code(self) -> None:
        # Get Resume Path
        params = {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": "https://www.polestar.com/sign-in-callback",
        }
        result = await self._client_session.get(
            "https://polestarid.eu.polestar.com/as/authorization.oauth2", params=params
        )
        if result.status_code != 303:
            _LOGGER.error(f"Error getting resume path {result.status_code}")
            raise PolestarAuthException(f"Error getting resume_path")

        query_params = result.next_request.url.params

        # check if code is in query_params
        if "code" in query_params:
            return query_params["code"][0]

        # get the resumePath
        if "resumePath" in query_params:
            resumePath = query_params["resumePath"]

        params = {"client_id": CLIENT_ID}
        data = {"pf.username": self.username, "pf.pass": self.password}
        result = await self._client_session.post(
            f"https://polestarid.eu.polestar.com/as/{resumePath}/resume/as/authorization.ping",
            params=params,
            data=data,
        )
        if result.status_code != 302:
            _LOGGER.error(f"Error getting code {result.status_code}")
            raise PolestarAuthException(f"Error getting authorization code")

        return result.next_request.url.params.get("code")
