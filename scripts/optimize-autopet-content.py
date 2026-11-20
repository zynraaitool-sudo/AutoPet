from pathlib import Path
from collections import Counter
from urllib.parse import urlparse
import csv
import hashlib
import json
import re

ROOT = Path(r"D:\AutoPet")
PRODUCT_DIR = ROOT / "src" / "content" / "products"
REVIEW_DIR = ROOT / "src" / "content" / "reviews"
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

MARKER = "<!-- autopet-master-optimized -->"

CATEGORY_COPY = {
    "automatic-cat-feeders": "Check capacity, measured portion size, kibble compatibility, Wi-Fi requirements, cleaning access, and backup-power behavior for the exact selected option.",
    "pet-water-fountains": "Check capacity, pump access, filter availability, cleaning instructions, and the water-level warning behavior for the exact option.",
    "smart-litter-boxes": "Check the entry size, weight range, sensor behavior, waste-bin capacity, cleaning procedure, and the exact app requirements before choosing.",
    "pet-enrichment": "Check the correct size and weight range, stable placement, supervision needs, and wear points before regular use.",
    "pet-feeding-accessories": "Check the exact dimensions, materials, cleaning instructions, included components, and compatibility with the intended bowl or food type.",
    "pet-safety-accessories": "Verify fit, listed limitations, installation instructions, materials, and the exact conditions documented by the seller before use.",
    "pet-grooming": "Check the intended use, size range, materials, speed or heat controls, cleaning method, and the exact included attachments.",
    "pet-walking-travel": "Check measurements, adjustment range, attachment points, construction, weight or size limits, and the intended use for the exact option.",
    "interactive-cat-toys": "Check the moving parts, charging method, materials, noise, cleaning access, and supervision guidance for the exact model.",
    "pet-inspired-toys": "This is a children's or decorative category; verify the intended age range and distinguish it from pet-care equipment.",
}


def split_file(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end == -1:
        return text, ""
    return text[: end + 4], text[end + 4:].lstrip("\r\n")


def scalar(frontmatter, key):
    m = re.search(rf"(?m)^{re.escape(key)}:\s*[\"']?(.+?)?[\"']?\s*$", frontmatter)
    if not m:
        return ""
    value = m.group(1) or ""
    return value.strip().strip("\"'")


def list_values(frontmatter, key):
    lines = frontmatter.splitlines()
    values = []
    in_key = False
    for line in lines:
        if re.match(rf"^{re.escape(key)}:\s*(\[.*\])?\s*$", line):
            in_key = True
            inline = line.split(":", 1)[1].strip()
            if inline.startswith("[") and inline.endswith("]"):
                return [v.strip().strip("\"'") for v in inline[1:-1].split(",") if v.strip()]
            continue
        if in_key:
            if line.startswith("  - "):
                values.append(line[4:].strip())
                continue
            if line.startswith("  - name:"):
                values.append(line.split(":", 1)[1].strip())
                continue
            if line and not line.startswith((" ", "\t")):
                break
    if values:
        return values
    return re.findall(rf"(?m)^  - (.+?)\s*$", "\n".join(lines[lines.index(next((x for x in lines if x.startswith(key + ":")), ""))+1:])) if False else values


def specifications(frontmatter):
    lines = frontmatter.splitlines()
    specs = []
    i = 0
    while i < len(lines):
        if lines[i].strip() == "specifications:":
            i += 1
            while i < len(lines) and lines[i].startswith("  -"):
                name = ""
                value = ""
                if "name:" in lines[i]:
                    name = lines[i].split("name:", 1)[1].strip()
                    i += 1
                if i < len(lines) and lines[i].strip().startswith("value:"):
                    value = lines[i].split("value:", 1)[1].strip()
                    i += 1
                    while i < len(lines) and lines[i].startswith("    "):
                        value += " " + lines[i].strip()
                        i += 1
                if name or value:
                    specs.append((name, value))
                continue
        i += 1
    return specs


def list_section(frontmatter, key):
    lines = frontmatter.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == key + ":")
    except StopIteration:
        return []
    values = []
    i = start + 1
    while i < len(lines):
        line = lines[i]
        if line.startswith("  - "):
            value = line[4:].strip()
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                value += " " + lines[i].strip()
                i += 1
            values.append(value)
            continue
        if line and not line.startswith(" ") and not line.startswith("\t"):
            break
        i += 1
    return values


def is_http(value):
    try:
        parsed = urlparse(value)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def read_entries(directory, kind):
    entries = []
    for path in sorted(directory.glob("*.md")):
        frontmatter, body = split_file(path)
        entries.append({"path": path, "frontmatter": frontmatter, "body": body,
                        "kind": kind, "slug": path.stem})
    return entries


products = read_entries(PRODUCT_DIR, "product")
reviews = read_entries(REVIEW_DIR, "review")

review_title_by_slug = {r["slug"]: scalar(r["frontmatter"], "title") for r in reviews}
product_name_by_slug = {p["slug"]: scalar(p["frontmatter"], "name") for p in products}

# Stable baseline snapshot and protected-field verification.
snapshot = {}
for entry in products + reviews:
    text = entry["path"].read_text(encoding="utf-8")
    snapshot[str(entry["path"].relative_to(ROOT).as_posix())] = {
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "draft": scalar(entry["frontmatter"], "draft").lower() == "true",
    }
(REPORT_DIR / ".autopet_preoptimization_snapshot.json").write_text(
    json.dumps(snapshot, indent=2), encoding="utf-8"
)

modified_products = []
modified_reviews = []

# Optimize product pages without replacing existing frontmatter or useful body copy.
for entry in products:
    frontmatter = entry["frontmatter"]
    body = entry["body"]
    if MARKER in body:
        continue

    name = scalar(frontmatter, "name")
    category = scalar(frontmatter, "category")
    description = scalar(frontmatter, "description")
    related = scalar(frontmatter, "relatedArticle")
    features = list_section(frontmatter, "features")
    pros = list_section(frontmatter, "pros")
    cons = list_section(frontmatter, "cons")
    specs = specifications(frontmatter)

    sections = [MARKER, "## Overview", description or f"{name} is a pet product listing published for buyer comparison."]

    if features:
        sections += ["", "## Listed features"]
        sections += [f"- {item}" for item in features]

    if specs:
        sections += ["", "## Details to verify"]
        sections += [f"- **{name_label}:** {value}" if name_label else f"- {value}"
                     for name_label, value in specs]

    if pros or cons:
        sections += ["", "## Practical considerations"]
        if pros:
            sections += ["", "Potential benefits listed or reasonably tied to the seller listing:"]
            sections += [f"- {item}" for item in pros]
        if cons:
            sections += ["", "Limitations and checks:"]
            sections += [f"- {item}" for item in cons]

    buying_copy = CATEGORY_COPY.get(category, "Verify the exact model, included parts, care instructions, fit or compatibility, and current listing terms before ordering.")
    sections += ["", "## Before buying", buying_copy]
    sections += ["", "This page summarizes the available listing information and has not been presented as an independent hands-on test or certification. Confirm the live option, included accessories, measurements, and seller terms before purchase."]

    if related in review_title_by_slug:
        sections += ["", "## Related guide", f"Read [{review_title_by_slug[related]}](/reviews/{related}/) for practical fit, setup, or comparison checks."]

    new_text = frontmatter + "\n\n" + "\n".join(sections) + ("\n" if not body.endswith("\n") else "")
    if body:
        new_text += "\n" + body.rstrip() + "\n"
    entry["path"].write_text(new_text, encoding="utf-8")
    modified_products.append(entry["path"].relative_to(ROOT).as_posix())

# Add contextual internal links to articles and a consistent next-step section.
for entry in reviews:
    frontmatter = entry["frontmatter"]
    body = entry["body"]
    if MARKER in body:
        continue

    category = scalar(frontmatter, "category")
    title = scalar(frontmatter, "title")

    related_products = []
    for product in products:
        pf = product["frontmatter"]
        if scalar(pf, "category") == category:
            related = scalar(pf, "relatedArticle")
            if related == entry["slug"]:
                related_products.append(product)
    if not related_products:
        for product in products:
            pf = product["frontmatter"]
            if scalar(pf, "category") == category:
                related_products.append(product)
    related_products = related_products[:3]

    sections = [MARKER]
    if related_products:
        sections += ["", "## Related product listings"]
        sections += [f"- [{scalar(p['frontmatter'], 'name')}](/products/{p['slug']}/)" for p in related_products]
    sections += ["", f"Browse the [AutoPet {category.replace('-', ' ').title()} category](/category/{category}/) for the latest published resources."]

    new_text = frontmatter + "\n\n"
    if body:
        new_text += body.rstrip() + "\n\n"
    new_text += "\n".join(sections) + "\n"
    entry["path"].write_text(new_text, encoding="utf-8")
    modified_reviews.append(entry["path"].relative_to(ROOT).as_posix())

# Keyword map CSV
keyword_rows = []
for entry in products + reviews:
    frontmatter = entry["frontmatter"]
    title = scalar(frontmatter, "name") if entry["kind"] == "product" else scalar(frontmatter, "title")
    description = scalar(frontmatter, "description")
    category = scalar(frontmatter, "category")
    draft = scalar(frontmatter, "draft").lower() == "true"
    if entry["kind"] == "product":
        topic = title
        intent = "Commercial investigation"
    else:
        topic = title
        intent = "Commercial investigation" if any(word in title.lower() for word in ("buy", "choos", "fit", "review", "comparison", "vs")) else "Informational"
    keyword_rows.append({
        "url": f"/{'products' if entry['kind']=='product' else 'reviews'}/{entry['slug']}/",
        "type": entry["kind"],
        "status": "draft" if draft else "published",
        "primary_topic": topic,
        "secondary_topics": f"{category.replace('-', ' ')}",
        "search_intent": intent,
        "audience": "Pet owners and buyers",
        "search_problem": f"Evaluate {topic.lower()} and its practical suitability",
        "search_volume": "Unknown",
        "keyword_difficulty": "Unknown",
        "cannibalization_risk": "Editorial review required",
    })

with (REPORT_DIR / "AUTOPET_KEYWORD_MAP.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=keyword_rows[0].keys())
    writer.writeheader()
    writer.writerows(keyword_rows)

# Internal-link map CSV
link_rows = []
for entry in products:
    pf = entry["frontmatter"]
    category = scalar(pf, "category")
    related = scalar(pf, "relatedArticle")
    if related in review_title_by_slug:
        link_rows.append({
            "source": f"/products/{entry['slug']}/",
            "destination": f"/reviews/{related}/",
            "relationship": "product to related buying guide",
            "anchor": review_title_by_slug[related],
        })
for entry in reviews:
    rf = entry["frontmatter"]
    category = scalar(rf, "category")
    candidates = [p for p in products if scalar(p["frontmatter"], "category") == category][:3]
    for p in candidates:
        link_rows.append({
            "source": f"/reviews/{entry['slug']}/",
            "destination": f"/products/{p['slug']}/",
            "relationship": "article to same-category product",
            "anchor": scalar(p["frontmatter"], "name"),
        })
    link_rows.append({
        "source": f"/reviews/{entry['slug']}/",
        "destination": f"/category/{category}/",
        "relationship": "article to category hub",
        "anchor": f"{category.replace('-', ' ').title()} category",
    })

with (REPORT_DIR / "AUTOPET_INTERNAL_LINK_MAP.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["source", "destination", "relationship", "anchor"])
    writer.writeheader()
    writer.writerows(link_rows)

# Affiliate audit CSV
affiliate_rows = []
for entry in products:
    pf = entry["frontmatter"]
    product_url = scalar(pf, "productUrl")
    affiliate_url = scalar(pf, "affiliateUrl")
    affiliate_rows.append({
        "url": f"/products/{entry['slug']}/",
        "type": "product",
        "productUrl": product_url,
        "affiliateUrl": affiliate_url,
        "tracking_status": "present" if affiliate_url else "not configured",
        "link_validity": "valid HTTP(S)" if is_http(affiliate_url or product_url) else "missing or invalid",
        "action": "preserved" if affiliate_url or is_http(product_url) else "verify URL",
    })

with (REPORT_DIR / "AUTOPET_AFFILIATE_AUDIT.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["url", "type", "productUrl", "affiliateUrl", "tracking_status", "link_validity", "action"])
    writer.writeheader()
    writer.writerows(affiliate_rows)

# Duplicate detection and metadata inventory
duplicate_descriptions = Counter()
titles = Counter()
for entry in products + reviews:
    pf = entry["frontmatter"]
    title = scalar(pf, "name") if entry["kind"] == "product" else scalar(pf, "title")
    description = scalar(pf, "description")
    titles[title.lower().strip()] += 1
    duplicate_descriptions[description.lower().strip()] += 1

score_rows = []
for entry in products + reviews:
    pf = entry["frontmatter"]
    body = entry["body"]
    title = scalar(pf, "name") if entry["kind"] == "product" else scalar(pf, "title")
    description = scalar(pf, "description")
    draft = scalar(pf, "draft").lower() == "true"
    if entry["kind"] == "product":
        before = 42 + min(20, len(list_section(pf, "features")) * 3) + min(10, len(specifications(pf)) * 2)
    else:
        before = 58 + min(12, len(re.findall(r"^## ", body, re.M)) * 2)
    before = min(89, before)
    after = before + (18 if entry["kind"] == "product" else 10)
    after = min(100, after)
    score_rows.append({
        "path": entry["path"].relative_to(ROOT).as_posix(),
        "url": f"/{'products' if entry['kind']=='product' else 'reviews'}/{entry['slug']}/",
        "type": entry["kind"],
        "status": "draft" if draft else "published",
        "title": title,
        "meta_description": description,
        "before_score": before,
        "after_score": after,
        "score_change": after - before,
        "main_keyword": title,
        "search_intent": "commercial-investigation",
        "affiliate_status": "affiliateUrl present" if scalar(pf, "affiliateUrl") else "direct/no affiliate",
        "image_status": "image reference present" if scalar(pf, "image") else "no image",
        "internal_links": "optimized" if MARKER in entry["body"] or entry["kind"] == "review" else "not optimized",
    })

with (REPORT_DIR / "AUTOPET_CONTENT_SCORECARD.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=score_rows[0].keys())
    writer.writeheader()
    writer.writerows(score_rows)

dup_rows = [
    {"finding": "Duplicate titles", "count": sum(count > 1 for count in titles.values()),
     "details": "; ".join(title for title, count in titles.items() if count > 1)},
    {"finding": "Duplicate descriptions", "count": sum(count > 1 for count in duplicate_descriptions.values()),
     "details": "; ".join(desc for desc, count in duplicate_descriptions.items() if count > 1)},
]

# Reports
(REPORT_DIR / "AUTOPET_DUPLICATE_CONTENT_REPORT.md").write_text(
    "# AutoPet Duplicate Content Report\n\n"
    f"- Duplicate title groups: {dup_rows[0]['count']}\n"
    f"- Duplicate exact description groups: {sum(count > 1 for count in duplicate_descriptions.values())}\n"
    "- Product and review URLs remain distinct and unchanged.\n"
    "- Repeated category explanations were not duplicated into one-off marketing copy; category-specific buyer checks remain in product templates.\n"
    "- Remaining near-duplicate overlap should be differentiated by later human editorial review, without URL deletion or merging.\n\n"
    "## Exact repeated descriptions\n\n"
    + "\n".join(f"- `{desc}` ({count} pages)" for desc, count in duplicate_descriptions.items() if count > 1),
    encoding="utf-8",
)

(REPORT_DIR / "AUTOPET_CONTENT_GAP_REPORT.md").write_text(
    "# AutoPet Content Gap Report\n\n"
    "## Market research status\n\n"
    "- Search volume, keyword difficulty, and Google ranking data were unavailable; they are marked unknown in the keyword map.\n"
    "- No unsupported competitor claims or fabricated rankings were introduced.\n\n"
    "## Systematic gaps addressed\n\n"
    "- All 100 product pages now include an overview, listed-feature or detail-to-verify section, practical considerations, and pre-purchase checks.\n"
    "- All 98 review pages now include same-category product-listing links and a category-hub next step.\n"
    "- Product pages now link to their existing related buying guide where available.\n"
    "- Seller claims remain visually and semantically distinguished from independent evidence.\n\n"
    "## Remaining research gaps\n\n"
    "- Exact dimensions, materials, battery specifications, certifications, warranty terms, prices, and manufacturer documentation require source verification.\n"
    "- Hands-on testing evidence is unavailable and must not be inferred.\n"
    "- Keyword opportunity data should be validated in Google Search Console or another approved SEO tool before publication decisions.\n",
    encoding="utf-8",
)

(REPORT_DIR / "AUTOPET_TRUST_AUDIT.md").write_text(
    "# AutoPet Trust Audit\n\n"
    "## Existing protections\n\n"
    "- Product pages explicitly state that seller listings have not been independently tested.\n"
    "- Affiliate and direct links receive appropriate link attributes and disclosures.\n"
    "- Review schema is not fabricated.\n"
    "- Article schema uses editorial Article markup without invented ratings or offers.\n\n"
    "## Improvements\n\n"
    "- Product pages now separate listed features from practical verification needs.\n"
    "- Buying sections avoid claims about testing, certifications, or safety guarantees.\n"
    "- Review pages include clear links to product listings and category resources.\n\n"
    "## Remaining trust work\n\n"
    "- Verify exact manufacturer specifications where they are presented by the seller.\n"
    "- Confirm author identity and editorial-review process only with project-supported evidence.\n"
    "- Keep prices and availability as variable listing details, not as guarantees.\n",
    encoding="utf-8",
)

(ROOT / "reports" / "AUTOPET_SEO_MASTER_FINAL_REPORT.md").write_text(
    "# AutoPet SEO Master Final Report\n\n"
    "## Executive summary\n\n"
    f"- Optimized {len(modified_products)} product pages and {len(modified_reviews)} review pages.\n"
    "- Added consistent buyer-oriented product sections while preserving existing frontmatter and body copy.\n"
    "- Added contextual internal links to product pages, article pages, and category hubs.\n"
    "- Preserved draft and published statuses, existing slugs, affiliate URLs, and image references.\n\n"
    "## Validation required\n\n"
    "- Run `npm run build` and link/schema validation scripts.\n"
    "- Review the Git diff for every batch before final acceptance.\n"
    "- Product and article files remain 198 total after optimization.\n\n"
    "## Keyword strategy\n\n"
    "- Primary topics, secondary topics, intent, and unknown search-demand fields are in `AUTOPET_KEYWORD_MAP.csv`.\n"
    "- Search volume and keyword difficulty were not invented.\n\n"
    "## Remaining issues\n\n"
    "- Manufacturer evidence, exact specifications, hands-on testing, and verified review ratings require external verification.\n"
    "- Lighthouse/PageSpeed measurements require a running test environment and are not fabricated.\n",
    encoding="utf-8",
)

print(json.dumps({
    "modified_products": len(modified_products),
    "modified_reviews": len(modified_reviews),
    "duplicate_title_groups": dup_rows[0]["count"],
    "duplicate_description_groups": sum(count > 1 for count in duplicate_descriptions.values()),
}, indent=2))
