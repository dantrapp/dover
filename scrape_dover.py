"""
Dover Cost Per Hire scraper

Loads the public Airtable shared view, follows Airtable's expanding virtual
scroll range, and exports every visible row to CSV in Airtable order.

Run: ./venv/bin/python scrape_dover.py
"""

import asyncio
import csv

from playwright.async_api import async_playwright

URL = "https://airtable.com/appihGhxZ1B8Zzyun/shrOw2cVwF9bu8roL"
OUTPUT = "dover_cost_per_hire.csv"
HEADERS = [
    "Position",
    "Cost Per Hire",
    "Company Stage",
    "Company Location",
    "Notable Investor(s)",
    "Recruiter Name",
]
SCROLL_SELECTOR = ".levelsScrollElement"
MAX_ITERATIONS = 300
END_STAGNATION_LIMIT = 3

GET_ROWS_JS = r"""
() => Array.from(document.querySelectorAll('[role="row"][aria-rowindex]')).map((row) => ({
  index: Number(row.getAttribute('aria-rowindex')),
  values: Array.from(row.children).map((cell) => cell.innerText.trim()),
}))
"""

GET_META_JS = rf"""
() => {{
  const el = document.querySelector('{SCROLL_SELECTOR}');
  return {{
    top: el.scrollTop,
    height: el.scrollHeight,
    client: el.clientHeight,
  }};
}}
"""


async def scrape():
    rows_by_index = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 1200})

        print(f"Loading {URL}...", flush=True)
        await page.goto(URL, wait_until="networkidle", timeout=120000)

        stagnant_end_hits = 0

        for iteration in range(1, MAX_ITERATIONS + 1):
            meta = await page.evaluate(GET_META_JS)
            visible_rows = await page.evaluate(GET_ROWS_JS)

            for row in visible_rows:
                rows_by_index[row["index"]] = row["values"]

            min_index = min(row["index"] for row in visible_rows)
            max_index = max(row["index"] for row in visible_rows)
            print(
                f"iter={iteration} top={meta['top']} height={meta['height']} "
                f"idx={min_index}-{max_index} collected={len(rows_by_index)}",
                flush=True,
            )

            max_scroll = meta["height"] - meta["client"]
            if meta["top"] >= max_scroll:
                await page.wait_for_timeout(1200)
                refreshed_meta = await page.evaluate(GET_META_JS)
                refreshed_rows = await page.evaluate(GET_ROWS_JS)

                for row in refreshed_rows:
                    rows_by_index[row["index"]] = row["values"]

                refreshed_max_index = max(row["index"] for row in refreshed_rows)
                print(
                    f"  end-check top={refreshed_meta['top']} "
                    f"height={refreshed_meta['height']} bottom_idx={refreshed_max_index} "
                    f"collected={len(rows_by_index)}",
                    flush=True,
                )

                at_end = refreshed_meta["top"] >= (
                    refreshed_meta["height"] - refreshed_meta["client"]
                )
                if refreshed_meta["height"] == meta["height"] and at_end:
                    stagnant_end_hits += 1
                else:
                    stagnant_end_hits = 0

                if stagnant_end_hits >= END_STAGNATION_LIMIT:
                    break

                await page.locator(SCROLL_SELECTOR).hover()
                await page.mouse.wheel(0, meta["client"])
                await page.wait_for_timeout(500)
                continue

            next_top = min(meta["top"] + int(meta["client"] * 0.8), max_scroll)
            await page.evaluate(
                f"(y) => {{ const el = document.querySelector('{SCROLL_SELECTOR}'); el.scrollTop = y; }}",
                next_top,
            )
            await page.wait_for_timeout(250)

        await browser.close()

    if not rows_by_index:
        raise RuntimeError("No rows captured from Airtable.")

    max_index = max(rows_by_index)
    missing = [index for index in range(1, max_index + 1) if index not in rows_by_index]
    if missing:
        raise RuntimeError(
            f"Missing {len(missing)} rows in export; first missing index: {missing[0]}"
        )

    with open(OUTPUT, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(HEADERS)
        for index in range(1, max_index + 1):
            values = rows_by_index[index]
            if len(values) != len(HEADERS):
                raise RuntimeError(
                    f"Row {index} has {len(values)} cells instead of {len(HEADERS)}"
                )
            writer.writerow(values)

    print(f"Saved {max_index} rows to {OUTPUT}", flush=True)


if __name__ == "__main__":
    asyncio.run(scrape())
