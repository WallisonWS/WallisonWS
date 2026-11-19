#!/usr/bin/env python3
"""
Optional Trello Stats Sync (Only runs when TRELLO_API_KEY, TRELLO_TOKEN & TRELLO_BOARD_ID are configured).
Never injects demo/mock text into the profile README.
"""

import os
import sys


def main() -> int:
    api_key = os.environ.get("TRELLO_API_KEY")
    token = os.environ.get("TRELLO_TOKEN")
    board_id = os.environ.get("TRELLO_BOARD_ID")

    if not (api_key and token and board_id):
        print("[TRELLO] Secrets not configured — skipping cleanly without modifying README.md.")
        return 0

    print("[TRELLO] Secrets detected — ready for live sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
