import re
from difflib import SequenceMatcher


STAGE_ORDER = {
    "Pre-seed": 0,
    "Seed": 1,
    "Series A": 2,
    "Series B": 3,
    "Series C+": 4,
}

FUNCTION_KEYWORDS = {
    "Engineering": [
        "engineer",
        "developer",
        "software",
        "frontend",
        "backend",
        "full stack",
        "fullstack",
        "ios",
        "android",
        "platform",
        "devops",
        "security",
        "research",
        "ml",
        "ai",
        "blockchain",
    ],
    "GTM": [
        "account executive",
        "sales",
        "growth",
        "marketing",
        "customer success",
        "demand generation",
        "revenue",
        "partnership",
        "success manager",
        "bdr",
        "sdr",
        "community",
    ],
    "Product": [
        "product manager",
        "product",
        "developer relations",
        "founder associate",
    ],
    "Design": [
        "designer",
        "design",
        "ux",
        "brand",
        "creative",
    ],
    "People": [
        "recruiter",
        "talent",
        "people",
        "hr",
        "human resources",
        "mentor",
        "therapist",
    ],
    "Clinical": [
        "clinical",
        "epic",
        "ehr",
        "health",
        "therapist",
        "associate antibody",
        "scientist",
    ],
    "Ops": [
        "operations",
        "ops",
        "chief of staff",
        "finance",
        "counsel",
        "analyst",
        "implementation",
        "support",
        "generalist",
        "program manager",
    ],
}

SENIORITY_KEYWORDS = [
    ("Founding", ["founding", "first"]),
    ("Chief", ["chief", "vp", "head"]),
    ("Director", ["director"]),
    ("Principal", ["principal", "staff"]),
    ("Senior", ["senior", "sr"]),
    ("Manager", ["manager", "lead"]),
    ("Associate", ["associate"]),
]

CITY_CLUSTERS = {
    "Bay Area": {"san francisco", "oakland", "berkeley"},
    "New York City": {"new york", "brooklyn", "glen cove"},
    "Boston": {"boston", "cambridge"},
    "Remote": {"remote"},
    "Austin": {"austin"},
}


def normalize_whitespace(value):
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_text(value):
    value = normalize_whitespace(value).lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9+ ]", " ", value)
    return normalize_whitespace(value)


def normalize_stage(stage):
    stage = normalize_text(stage)
    if stage in {"pre seed", "pre-seed"}:
        return "Pre-seed"
    if stage == "seed":
        return "Seed"
    if stage == "series a":
        return "Series A"
    if stage == "series b":
        return "Series B"
    if stage in {"series c", "series c+", "series d", "public company"}:
        return "Series C+"
    return "Seed"


def stage_rank(stage):
    return STAGE_ORDER[normalize_stage(stage)]


def normalize_role_title(title):
    title = normalize_text(title)
    replacements = {
        "full stack": "fullstack",
        "swe": "software engineer",
        "ae": "account executive",
        "sr ": "senior ",
    }
    for source, target in replacements.items():
        title = title.replace(source, target)
    return normalize_whitespace(title)


def parse_cost_to_usd(cost_display):
    match = re.search(r"([\d.]+)", cost_display or "")
    if not match:
        return 0
    value = float(match.group(1))
    if "k" in (cost_display or "").lower():
        return int(round(value * 1000))
    return int(round(value))


def infer_function(title):
    title = normalize_role_title(title)
    for function, keywords in FUNCTION_KEYWORDS.items():
        if any(keyword in title for keyword in keywords):
            return function
    return "Other"


def infer_seniority(title):
    title = normalize_role_title(title)
    for label, keywords in SENIORITY_KEYWORDS:
        if any(keyword in title for keyword in keywords):
            return label
    return "Individual Contributor"


def normalize_location(location):
    location = normalize_whitespace(location)
    if not location:
        return {
            "city": "",
            "region": "",
            "cluster": "",
            "display": "",
        }
    if location.lower() == "remote":
        return {
            "city": "Remote",
            "region": "Remote",
            "cluster": "Remote",
            "display": "Remote",
        }
    parts = [normalize_whitespace(part) for part in location.split(",")]
    city = parts[0]
    region = parts[1] if len(parts) > 1 else ""
    city_key = city.lower()
    cluster = region or city
    for cluster_name, cities in CITY_CLUSTERS.items():
        if city_key in cities:
            cluster = cluster_name
            break
    if region == "Canada":
        cluster = "Remote"
    return {
        "city": city,
        "region": region,
        "cluster": cluster,
        "display": location,
    }


def title_similarity(left, right):
    left_norm = normalize_role_title(left)
    right_norm = normalize_role_title(right)
    return SequenceMatcher(None, left_norm, right_norm).ratio()
