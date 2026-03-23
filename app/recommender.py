from __future__ import annotations

import math
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence


CATEGORY_LABELS = {
    "cmkz54pbm000vns019mokm8dp": "Flowers & Bouquets",
    "cmkz57wza0012ns0162oh4obo": "Chocolates & Sweets",
    "cmkz592k20018ns012ju457bg": "Watches & Accessories",
    "cml0g5j3g0002sc01qobq1n72": "Curated Gifts & Stationery",
    "cml0g6qev0007sc01d1wj96mo": "Fashion & Apparel",
    "cml0olc910039pw01177zda8g": "Jewelry",
    "cml0qw58i008jpw01p5a85pr7": "Eco-Friendly Gifts",
    "cml0r4bxr008opw01aktfdvmx": "Wellness Essentials",
    "cml0r659g008tpw018zqjkdkb": "Sustainable Home Decor",
    "cml0tctfc002xo201hpycr57n": "Musical Toys",
    "cml0u5vji0032o201xpg166lu": "Plush Toys",
    "cml0u88h80038o201hhcw0q2k": "Creative Activity Kits",
    "cml0uasxm003eo201thwvbg5l": "Fragrances & Candles",
    "cml0ue769003no201f7vi986z": "Gift Cards",
    "cml0ug1d6003to201xuwjkmcn": "Gift Accessories",
    "cml1xsl8p000ald01fjlwo2lo": "Romantic Gifts",
    "cml1xxy3k000gld01lmldeic1": "Personalized Keepsakes",
    "cml1y3ir8000hma01zboy5gts": "Couple Gifts",
    "cml256swj00elma01jdp2zgfb": "Festive Hampers",
    "cml258vol00eqma01a56hvc3y": "Occasion Gift Sets",
}

OCCASION_RULES = {
    "birthday": {
        "keywords": [
            "birthday",
            "party",
            "celebration",
            "cake",
            "gift",
            "flowers",
            "candles",
        ],
        "categories": [
            "Flowers & Bouquets",
            "Chocolates & Sweets",
            "Gift Accessories",
            "Fragrances & Candles",
            "Personalized Keepsakes",
        ],
    },
    "wedding": {
        "keywords": [
            "wedding",
            "bridal",
            "couple",
            "romantic",
            "love",
            "engagement",
            "jewelry",
        ],
        "categories": [
            "Jewelry",
            "Couple Gifts",
            "Romantic Gifts",
            "Flowers & Bouquets",
            "Personalized Keepsakes",
        ],
    },
    "anniversary": {
        "keywords": [
            "anniversary",
            "couple",
            "romantic",
            "love",
            "rose",
            "perfume",
            "jewelry",
        ],
        "categories": [
            "Jewelry",
            "Couple Gifts",
            "Romantic Gifts",
            "Flowers & Bouquets",
            "Fragrances & Candles",
        ],
    },
    "valentine": {
        "keywords": [
            "valentine",
            "love",
            "romantic",
            "couple",
            "rose",
            "chocolate",
            "perfume",
        ],
        "categories": [
            "Romantic Gifts",
            "Couple Gifts",
            "Flowers & Bouquets",
            "Chocolates & Sweets",
            "Fragrances & Candles",
        ],
    },
    "diwali": {
        "keywords": [
            "diwali",
            "festival",
            "festive",
            "hamper",
            "luxury",
            "dry fruits",
            "gift",
        ],
        "categories": ["Festive Hampers", "Gift Accessories", "Gift Cards"],
    },
    "holi": {
        "keywords": ["holi", "festival", "festive", "hamper", "gift"],
        "categories": ["Festive Hampers", "Gift Accessories"],
    },
    "christmas": {
        "keywords": ["christmas", "holiday", "winter", "hamper", "gift"],
        "categories": ["Festive Hampers", "Gift Accessories", "Gift Cards"],
    },
    "office party": {
        "keywords": [
            "office",
            "corporate",
            "team",
            "coworker",
            "pens",
            "stationery",
            "gift cards",
        ],
        "categories": ["Gift Cards", "Curated Gifts & Stationery", "Gift Accessories"],
    },
    "baby shower": {
        "keywords": [
            "baby",
            "newborn",
            "baby shower",
            "soft toys",
            "plush",
            "keepsake",
        ],
        "categories": ["Occasion Gift Sets", "Plush Toys", "Personalized Keepsakes"],
    },
    "housewarming": {
        "keywords": [
            "housewarming",
            "home",
            "decor",
            "candles",
            "planters",
            "wellness",
        ],
        "categories": [
            "Sustainable Home Decor",
            "Fragrances & Candles",
            "Occasion Gift Sets",
        ],
    },
    "engagement": {
        "keywords": ["engagement", "couple", "romantic", "jewelry", "wedding", "love"],
        "categories": [
            "Jewelry",
            "Couple Gifts",
            "Romantic Gifts",
            "Occasion Gift Sets",
        ],
    },
}

SPECIAL_OCCASION_TERMS = {
    "birthday",
    "wedding",
    "anniversary",
    "valentine",
    "engagement",
    "diwali",
    "holi",
    "christmas",
    "baby",
    "newborn",
    "housewarming",
    "office",
}

TOKEN_RE = re.compile(r"[a-z0-9']+")


@dataclass(frozen=True)
class NormalizedProduct:
    product_id: str
    vendor_id: str
    vendor_category: str
    vendor_category_desc: str
    title: str
    description: str
    files: Sequence[str]
    brand: str
    search_text: str


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall((text or "").lower())


def derive_category_label(category_id: str, title: str) -> str:
    return CATEGORY_LABELS.get(category_id) or (
        title.strip() if title else "General Gifts"
    )


def build_search_text(
    title: str,
    description: str,
    short_description: str,
    brand: str,
    category_label: str,
) -> str:
    parts = [title, description, short_description, brand, category_label]
    return " ".join(part.strip() for part in parts if part).lower()


def get_occasion_rule(occasion: str) -> dict | None:
    lowered = (occasion or "").strip().lower()
    for key, rule in OCCASION_RULES.items():
        if key in lowered or lowered in key:
            return rule
    return None


def expand_occasion(occasion: str) -> str:
    rule = get_occasion_rule(occasion)
    words = set(tokenize(occasion))
    if rule:
        for keyword in rule["keywords"]:
            words.update(tokenize(keyword))
    return " ".join(sorted(words))


class OccasionRecommender:
    def __init__(self, products: Sequence[NormalizedProduct]) -> None:
        self.products = list(products)
        self.product_vectors = [
            self._vectorize(product.search_text) for product in self.products
        ]

    def recommend(self, occasion: str, limit: int = 8) -> List[dict]:
        query = (occasion or "").strip()
        if not query:
            return []

        query_text = self._build_query_text(query)
        query_vector = self._vectorize(query_text)
        expanded_tokens = set(tokenize(query_text))
        rule = get_occasion_rule(query)

        scored_products = []
        for product, product_vector in zip(self.products, self.product_vectors):
            score = self._score_product(
                product, product_vector, query_vector, expanded_tokens, rule
            )
            if score > 0.01:
                scored_products.append((score, product))

        scored_products.sort(key=lambda item: item[0], reverse=True)
        top_results = self._deduplicate(scored_products, limit)
        return [
            {
                "productId": product.product_id,
                "title": product.title,
                "vendor_category_desc": product.vendor_category_desc,
                "description_snippet": self._snippet(product.description),
                "image_url": product.files[0] if product.files else "",
                "brand": product.brand,
                "score": round(score, 4),
            }
            for score, product in top_results
        ]

    def _build_query_text(self, occasion: str) -> str:
        rule = get_occasion_rule(occasion)
        parts = [occasion, expand_occasion(occasion)]
        if rule:
            parts.extend(rule["categories"])
        return " ".join(parts)

    def _vectorize(self, text: str) -> Counter:
        return Counter(tokenize(text))

    def _cosine_similarity(self, left: Counter, right: Counter) -> float:
        if not left or not right:
            return 0.0

        common_terms = set(left) & set(right)
        numerator = sum(left[term] * right[term] for term in common_terms)
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))

        if left_norm == 0.0 or right_norm == 0.0:
            return 0.0

        return numerator / (left_norm * right_norm)

    def _score_product(
        self,
        product: NormalizedProduct,
        product_vector: Counter,
        query_vector: Counter,
        expanded_tokens: set[str],
        rule: dict | None,
    ) -> float:
        score = self._cosine_similarity(query_vector, product_vector)
        query_terms = set(query_vector.keys())
        title_tokens = set(tokenize(product.title))
        product_text = product.search_text.lower()
        title_text = product.title.lower()

        for term in query_terms:
            if term in title_tokens:
                score += 0.06
            elif term in product_vector:
                score += 0.02

        if rule and product.vendor_category_desc in rule["categories"]:
            score += 0.08

        for keyword in rule["keywords"] if rule else []:
            keyword_text = keyword.lower()
            if keyword_text in title_text:
                score += 0.12
            elif keyword_text in product_text:
                score += 0.04

        conflicting_terms = (title_tokens & SPECIAL_OCCASION_TERMS) - expanded_tokens
        if conflicting_terms:
            score *= 0.6

        return min(score, 1.0)

    def _deduplicate(
        self,
        scored_products: Sequence[tuple[float, NormalizedProduct]],
        limit: int,
    ) -> List[tuple[float, NormalizedProduct]]:
        results: List[tuple[float, NormalizedProduct]] = []
        seen_titles = set()

        for score, product in scored_products:
            title_key = re.sub(r"[^a-z0-9]+", " ", product.title.lower()).strip()
            if title_key in seen_titles:
                continue
            seen_titles.add(title_key)
            results.append((score, product))
            if len(results) >= limit:
                break
        return results

    @staticmethod
    def _snippet(text: str, max_length: int = 150) -> str:
        cleaned = re.sub(r"\s+", " ", text).strip()
        if len(cleaned) <= max_length:
            return cleaned
        return cleaned[: max_length - 3].rstrip() + "..."


def load_products(json_path: str | Path) -> List[NormalizedProduct]:
    with open(json_path, "r", encoding="utf-8") as handle:
        payloads = json.load(handle)

    normalized: List[NormalizedProduct] = []
    for payload in payloads:
        if payload.get("status") != "ACTIVE":
            continue
        if payload.get("isApproved") is not True:
            continue
        if payload.get("deletedAt"):
            continue

        product_id = str(
            payload.get("id")
            or payload.get("productId")
            or payload.get("product_id")
            or ""
        )
        vendor_id = str(
            payload.get("shopId")
            or payload.get("vendorId")
            or payload.get("vendor_id")
            or ""
        )
        vendor_category = str(
            payload.get("categoryId") or payload.get("vendor_category") or ""
        )
        title = str(payload.get("name") or payload.get("title") or "").strip()
        description = str(
            payload.get("description") or payload.get("shortDescription") or ""
        ).strip()
        short_description = str(payload.get("shortDescription") or "").strip()
        brand = str(payload.get("brand") or "").strip()
        main_image = str(payload.get("mainImage") or "").strip()
        vendor_category_desc = derive_category_label(vendor_category, title)
        files = [main_image] if main_image else []
        search_text = build_search_text(
            title, description, short_description, brand, vendor_category_desc
        )

        normalized.append(
            NormalizedProduct(
                product_id=product_id,
                vendor_id=vendor_id,
                vendor_category=vendor_category,
                vendor_category_desc=vendor_category_desc,
                title=title,
                description=description,
                files=files,
                brand=brand,
                search_text=search_text,
            )
        )

    return normalized
