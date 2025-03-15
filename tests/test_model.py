"""Tests for the CubeJS data model."""

import pytest
from pydantic import ValidationError

from cubejs import (
    CubeJSRequest,
    Filter,
    FilterOperators,
    Granularity,
    LogicalOperator,
    OrderBy,
    TimeDimension,
)


class TestTimeDimension:
    """Test suite for TimeDimension model."""

    def test_valid_time_dimension(self):
        """Test creating a valid time dimension."""
        time_dim = TimeDimension(
            dimension="orders.created_at",
            granularity=Granularity.MONTH,
            date_range=["2023-01-01", "2023-12-31"],
        )
        assert time_dim.dimension == "orders.created_at"
        assert time_dim.granularity == Granularity.MONTH
        assert time_dim.date_range == ["2023-01-01", "2023-12-31"]
        assert time_dim.compare_date_range is None

    def test_time_dimension_with_relative_date(self):
        """Test time dimension with relative date string."""
        time_dim = TimeDimension(
            dimension="orders.created_at",
            granularity=Granularity.DAY,
            date_range="last week",
        )
        assert time_dim.date_range == "last week"

    def test_time_dimension_with_compare_date_range(self):
        """Test time dimension with compare date range."""
        time_dim = TimeDimension(
            dimension="orders.created_at",
            granularity=Granularity.MONTH,
            compare_date_range=[
                ["2023-01-01", "2023-03-31"],
                ["2022-01-01", "2022-03-31"],
            ],
        )
        assert time_dim.compare_date_range == [
            ["2023-01-01", "2023-03-31"],
            ["2022-01-01", "2022-03-31"],
        ]
        assert time_dim.date_range is None

    def test_time_dimension_with_mixed_compare_date_range(self):
        """Test time dimension with mixed format compare date range."""
        time_dim = TimeDimension(
            dimension="orders.created_at",
            granularity=Granularity.MONTH,
            compare_date_range=[["2023-01-01", "2023-03-31"], "last quarter"],
        )
        assert time_dim.compare_date_range == [
            ["2023-01-01", "2023-03-31"],
            "last quarter",
        ]

    def test_invalid_both_date_ranges(self):
        """Test that providing both date_range and compare_date_range is an error."""
        with pytest.raises(ValidationError) as exc_info:
            TimeDimension(
                dimension="orders.created_at",
                date_range=["2023-01-01", "2023-12-31"],
                compare_date_range=[["2022-01-01", "2022-12-31"]],
            )
        assert "Cannot provide both date_range and compare_date_range" in str(
            exc_info.value
        )

    def test_invalid_compare_date_range_length(self):
        """Test that compare_date_range entries must have exactly 2 dates when lists."""
        with pytest.raises(ValidationError) as exc_info:
            TimeDimension(
                dimension="orders.created_at",
                compare_date_range=[["2023-01-01", "2023-03-31", "2023-06-30"]],
            )
        assert "Each compare_date_range entry must contain exactly 2 dates" in str(
            exc_info.value
        )


class TestFilter:
    """Test suite for Filter model."""

    def test_equals_filter(self):
        """Test creating an equals filter."""
        filter_obj = Filter(
            member="products.category",
            operator=FilterOperators.EQUALS,
            values=["Electronics"],
        )
        assert filter_obj.member == "products.category"
        assert filter_obj.operator == "equals"
        assert filter_obj.values == ["Electronics"]

    def test_not_equals_filter(self):
        """Test creating a not equals filter."""
        filter_obj = Filter(
            member="products.category",
            operator=FilterOperators.NOT_EQUALS,
            values=["Clothing"],
        )
        assert filter_obj.operator == "notEquals"
        assert filter_obj.values == ["Clothing"]

    def test_contains_filter(self):
        """Test creating a contains filter."""
        filter_obj = Filter(
            member="products.name",
            operator=FilterOperators.CONTAINS,
            values=["iPhone"],
        )
        assert filter_obj.operator == "contains"

    def test_in_date_range_filter(self):
        """Test creating an in date range filter."""
        filter_obj = Filter(
            member="orders.created_at",
            operator=FilterOperators.IN_DATE_RANGE,
            values=["2023-01-01", "2023-12-31"],
        )
        assert filter_obj.operator == "inDateRange"
        assert filter_obj.values == ["2023-01-01", "2023-12-31"]

    def test_set_filter_without_values(self):
        """Test creating a set filter without values."""
        filter_obj = Filter(
            member="products.description",
            operator=FilterOperators.SET,
        )
        assert filter_obj.operator == "set"
        assert filter_obj.values is None


class TestLogicalOperator:
    """Test suite for LogicalOperator model."""

    def test_or_operator(self):
        """Test creating an OR logical operator."""
        logical_op = LogicalOperator(
            or_=[
                Filter(
                    member="products.category",
                    operator=FilterOperators.EQUALS,
                    values=["Electronics"],
                ),
                Filter(
                    member="products.category",
                    operator=FilterOperators.EQUALS,
                    values=["Computers"],
                ),
            ]
        )
        assert len(logical_op.or_) == 2
        assert logical_op.and_ is None

    def test_and_operator(self):
        """Test creating an AND logical operator."""
        logical_op = LogicalOperator(
            and_=[
                Filter(
                    member="products.price",
                    operator=FilterOperators.GREATER_THAN,
                    values=["100"],
                ),
                Filter(
                    member="products.price",
                    operator=FilterOperators.LESS_THAN,
                    values=["500"],
                ),
            ]
        )
        assert len(logical_op.and_) == 2
        assert logical_op.or_ is None

    def test_nested_logical_operators(self):
        """Test nesting logical operators."""
        logical_op = LogicalOperator(
            or_=[
                Filter(
                    member="products.category",
                    operator=FilterOperators.EQUALS,
                    values=["Electronics"],
                ),
                LogicalOperator(
                    and_=[
                        Filter(
                            member="products.price",
                            operator=FilterOperators.GREATER_THAN,
                            values=["100"],
                        ),
                        Filter(
                            member="products.in_stock",
                            operator=FilterOperators.EQUALS,
                            values=["true"],
                        ),
                    ]
                ),
            ]
        )
        assert len(logical_op.or_) == 2
        assert isinstance(logical_op.or_[1], LogicalOperator)
        assert len(logical_op.or_[1].and_) == 2


class TestCubeJSRequest:
    """Test suite for CubeJSRequest model."""

    def test_minimal_request(self):
        """Test creating a minimal request with just measures."""
        request = CubeJSRequest(measures=["orders.count", "orders.total_amount"])
        assert request.measures == ["orders.count", "orders.total_amount"]
        assert request.dimensions is None
        assert request.filters == []
        assert request.time_dimensions is None

    def test_complete_request(self):
        """Test creating a complete request with all fields."""
        request = CubeJSRequest(
            measures=["orders.count", "orders.total_amount"],
            dimensions=["customers.city", "customers.state"],
            time_dimensions=[
                TimeDimension(
                    dimension="orders.created_at",
                    granularity=Granularity.MONTH,
                    date_range=["2023-01-01", "2023-12-31"],
                )
            ],
            filters=[
                Filter(
                    member="orders.status",
                    operator=FilterOperators.EQUALS,
                    values=["completed"],
                ),
                LogicalOperator(
                    or_=[
                        Filter(
                            member="orders.total_amount",
                            operator=FilterOperators.GREATER_THAN,
                            values=["100"],
                        ),
                        Filter(
                            member="orders.items_count",
                            operator=FilterOperators.GREATER_THAN,
                            values=["5"],
                        ),
                    ]
                ),
            ],
            order={"orders.total_amount": OrderBy.DESC},
            limit=100,
            offset=0,
        )

        assert len(request.measures) == 2
        assert len(request.dimensions) == 2
        assert len(request.time_dimensions) == 1
        assert len(request.filters) == 2
        assert request.order == {"orders.total_amount": OrderBy.DESC}
        assert request.limit == 100
        assert request.offset == 0

    def test_request_serialization(self):
        """Test that the request serializes correctly with proper field names."""
        request = CubeJSRequest(
            measures=["orders.count"],
            time_dimensions=[
                TimeDimension(
                    dimension="orders.created_at",
                    granularity=Granularity.MONTH,
                    date_range=["2023-01-01", "2023-12-31"],
                )
            ],
        )

        serialized = request.model_dump(by_alias=True)
        assert "timeDimensions" in serialized
        assert "dateRange" in serialized["timeDimensions"][0]
