import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.abspath("src"))

from xkcd_mcp import xkcd_api


async def test_search():
    query = "global warming"
    print(f"Searching for: {query}...")
    nums = await xkcd_api.search_explain_xkcd(query)
    print(f"Found comic numbers: {nums}")

    if nums:
        for n in nums[:2]:
            comic = await xkcd_api.fetch_by_number(n)
            if comic.get("success"):
                print(f"✅ #{n}: {comic['comic']['title']}")
            else:
                print(f"❌ #{n}: Error")
    else:
        print("No results found.")


if __name__ == "__main__":
    asyncio.run(test_search())
