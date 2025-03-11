# cubejs
An unofficial async Python client for Cube, making it easy to integrate your Python
applications with Cube's semantic layer.

## What is Cube?

[CubeJS](https://github.com/cube-js/cube) is an open-source analytics API platform that 
enables data engineers and application developers to build consistent, accessible, and 
secure data applications. It serves as a semantic layer between your data sources and 
applications, providing a unified API for data access.

## What is a Semantic Layer?

A semantic layer is an abstraction that sits between you data warehouse and your 
analytical consumers. It:
- Translates complex data structures into an easy API endpoints
- Ensures consistent business metrics and KPIs across all applications, vizualizations,
  and tools
- Centralizes data access controls and security policies
- Optimizes queries for performance

## Installation

```bash
pip install "git+https://github.com/wandercom/cubejs.git"
```

## Usage

### Basic Query Example

```python
import asyncio
import cubejs
from loguru import logger

async def main() -> None:
    # Define the query using the request model
    request = cubejs.CubeJSRequest(
        measures=["orders.count"],
        dimensions=["orders.status"],
        time_dimensions=[
            cubejs.TimeDimension(
                dimension="orders.created_at",
                date_range="last 30 days",
                granularity="day"
            )
        ],
        limit=100
    )

    # Execute the query and get results
    response = await cubejs.get_measures(
        auth=cubejs.CubeJSAuth(
            token="your-api-token",
            host="https://your-cube-instance.example.com"
        ),
        request=request
    )
    
    logger.info(f"Query Results: {response}")

if __name__ == "__main__":
    asyncio.run(main())

```

## Client features
- [pydantic](https://github.com/pydantic/pydantic) model types defined by the CubeJS API
- [tenacity](https://github.com/jd/tenacity) handles retries and exponential backoff for 
server instability and continue wait errors.
- Async requests for performance

## About Wander
This client is maintained by [Wander](https://wander.com), a company revolutionizing how
people experience travel and discover accommodations.

### How Wander Uses a Semantic Layer
At Wander, we use a semantic layer to:
- Centralize business metrics meaning and definition in a single repository
- Dashboards, ML services, data pipelines and operational tools, both internal and 
  client-facing, all access a single source of truth from our semantic layer.
- Our data warehouse becomes a technical detail so we can focus on building great 
  products.

## License
MIT

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
