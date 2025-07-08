"""CubeJS client."""

import httpx
import tenacity
from loguru import logger

from cubejs.errors import (
    AuthorizationError,
    BadGatewayError,
    ContinueWaitError,
    RequestError,
    RetryableError,
    ServerError,
    UnexpectedResponseError,
)
from cubejs.model import CubeJSAuth, CubeJSRequest, CubeJSResponse


def _error_handler(response: httpx.Response) -> None:
    """Handle errors from CubeJS server.

    According to CubeJS docs the expected responses are:
        200 - success
        400 - request error
        403 - authorization error
        500 - server error

    Anything other than 200 is unexpected and will raise an error.

    """
    if response.status_code == 403:
        raise AuthorizationError(response.text)
    if response.status_code == 400:
        raise RequestError(response.text)
    if "Continue wait" in response.text:
        raise ContinueWaitError()
    if response.status_code == 502:
        raise BadGatewayError()
    if response.status_code == 500:
        raise ServerError(response.text)
    if response.status_code != 200:
        raise UnexpectedResponseError(response.text)


@tenacity.retry(
    retry=tenacity.retry_if_exception_type(RetryableError),
    wait=tenacity.wait_exponential(multiplier=2, min=1, max=30),
    stop=tenacity.stop_after_attempt(5),
)
async def get_measures(auth: CubeJSAuth, request: CubeJSRequest) -> CubeJSResponse:
    """Get measures from cubejs.

    Args:
        auth: cubejs auth.
        request: definition of measures you want to fetch from the semantic layer.

    Returns:
        cubejs response with requested measures.

    Raises:
        AuthorizationError: if the request is not authorized.
        RequestError: if the request is invalid.
        ContinueWaitError: if the request is not ready yet.
        ServerError: if the server is not available.
        UnexpectedResponseError: if the response is unexpected.

    """
    logger.debug(f"Getting measures from {auth.host}")
    url = f"{auth.host}/cubejs-api/v1/load"
    headers = {"Authorization": auth.token}
    request_payload = {"query": request.model_dump(by_alias=True, exclude_none=True)}
    logger.debug(f"Query payload: {request_payload}")
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url=url, json=request_payload, headers=headers)
        _error_handler(response)
    cube_js_response = CubeJSResponse(**response.json())
    logger.debug("CubeJS response succesfully received!")
    return cube_js_response
