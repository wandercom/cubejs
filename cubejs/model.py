"""Data model."""

from pydantic import BaseModel, Field


class TimeDimension(BaseModel):
    """Time dimension section of a cubejs request.

    Args:
        dimension: column name to use as time reference.
        granularity: granularity to transform the timestamp.
        date_range: date range to filter the query.

    """

    dimension: str
    granularity: str | None = None
    date_range: list[str] | str | None = Field(
        default=None, serialization_alias="dateRange"
    )

    class Config:  # noqa: D106
        exclude_none = True
        populate_by_name = True


class Filter(BaseModel):
    """Filter section of a cubejs request.

    Args:
        member: member to filter by.
        operator: operator to apply.
        values: values to filter by.

    """

    member: str
    operator: str
    values: list[str]


class CubeJSRequest(BaseModel):
    """CubeJS request definition.

    Args:
        measures: list of measures.
        time_dimensions: time dimensions to aggregate measures by.
        dimensions: dimensions to group by.
        segments: segments to filter by.
        filters: other filters to apply.
        order: order records in response by.
        limit: limit the number of records in response.

    """

    measures: list[str]
    time_dimensions: list[TimeDimension] | None = Field(
        serialization_alias="timeDimensions", default=None
    )
    dimensions: list[str] | None = None
    segments: list[str] | None = None
    filters: list[Filter] | None = None
    order: dict[str, str] | None = None
    limit: int | None = None


class CubeJSAuth(BaseModel):
    """CubeJS auth configuration.

    Args:
        token: cubejs token.
        host: cubejs cloud host.

    """

    token: str
    host: str


class CubeJSResponse(BaseModel):
    """CubeJS response.

    Args:
        data: cubejs response data as a list of dictionaries.

    """

    data: list[dict[str, str | int | float | None]]
