# 🍽️ Catania Restaurant Market Analysis

End-to-end market intelligence pipeline for Catania's restaurant sector — from automated web scraping to an interactive Power BI dashboard.

**[Live Dashboard →](https://app.powerbi.com/view?r=eyJrIjoiZTk1MWE5NjUtMGVmMS00NjU4LTg0ZmEtYTQ4NWExMGJmNWZhIiwidCI6Ijc0NTkwNTUzLTkzMjYtNDE4Yi04MDA2LTI4ODQzNjhjYTNmMiJ9&pageName=3bfe2ebd104db06a54a6)**  ·  **[Portfolio →](https://biagiospada.dev)**

---

## Overview

This project analyzes the competitive landscape of Catania's restaurant market to support data-driven investment decisions. The pipeline collects, cleans, geocodes, and visualizes data on 230+ restaurants, producing actionable insights on market saturation, pricing gaps, and geographic opportunities.

## Key Findings

- **Italian Seafood dominates** — 76 restaurants (33% of market), making it the most saturated segment
- **$$–$$$ tier is oversaturated** — 70% market share but the lowest average rating (4.36), signaling quality gaps
- **3 underserved niches identified** — Seafood Mediterranean, Asian Thai, and Dessert Italian show high demand with low supply
- **Geographic opportunity in Sud-Est** — only 15 restaurants but the highest average rating (4.50) vs. 71 in the saturated historic center (Sud-Ovest)
- **Premium pricing is cosmetic** — $$$$ tier averages €13.21/dish vs. €13.05 for $$–$$$, based on 2,599 menu items analyzed

## Architecture

```
TripAdvisor ──→ Scrapy Spider ──→ PostgreSQL ──→ Power BI Dashboard
                                       ↑
                          Python Geocoding
                        (Nominatim / geopy)
```

| Stage | Tool | Description |
|-------|------|-------------|
| **Scraping** | Scrapy | Automated spider collecting restaurant data (name, rating, reviews, price range, cuisine, address) |
| **Storage** | PostgreSQL | Relational database with structured schema |
| **Geocoding** | Python (geopy/Nominatim) | Latitude/longitude resolution from addresses — 138/152 restaurants successfully geocoded |
| **Modeling** | Power BI | Star schema with 5 tables, 3 relationships, 16 DAX measures |
| **Visualization** | Power BI | 3-page interactive dashboard with KPIs, maps, charts, and cross-filtering |

## Data Model

```
                    ┌──────────────────┐
                    │  dim_cuisine     │
                    │──────────────────│
                    │  cuisine_id (PK) │
                    │  cuisine_name    │
                    └────────┬─────────┘
                             │
                ┌────────────┴────────────┐
                │ bridge_restaurant_      │
                │ cuisine                 │
                │─────────────────────────│
                │ restaurant_id (FK)      │
                │ cuisine_id (FK)         │
                └────────────┬────────────┘
                             │
┌──────────────────┐         │         ┌──────────────────┐
│  dim_restaurant  ├─────────┘         │  fact_menu       │
│──────────────────│                   │──────────────────│
│  id (PK)         │───────────────────│  restaurant_id   │
│  name            │                   │  dish_name       │
│  rating_avg      │                   │  price           │
│  total_reviews   │                   │  currency        │
│  price_range     │                   └──────────────────┘
│  address         │
│  latitude        │
│  longitude       │
│  zone            │
└──────────────────┘
```

## Dashboard

The Power BI dashboard consists of 3 interactive pages:

1. **Market Overview** — KPI cards (total restaurants, avg. rating, avg. dish price), cuisine mix donut chart, geographic bubble map, restaurant ranking table with price range slicer
2. **Pricing & Correlation Analysis** — Price distribution across segments, rating vs. price correlations, menu depth analysis
3. **Geographic Analysis** — Zone-level saturation mapping, quadrant comparison, opportunity identification

> Screenshots available in `/screenshots`

## Tech Stack

- **Python** — Scrapy (scraping), geopy (geocoding), Pandas (data processing)
- **PostgreSQL** — Data storage and SQL analysis
- **Power BI** — Star schema modeling, DAX measures, Power Query/M, interactive dashboards
- **Git** — Version control

## Project Structure

```
├── restaurant_scraper/       # Scrapy project
│   ├── spiders/              # TripAdvisor spider
│   ├── items.py
│   ├── pipelines.py          # PostgreSQL pipeline
│   └── settings.py
├── scripts/
│   └── geocoding.py          # Nominatim geocoding script
├── screenshots/              # Dashboard screenshots
├── restaurant_analysis.pbix  # Power BI file
└── README.md
```

## Setup

### Prerequisites
- Python 3.10+
- PostgreSQL
- Power BI Desktop

### Installation

```bash
# Clone the repo
git clone https://github.com/raytp29/restaurant-scraper.git
cd restaurant-scraper

# Install dependencies
pip install scrapy geopy pandas psycopg2-binary

# Set up PostgreSQL database
createdb restaurants

# Run the spider
cd restaurant_scraper
scrapy crawl tripadvisor

# Run geocoding
python scripts/geocoding.py
```

Then open `restaurant_analysis.pbix` in Power BI Desktop and connect to your local PostgreSQL instance (`localhost:5432`, database `restaurants`).

## Author

**Biagio Spada** — Data Analyst

- Portfolio: [biagiospada.dev](https://biagiospada.dev)
- LinkedIn: [linkedin.com/in/biagio-spada](https://linkedin.com/in/biagio-spada)
- GitHub: [github.com/raytp29](https://github.com/raytp29)
