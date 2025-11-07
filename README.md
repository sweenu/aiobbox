[![codecov](https://codecov.io/github/sweenu/aiobbox/graph/badge.svg?token=K18JVQX6I4)](https://codecov.io/github/sweenu/aiobbox)

# aiobbox

Async Python API wrapper for Bouygues Telecom routers.

Tested with model F@st5696b, firmware version 25.5.28.

## Usage

- Supports the following Bbox API endpoints:
  - `/login` - Authentication
  - `/device` - Device information
  - `/hosts` - Connected devices
  - `/wan/ip/stats` - WAN statistics

```python
import asyncio
from aiobbox import BboxApi

async def main():
    async with BboxApi("your_password") as bbox:
        # Get router's information
        router = await bbox.get_router_info()
        print(f"Router model: {router.modelname}")

        # Get connected hosts
        hosts = await bbox.get_hosts()
        print(f"Connected hosts: {len(hosts)}")

        # Get WAN statistics
        wan_stats = await bbox.get_wan_ip_stats()
        print(f"Download: {wan_stats.rx.bandwidth} Mbps")
        print(f"Upload: {wan_stats.tx.bandwidth} Mbps")

asyncio.run(main())
```

## Development

```bash
# Install dependencies and set up development environment
uv sync --dev

# Run tests
uv run pytest

# Run linting and formating
uv run pre-commit run --all-files

# Run integration tests
BBOX_PASSWORD=your_password uv run pytest tests/integration.py -vvs --no-cov
```
