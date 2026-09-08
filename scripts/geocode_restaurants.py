"""
Geocode restaurant addresses using Nominatim (OpenStreetMap)
and update PostgreSQL with latitude/longitude coordinates.
"""

import time
import psycopg2
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# ── Setup geocoder ─────────────────────────────────────────
geolocator = Nominatim(user_agent="catania_restaurant_analysis")
# Nominatim richiede max 1 richiesta al secondo
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.1)


def get_restaurants_without_coords(conn):
    """Prende i ristoranti con indirizzo ma senza coordinate."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, name, address 
            FROM restaurants 
            WHERE address IS NOT NULL 
              AND address != ''
              AND (latitude IS NULL OR longitude IS NULL)
            ORDER BY id
        """)
        return cur.fetchall()


def update_coords(conn, restaurant_id, lat, lng):
    """Aggiorna le coordinate di un ristorante."""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE restaurants 
            SET latitude = %s, longitude = %s, updated_at = NOW()
            WHERE id = %s
        """, (lat, lng, restaurant_id))
    conn.commit()


def geocode_address(address, name):
    """
    Tenta il geocoding in 3 modi:
    1. Indirizzo completo
    2. Indirizzo + "Catania Italy" (se non già presente)
    3. Nome ristorante + "Catania Italy"
    """
    queries = [
        address,
        f"{address}, Catania, Italy",
        f"{name}, Catania, Italy",
    ]

    for query in queries:
        try:
            location = geocode(query)
            if location:
                return location.latitude, location.longitude, query
        except Exception as e:
            print(f"  ⚠️  Errore geocoding '{query}': {e}")
            time.sleep(2)  # Pausa extra in caso di errore

    return None, None, None


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    restaurants = get_restaurants_without_coords(conn)

    total = len(restaurants)
    found = 0
    not_found = []

    print(f"\n🔍 {total} ristoranti da geocodificare\n")

    for i, (rid, name, address) in enumerate(restaurants, 1):
        print(f"[{i}/{total}] {name}")
        print(f"  📍 {address}")

        lat, lng, matched_query = geocode_address(address, name)

        if lat and lng:
            update_coords(conn, rid, lat, lng)
            found += 1
            print(f"  ✅ {lat:.6f}, {lng:.6f}")
        else:
            not_found.append((rid, name, address))
            print(f"  ❌ Non trovato")

        print()

    # ── Riepilogo ──────────────────────────────────────────
    print("=" * 50)
    print(f"✅ Geocodificati: {found}/{total}")
    print(f"❌ Non trovati:   {len(not_found)}/{total}")

    if not_found:
        print(f"\nRistoranti senza coordinate:")
        for rid, name, address in not_found:
            print(f"  - [{rid}] {name} | {address}")

    conn.close()


if __name__ == "__main__":
    main()