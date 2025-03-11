from unittest.mock import Mock

import pytest

from cubejs import (
    CubeJSAuth,
    CubeJSRequest,
    CubeJSResponse,
    Filter,
    TimeDimension,
    errors,
    get_measures,
)
from cubejs.client import _error_handler


@pytest.mark.asyncio
async def test_get_metrics(httpx_mock):
    # arrange
    httpx_mock.add_response(
        method="POST",
        url="https://host/cubejs-api/v1/load",
        json={
            "data": [
                {
                    "orders.created_at.day": "2023-02-01T00:00:00.000",
                    "orders.status": "completed",
                    "orders.count": 42,
                },
                {
                    "orders.created_at.day": "2023-02-01T00:00:00.000",
                    "orders.status": "processing",
                    "orders.count": 13,
                },
                {
                    "orders.created_at.day": "2023-01-31T00:00:00.000",
                    "orders.status": "completed",
                    "orders.count": 35,
                },
            ]
        },
    )

    # act
    output = await get_measures(
        auth=CubeJSAuth(token="token", host="https://host"),
        request=CubeJSRequest(
            measures=["orders.count"],
            time_dimensions=[
                TimeDimension(
                    dimension="orders.created_at",
                    granularity="day",
                    date_range="last 30 days",
                )
            ],
            dimensions=["orders.status"],
            filters=[
                Filter(
                    member="orders.status",
                    operator="equals",
                    values=["completed", "processing"],
                )
            ],
            order={"orders.count": "desc"},
        ),
    )

    # assert
    assert output == CubeJSResponse(
        data=[
            {
                "orders.created_at.day": "2023-02-01T00:00:00.000",
                "orders.status": "completed",
                "orders.count": 42,
            },
            {
                "orders.created_at.day": "2023-02-01T00:00:00.000",
                "orders.status": "processing",
                "orders.count": 13,
            },
            {
                "orders.created_at.day": "2023-01-31T00:00:00.000",
                "orders.status": "completed",
                "orders.count": 35,
            },
        ]
    )


def test_error_handler():
    # act
    with pytest.raises(errors.AuthorizationError) as auth_error:
        _error_handler(Mock(status_code=403, text=""))

    with pytest.raises(errors.RequestError) as request_error:
        _error_handler(Mock(status_code=400, text=""))

    with pytest.raises(errors.ContinueWaitError) as continue_wait_error:
        _error_handler(Mock(status_code=200, text="Continue wait"))

    with pytest.raises(errors.ServerError) as server_error:
        _error_handler(Mock(status_code=500, text=""))

    with pytest.raises(errors.UnexpectedResponseError) as unexpected_response_error:
        _error_handler(Mock(status_code=201, text=""))

    # assert
    assert str(auth_error.value) == "CubeJS authorization error: "
    assert str(request_error.value) == "CubeJS 400 request error: "
    assert (
        str(continue_wait_error.value)
        == "CubeJS query is not ready yet, continue waiting..."
    )
    assert str(server_error.value) == "CubeJS server error: "
    assert str(unexpected_response_error.value) == "CubeJS unexpected response: "
