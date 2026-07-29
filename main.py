import json
import re
from pathlib import Path

import requests

# ==========================================================
# Configuration
# ==========================================================

URL = "https://in.bookmyshow.com/movies/chennai/the-odyssey/buytickets/ET00480917"

COOKIE = "__cf_bm=9y8FpWmhfhXGHT.ckgOzhY1kwbNu0jAQQUhgjTVOkZA-1785309670.1714568-1.0.1.1-jfnlX0Dwbaj1iNJYeHwngZ4kWLbbE0MwoSP95tXEzJOsxH_3ErtjPFqO3iRgxBoZzsAuDUwppw.G5bz4O8WG7SIMBDwJQt9R5azAVipNmPTF72yqPOcvSHgAHL5X81T5; _cfuvid=lh4rRPQQvMY2prWCf21Xq6d8cQGSsUJcJW5DZWgnnPs-1785309670.1714568-1.0.1.1-odAQdTjbXHq89E540mdxy.72quUs67Hg1e4I3zWi5u4"

STATE_FILE = Path("date_state.json")

NTFY_TOPIC = "YOUR_NTFY_TOPIC"

# ==========================================================


def send_ntfy(message: str):
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode(),
        headers={
            "Title": "🎬 BookMyShow",
            "Priority": "5",
            "Tags": "movie",
        },
        timeout=10,
    )


def extract_style(html: str, date: str):
    """
    Finds the class name used for the day number.

    Example matched HTML:

    <div id="20260801"...>
        ...
        <div class="sc-7o7nez-0 gUIrow">01</div>

    Returns:
        gUIrow
    """

    pattern = (
        rf'<div id="202608{date}".*?'
        rf'<div class="sc-7o7nez-0 ([^"]+)">{date}</div>'
    )

    m = re.search(pattern, html, re.DOTALL)

    if not m:
        return None

    return m.group(1)


def load_state():
    if not STATE_FILE.exists():
        return {}

    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def main():
    headers = {
        "Cookie": COOKIE,
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0.0.0 Safari/537.36"
        ),
    }

    response = requests.get(URL, headers=headers, timeout=30)

    html = response.text

    current = {
        "01": extract_style(html, "01"),
        "02": extract_style(html, "02"),
    }

    print("Current:", current)

    previous = load_state()

    if previous:
        for day in ("01", "02"):
            old = previous.get(day)
            new = current.get(day)

            if old != new:
                msg = (
                    f"{day} changed!\n\n"
                    f"{old}  →  {new}"
                )

                print(msg)
                send_ntfy(msg)

    save_state(current)


if __name__ == "__main__":
    main()
