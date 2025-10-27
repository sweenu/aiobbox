"""Integration test for aiobbox using real Bbox router credentials.

This test requires a real Bbox router and valid credentials.
Set the BBOX_PASSWORD environment variable to run this test.

Example:
    BBOX_PASSWORD=your_password uv run pytest tests/integration.py -v -s
"""

import asyncio
import os

import pytest

from aiobbox import BboxApi, BboxApiError, BboxAuthError


def requires_router_credentials() -> str:
    """Skip test if router credentials are not available."""
    password = os.getenv("BBOX_PASSWORD")
    if not password:
        pytest.skip("BBOX_PASSWORD environment variable not set")
    return password


class TestBboxIntegration:
    """Integration test with real Bbox router."""

    @pytest.mark.asyncio
    async def test_all_endpoints(self) -> None:
        """Test all API endpoints with single authentication to avoid rate limits."""
        password = requires_router_credentials()

        async with BboxApi(password) as api:
            # Test authentication
            assert api._authenticated is True
            print("✅ Successfully authenticated to Bbox router")

            # Test router info
            router_info = await api.get_router_info()
            assert router_info.modelname is not None
            assert router_info.status is not None
            assert router_info.uptime >= 0
            assert router_info.running.version is not None

            print(
                f"✅ Router info: {router_info.modelname} (v{router_info.running.version})"
            )
            print(f"   Status: {'Online' if router_info.status == 1 else 'Offline'}")
            print(f"   Uptime: {router_info.uptime} seconds")

            # Test hosts
            hosts = await api.get_hosts()
            assert isinstance(hosts, list)

            active_hosts = [h for h in hosts if h.active == 1]
            print(
                f"✅ Found {len(active_hosts)} active hosts out of {len(hosts)} total"
            )

            for i, host in enumerate(active_hosts[:5]):  # Show first 5
                print(f"   {i + 1}. {host.hostname or 'Unknown'} ({host.macaddress})")

            # Test WAN stats
            wan_stats = await api.get_wan_ip_stats()
            assert wan_stats.rx.bandwidth >= 0
            assert wan_stats.tx.bandwidth >= 0
            assert int(wan_stats.rx.bytes) >= 0
            assert int(wan_stats.tx.bytes) >= 0

            print("✅ WAN Statistics:")
            print(f"   Download: {wan_stats.rx.bandwidth} Mbps")
            print(f"   Upload: {wan_stats.tx.bandwidth} Mbps")
            print(f"   Download bytes: {wan_stats.rx.bytes}")
            print(f"   Upload bytes: {wan_stats.tx.bytes}")

            print("\n🎉 All endpoints working correctly!")


if __name__ == "__main__":
    """Run integration tests directly for debugging."""
    import sys

    async def main() -> None:
        password = os.getenv("BBOX_PASSWORD")
        if not password:
            print("❌ Please set BBOX_PASSWORD environment variable")
            sys.exit(1)

        print("🔌 Testing Bbox API integration...")

        try:
            # Test authentication
            async with BboxApi(password) as api:
                print("✅ Authentication successful")

                # Test router info
                router_info = await api.get_router_info()
                print(
                    f"✅ Router: {router_info.modelname} (v{router_info.running.version})"
                )

                # Test hosts
                hosts = await api.get_hosts()
                active_hosts = [h for h in hosts if h.active == 1]
                print(f"✅ Active hosts: {len(active_hosts)}")

                # Test WAN stats
                wan_stats = await api.get_wan_ip_stats()
                print(
                    f"✅ Download: {wan_stats.rx.bandwidth} Mbps, Upload: {wan_stats.tx.bandwidth} Mbps"
                )

                print("\n🎉 All integration tests passed!")

        except BboxAuthError as e:
            print(f"❌ Authentication failed: {e}")
            sys.exit(1)
        except BboxApiError as e:
            print(f"❌ API error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            sys.exit(1)

    asyncio.run(main())
