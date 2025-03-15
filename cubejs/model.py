"""Data model."""

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class OrderBy(str, Enum):
    """CubeJS order by available options.

    If the order property is not specified in the query, Cube sorts results by default:
    1. First time dimension with granularity (ascending)
    2. If no time dimension exists, first measure (descending)
    3. If no measure exists, first dimension (ascending)

    The order can be specified either as a dict mapping fields to ASC/DESC,
    or as an array of tuples for controlling the ordering sequence.
    """

    ASC = "asc"
    DESC = "desc"


class Granularity(str, Enum):
    """CubeJS granularity available for time dimensions.

    Time-based properties are modeled using dimensions of the time type. They allow
    grouping the result set by a unit of time (e.g., days, weeks, month, etc.), also
    known as the time dimension granularity.

    The following granularities are available by default for any time dimension
    """

    YEAR = "year"
    QUARTER = "quarter"
    MONTH = "month"
    WEEK = "week"
    DAY = "day"
    HOUR = "hour"
    MINUTE = "minute"
    SECOND = "second"


class FilterOperators(str, Enum):
    """CubeJS available filter operations.

    Different operators are available depending on whether they're applied to measures
    or dimensions, and for dimensions, the available operators depend on the dimension
    type.

    Operators for measures:
    - equals, notEquals: Exact match or its opposite. Supports multiple values.
    - gt, gte, lt, lte: Greater than, greater than or equal, less than,
        less than or equal.
    - set, notSet: Checks if value is not NULL or is NULL respectively.
    - measureFilter: Applies an existing measure's filters to the current query.

    Operators for dimensions (availability depends on dimension type):
    - string: equals, notEquals, contains, notContains, startsWith, notStartsWith,
        endsWith, notEndsWith, set, notSet
    - number: equals, notEquals, gt, gte, lt, lte, set, notSet
    - time: equals, notEquals, inDateRange, notInDateRange, beforeDate, afterDate,
        set, notSet
    """

    EQUALS = "equals"
    NOT_EQUALS = "notEquals"
    CONTAINS = "contains"
    NOT_CONTAINS = "notContains"
    STARTS_WITH = "startsWith"
    NOT_STARTS_WITH = "notStartsWith"
    ENDS_WITH = "endsWith"
    NOT_ENDS_WITH = "notEndsWith"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    SET = "set"
    NOT_SET = "notSet"
    IN_DATE_RANGE = "inDateRange"
    NOT_IN_DATE_RANGE = "notInDateRange"
    BEFORE_DATE = "beforeDate"
    AFTER_DATE = "afterDate"
    MEASURE_FILTER = "measureFilter"


class TimeDimension(BaseModel):
    """Time dimension filters and grouping.

    Provides a convenient shortcut to pass a dimension and filter as a TimeDimension.

    Args:
        dimension: Time dimension name to use for filtering and/or grouping.
        granularity: A granularity for the time dimension. Can be one of the default
            granularities (e.g., year, week, day) or a custom granularity. If not
            provided, Cube will only filter by the time dimension without grouping.
        date_range: Date range for filtering. Can be:
            - An array of dates in YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss.SSS format
            - A single date (equivalent to passing two identical dates)
            - A string with a relative date range (e.g., "last quarter")
            Values should be local and in query timezone. YYYY-MM-DD dates are padded
            to start/end of day when used as range boundaries.
        compare_date_range: An array of date ranges to compare measure values across
            different time periods.
    """

    dimension: str
    granularity: Granularity | None = None
    date_range: list[str] | str | None = Field(
        default=None, serialization_alias="dateRange"
    )
    compare_date_range: list[list[str] | str] | None = Field(
        default=None, serialization_alias="compareDateRange"
    )

    @model_validator(mode="after")
    def validate_date_ranges(self) -> "TimeDimension":
        """Validate date range configurations."""
        if self.date_range is not None and self.compare_date_range is not None:
            raise ValueError("Cannot provide both date_range and compare_date_range")

        if self.compare_date_range is not None:
            for date_range in self.compare_date_range:
                if isinstance(date_range, list) and len(date_range) != 2:
                    raise ValueError(
                        "Each compare_date_range entry must contain exactly 2 "
                        "dates when provided"
                    )

        return self

    class Config:  # noqa: D106
        exclude_none = True
        populate_by_name = True


class Filter(BaseModel):
    """Filter section of a cubejs request.

    Filters can be applied to dimensions or measures:
    - When filtering dimensions, raw data is restricted before calculations
    - When filtering measures, results are restricted after measure calculation

    Args:
        member: Dimension or measure to filter by (e.g., "stories.isDraft").
        operator: Operator to apply to the filter. Available operators depend on
            whether filtering a dimension or measure, and the type of dimension.
            See FilterOperators for available options.
        values: Array of values for the filter. Values must be strings.
            For dates, use YYYY-MM-DD format. Optional for some operators
            like 'set' and 'notSet'.
    """

    member: str
    operator: str
    values: list[str] | None = None


class LogicalOperator(BaseModel):
    """Logical operator for combining filters.

    Allows combining multiple filters with boolean logic. You can use either 'or_' or
    'and_' to create complex filter conditions.

    Note:
        - You cannot mix dimension and measure filters in the same logical operator
        - Dimension filters apply to raw data (WHERE clause in SQL)
        - Measure filters apply to aggregated data (HAVING clause in SQL)

    Args:
        or_: List of filters or other logical operators to combine with OR.
        and_: List of filters or other logical operators to combine with AND.
    """

    or_: list["FilterOrLogical"] | None = Field(default=None, serialization_alias="or")
    and_: list["FilterOrLogical"] | None = Field(
        default=None, serialization_alias="and"
    )

    class Config:  # noqa: D106
        exclude_none = True
        populate_by_name = True


FilterOrLogical = Filter | LogicalOperator


class CubeJSRequest(BaseModel):
    """CubeJS request definition.

    Args:
        measures: list of measures.
        time_dimensions: time dimensions to aggregate measures by.
        dimensions: dimensions to group by.
        segments: segments to filter by.
        filters: other filters to apply (can include logical operators).
        order: order records in response by.
        limit: limit the number of records in response.
        offset: number of records to skip in response.

    """

    measures: list[str] = Field(default_factory=list)
    time_dimensions: list[TimeDimension] | None = Field(
        serialization_alias="timeDimensions", default=None
    )
    dimensions: list[str] | None = None
    segments: list[str] | None = None
    filters: list[FilterOrLogical] = Field(default_factory=list)
    order: dict[str, OrderBy] | None = None
    limit: int | None = None
    offset: int | None = None


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
