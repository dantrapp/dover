from statistics import median

from planner.models import BenchmarkHire, RecruiterProfile
from planner.services.normalize import (
    infer_function,
    normalize_location,
    normalize_role_title,
    normalize_stage,
    stage_rank,
    title_similarity,
)


def quantile(values, ratio):
    ordered = sorted(values)
    if not ordered:
        return 0
    index = int(round((len(ordered) - 1) * ratio))
    return ordered[index]


def format_currency(value):
    return f"${value / 1000:.1f}K".replace(".0K", "K")


def confidence_label(tier, sample_size):
    if tier <= 2 and sample_size >= 8:
        return "High confidence"
    if sample_size >= 5:
        return "Good directional read"
    return "Low-sample estimate"


def build_query(payload):
    role_title = (payload.get('roleTitle') or '').strip() or 'Founding engineer'
    stage = normalize_stage(payload.get('companyStage') or 'Seed')
    location = normalize_location(payload.get('companyLocation') or 'Remote')
    inferred_function = infer_function(role_title)
    selected_function = payload.get('function') or inferred_function
    if selected_function == 'Other':
        selected_function = inferred_function
    return {
        'role_title': role_title,
        'normalized_role_title': normalize_role_title(role_title),
        'company_stage': stage,
        'stage_rank': stage_rank(stage),
        'location': location,
        'function': selected_function,
        'hiring_priority': payload.get('hiringPriority') or 'Not sure',
        'optional_context': (payload.get('optionalContext') or '').strip(),
    }


def score_hire(hire, query):
    score = 0.0
    title_score = title_similarity(hire.role_title, query['role_title'])
    score += title_score * 4
    if hire.function == query['function']:
        score += 2.5
    stage_gap = abs(hire.stage_rank - query['stage_rank'])
    score += max(0, 1.8 - (stage_gap * 0.7))
    if hire.geo_cluster == query['location']['cluster']:
        score += 1.6
    elif hire.normalized_region and hire.normalized_region == query['location']['region']:
        score += 0.8
    elif query['location']['cluster'] == 'Remote' or hire.geo_cluster == 'Remote':
        score += 0.4
    return round(score, 4), title_score


def select_benchmark_sample(query):
    hires = list(BenchmarkHire.objects.all())
    tiers = [
        lambda hire, title_score: hire.normalized_role_title == query['normalized_role_title']
        and hire.company_stage == query['company_stage']
        and hire.geo_cluster == query['location']['cluster'],
        lambda hire, title_score: hire.normalized_role_title == query['normalized_role_title']
        and hire.company_stage == query['company_stage'],
        lambda hire, title_score: hire.function == query['function']
        and hire.company_stage == query['company_stage']
        and title_score >= 0.5,
        lambda hire, title_score: hire.function == query['function']
        and title_score >= 0.45,
        lambda hire, title_score: hire.function == query['function'],
    ]

    scored = []
    for hire in hires:
        score, title_score = score_hire(hire, query)
        scored.append((hire, score, title_score))

    for tier_index, matcher in enumerate(tiers, start=1):
        sample = [item for item in scored if matcher(item[0], item[2])]
        sample.sort(key=lambda item: (-item[1], item[0].source_row_index))
        if len(sample) >= 5 or tier_index == len(tiers):
            return tier_index, sample[:18]
    return len(tiers), []


def build_benchmark(query):
    tier, sample = select_benchmark_sample(query)
    costs = [item[0].cost_per_hire_usd for item in sample]
    sample_size = len(sample)
    low = quantile(costs, 0.25) if costs else 0
    med = int(median(costs)) if costs else 0
    high = quantile(costs, 0.75) if costs else 0
    comparables = []
    for hire, score, _title_score in sample[:5]:
        comparables.append(
            {
                'roleTitle': hire.role_title,
                'costPerHire': hire.cost_per_hire_display,
                'companyStage': hire.company_stage,
                'companyLocation': hire.company_location,
                'notableInvestors': hire.notable_investors,
                'score': round(score, 2),
            }
        )

    return {
        'tier': tier,
        'sampleSize': sample_size,
        'confidenceLabel': confidence_label(tier, sample_size),
        'low': format_currency(low) if low else '$0',
        'median': format_currency(med) if med else '$0',
        'high': format_currency(high) if high else '$0',
        'lowUsd': low,
        'medianUsd': med,
        'highUsd': high,
        'comparables': comparables,
    }


def score_recruiter(recruiter, query):
    score = 0
    if query['function'] in recruiter.functions:
        score += 4
    if query['company_stage'] in recruiter.stage_focus:
        score += 3
    if query['location']['cluster'] in recruiter.geo_focus or 'Remote' in recruiter.geo_focus:
        score += 2
    if query['hiring_priority'] in recruiter.hiring_priority_focus:
        score += 2
    if any(keyword in recruiter.sample_role.lower() for keyword in query['normalized_role_title'].split()):
        score += 1
    return score


def build_recruiter_matches(query):
    recruiters = list(RecruiterProfile.objects.all())
    ranked = sorted(
        recruiters,
        key=lambda recruiter: (-score_recruiter(recruiter, query), recruiter.name),
    )
    cards = []
    for recruiter in ranked[:3]:
        cards.append(
            {
                'name': recruiter.name,
                'location': recruiter.location,
                'yearsExperience': recruiter.years_experience,
                'headline': recruiter.headline,
                'bio': recruiter.bio,
                'sampleRole': recruiter.sample_role,
                'sampleCost': recruiter.sample_cost_display,
                'sampleStage': recruiter.sample_stage,
                'accent': recruiter.accent,
            }
        )
    return cards


def build_route_recommendation(query, benchmark):
    reasons = []
    if query['company_stage'] in {'Pre-seed', 'Seed', 'Series A'}:
        reasons.append('Early-stage teams usually benefit most from an embedded recruiter who can shape the brief, not just source against it.')
    if query['hiring_priority'] in {'Need process help', 'Need full-cycle recruiter'}:
        reasons.append('This brief points toward hands-on marketplace support instead of a narrow sourcing-only engagement.')
    if benchmark['sampleSize'] >= 5:
        reasons.append('Dover already has enough comparable marketplace hires to anchor the search in real cost expectations.')
    else:
        reasons.append('The market signal here is thinner, so the best path is a scoped marketplace search with a wider comparison set.')

    if query['company_stage'] == 'Series C+' and query['hiring_priority'] == 'Need pipeline':
        label = 'Hybrid route'
        detail = 'Use Dover for specialist search support while keeping your internal team in the driver seat.'
    else:
        label = 'Use Dover marketplace'
        detail = 'A fractional recruiter is the fastest path to calibrated, embedded execution for this hire.'

    return {'label': label, 'detail': detail, 'reasons': reasons}


def build_summary(query, benchmark):
    location = query['location']['cluster'] or query['location']['display'] or 'the market'
    return (
        f"{query['company_stage']} {query['function'].lower()} hiring in {location} is clustering around "
        f"{benchmark['median']} on Dover's marketplace. The strongest move is a self-serve estimate first, "
        "then an embedded recruiter match if you need speed plus process ownership."
    )


def build_planner_response(payload):
    query = build_query(payload)
    benchmark = build_benchmark(query)
    return {
        'query': {
            'roleTitle': query['role_title'],
            'companyStage': query['company_stage'],
            'companyLocation': query['location']['display'] or 'Remote',
            'function': query['function'],
            'hiringPriority': query['hiring_priority'],
            'optionalContext': query['optional_context'],
        },
        'benchmark': benchmark,
        'recruiters': build_recruiter_matches(query),
        'routeRecommendation': build_route_recommendation(query, benchmark),
        'summary': build_summary(query, benchmark),
        'methodology': (
            "Benchmarks come from 901 real Dover marketplace hires. The planner prioritizes comparable roles "
            "by function, company stage, and location, then widens the sample when exact matches are sparse."
        ),
    }
