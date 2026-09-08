"""
Populate the `category` column in menu_items using the categorize() function.

Usage:
    python scripts/update_categories.py            # apply updates
    python scripts/update_categories.py --dry-run  # show distribution, no writes

Idempotent: safe to re-run. Always recomputes all rows from dish_name.
"""
# Add project root to path so 'restaurant_scraper' is importable
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
from collections import Counter

from sqlalchemy.orm import sessionmaker

from restaurant_scraper.database.connection import engine
from restaurant_scraper.database.models import MenuItem
from restaurant_scraper.categorization import categorize


def main(dry_run: bool = False) -> None:
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        items = session.query(MenuItem).all()
        total = len(items)
        print(f"Loaded {total} menu items from database")

        counter = Counter()
        changed = 0
        for item in items:
            new_cat = categorize(item.dish_name)
            counter[new_cat] += 1
            if item.category != new_cat:
                if not dry_run:
                    item.category = new_cat
                changed += 1

        print("\n=== Distribution ===")
        for cat, n in counter.most_common():
            pct = 100.0 * n / total if total else 0.0
            print(f"  {cat:12s}  {n:5d}  ({pct:5.1f}%)")

        altro_pct = 100.0 * counter.get("Altro", 0) / total if total else 0.0
        print(f"\nRows to change: {changed} / {total}")
        print(f"'Altro' coverage: {altro_pct:.1f}%")

        if dry_run:
            print("\n[DRY RUN] no changes committed.")
            return

        session.commit()
        print("\n✅ Changes committed to database!")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update menu_items.category")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would change without writing to DB"
    )
    args = parser.parse_args()
    main(dry_run=args.dry_run)
