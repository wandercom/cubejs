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
                    "calendars.ts.month": "2023-02-01T00:00:00.000",
                    "calendars.property_name": "Wander Hudson Valley",
                    "calendars.confirmed_booking_revenue": 20000.0,
                },
                {
                    "calendars.ts.month": "2023-01-01T00:00:00.000",
                    "calendars.property_name": "Wander Hudson Valley",
                    "calendars.confirmed_booking_revenue": 10000.0,
                },
            ]
        },
    )

    # act
    output = await get_measures(
        auth=CubeJSAuth(token="token", host="https://host"),
        request=CubeJSRequest(
            measures=["calendars.confirmed_booking_revenue"],
            time_dimensions=[
                TimeDimension(
                    dimension="calendars.ts",
                    granularity="month",
                    date_range="This year",
                )
            ],
            dimensions=["calendars.property_name"],
            segments=["properties.owned"],
            filters=[
                Filter(
                    member="calendars.property_name",
                    operator="startsWith",
                    values=["Wander Hudson"],
                )
            ],
            order={"calendars.confirmed_booking_revenue": "desc"},
        ),
    )

    # assert
    assert output == CubeJSResponse(
        data=[
            {
                "calendars.ts.month": "2023-02-01T00:00:00.000",
                "calendars.property_name": "Wander Hudson Valley",
                "calendars.confirmed_booking_revenue": 20000.0,
            },
            {
                "calendars.ts.month": "2023-01-01T00:00:00.000",
                "calendars.property_name": "Wander Hudson Valley",
                "calendars.confirmed_booking_revenue": 10000.0,
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
