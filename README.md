# Occasion-Based Product Recommender

FastAPI application that recommends products from `products.json` for a user-provided occasion (for example, `Wedding`, `Diwali`, `Office Party`) and displays ranked results on the same page.

## What It Does

- Loads and normalizes product data from `products.json`
- Filters to active, approved, non-deleted products only
- Expands occasions with curated keywords (rule-based)
- Ranks products using token overlap + cosine similarity + category/keyword boosts
- Penalizes products that strongly match conflicting occasion terms
- Exposes:
  - Web UI at `/`
  - JSON API at `/api/recommend`

## Tech Stack

- Python 3
- FastAPI
- Jinja2 templates
- Vanilla JavaScript/CSS

## Repository Structure

```text
app/
  main.py            # FastAPI app + routes
  recommender.py     # normalization + ranking logic
templates/
  index.html         # single-page UI
static/
  app.js             # client-side fetch + rendering
  styles.css         # page styling
products.json        # input catalog
requirements.txt
```

## Recommendation Pipeline

1. Normalize fields from the source payload into an internal `NormalizedProduct` model.
2. Build searchable text from title, description, brand, and derived category label.
3. Expand the query occasion with predefined keywords from `OCCASION_RULES`.
4. Vectorize query/product text as token frequency counters.
5. Compute cosine similarity.
6. Apply boosts for:
   - query token hits in title/body
   - category match with the detected occasion rule
   - direct rule-keyword hits in title/body
7. Apply a penalty for conflicting special-occasion terms.
8. Deduplicate similar titles and return top `limit` results.

## Data Filtering and Normalization

`load_products()` keeps only entries where:

- `status == "ACTIVE"`
- `isApproved == true`
- `deletedAt` is empty/null

Main field mappings include:

- `id` -> `product_id`
- `shopId` -> `vendor_id`
- `categoryId` -> `vendor_category`
- `name` -> `title`
- `description`/`shortDescription` -> `description`
- `mainImage` -> `files[0]`

Category IDs are translated to readable labels using `CATEGORY_LABELS`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the App

```bash
uvicorn app.main:app --reload
```

Open: `http://127.0.0.1:8000`

## API

### Request

```bash
curl "http://127.0.0.1:8000/api/recommend?occasion=Wedding&limit=8"
```

### Query Parameters

- `occasion` (string, required, 1-100 chars)
- `limit` (int, optional, default `8`, min `1`, max `24`)

### Response Shape

```json
{
  "occasion": "Wedding",
  "count": 8,
  "results": [
    {
      "productId": "...",
      "title": "...",
      "vendor_category_desc": "...",
      "description_snippet": "...",
      "image_url": "https://...",
      "brand": "...",
      "score": 0.7421
    }
  ]
}
```
