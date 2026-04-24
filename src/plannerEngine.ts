import benchmarkHires from './data/benchmarkHires.json';
import recruiters from './data/recruiters.json';

export type PlannerOptions = {
  stages: string[];
  functions: string[];
  priorities: string[];
  featuredCities: string[];
  exampleRoles: string[];
};

export type PlannerForm = {
  roleTitle: string;
  companyStage: string;
  companyLocation: string;
  function: string;
  hiringPriority: string;
  optionalContext: string;
};

export type ComparableHire = {
  roleTitle: string;
  costPerHire: string;
  companyStage: string;
  companyLocation: string;
  notableInvestors: string;
  score: number;
};

export type Benchmark = {
  sampleSize: number;
  confidenceLabel: string;
  low: string;
  median: string;
  high: string;
  comparables: ComparableHire[];
};

export type RecruiterMatch = {
  name: string;
  location: string;
  yearsExperience: number;
  headline: string;
  bio: string;
  sampleRole: string;
  sampleCost: string;
  sampleStage: string;
  accent: string;
};

export type PlannerResult = {
  query: PlannerForm;
  benchmark: Benchmark;
  recruiters: RecruiterMatch[];
  routeRecommendation: {
    label: string;
    detail: string;
    reasons: string[];
  };
  summary: string;
  methodology: string;
};

type BenchmarkHireRecord = {
  sourceRowIndex: number;
  roleTitle: string;
  normalizedRoleTitle: string;
  function: string;
  seniority: string;
  costPerHireUsd: number;
  costPerHireDisplay: string;
  companyStage: string;
  stageRank: number;
  companyLocation: string;
  normalizedCity: string;
  normalizedRegion: string;
  geoCluster: string;
  notableInvestors: string;
  recruiterName: string;
};

type RecruiterSeedRecord = {
  slug: string;
  name: string;
  location: string;
  years_experience: number;
  headline: string;
  bio: string;
  functions: string[];
  stage_focus: string[];
  geo_focus: string[];
  hiring_priority_focus: string[];
  sample_role: string;
  sample_cost_display: string;
  sample_stage: string;
  accent: string;
};

const hires = benchmarkHires as BenchmarkHireRecord[];
const recruiterSeeds = recruiters as RecruiterSeedRecord[];

const stageOrder: Record<string, number> = {
  'Pre-seed': 0,
  Seed: 1,
  'Series A': 2,
  'Series B': 3,
  'Series C+': 4,
};

const functionKeywords: Record<string, string[]> = {
  Engineering: [
    'engineer',
    'developer',
    'software',
    'frontend',
    'backend',
    'full stack',
    'fullstack',
    'ios',
    'android',
    'platform',
    'devops',
    'security',
    'research',
    'ml',
    'ai',
    'blockchain',
  ],
  GTM: [
    'account executive',
    'sales',
    'growth',
    'marketing',
    'customer success',
    'demand generation',
    'revenue',
    'partnership',
    'success manager',
    'bdr',
    'sdr',
    'community',
  ],
  Product: ['product manager', 'product', 'developer relations', 'founder associate'],
  Design: ['designer', 'design', 'ux', 'brand', 'creative'],
  People: ['recruiter', 'talent', 'people', 'hr', 'human resources', 'mentor', 'therapist'],
  Clinical: ['clinical', 'epic', 'ehr', 'health', 'therapist', 'scientist'],
  Ops: ['operations', 'ops', 'chief of staff', 'finance', 'counsel', 'analyst', 'implementation', 'support'],
};

const cityClusters: Record<string, string[]> = {
  'Bay Area': ['san francisco', 'oakland', 'berkeley'],
  'New York City': ['new york', 'brooklyn', 'glen cove'],
  Boston: ['boston', 'cambridge'],
  Remote: ['remote'],
  Austin: ['austin'],
};

export const plannerOptions: PlannerOptions = {
  stages: ['Pre-seed', 'Seed', 'Series A', 'Series B', 'Series C+'],
  functions: ['Engineering', 'GTM', 'Product', 'Design', 'Ops', 'People', 'Clinical', 'Other'],
  priorities: [
    'Need pipeline',
    'Need process help',
    'Need full-cycle recruiter',
    'Need a specialist search',
    'Not sure',
  ],
  featuredCities: ['San Francisco, CA', 'New York, NY', 'Boston, MA', 'Austin, TX', 'Remote'],
  exampleRoles: [
    'Founding engineer',
    'Senior backend engineer',
    'Enterprise account executive',
    'Product designer',
    'Customer success manager',
  ],
};

function normalizeWhitespace(value: string) {
  return value.replace(/\s+/g, ' ').trim();
}

function normalizeText(value: string) {
  return normalizeWhitespace(
    value
      .toLowerCase()
      .replaceAll('&', ' and ')
      .replace(/[^a-z0-9+ ]/g, ' '),
  );
}

function normalizeStage(stage: string) {
  const normalized = normalizeText(stage);
  if (normalized === 'pre seed') return 'Pre-seed';
  if (normalized === 'seed') return 'Seed';
  if (normalized === 'series a') return 'Series A';
  if (normalized === 'series b') return 'Series B';
  if (['series c', 'series c+', 'series d', 'public company'].includes(normalized)) return 'Series C+';
  return 'Seed';
}

function normalizeRoleTitle(title: string) {
  return normalizeWhitespace(
    normalizeText(title)
      .replaceAll('full stack', 'fullstack')
      .replaceAll('swe', 'software engineer')
      .replaceAll('ae', 'account executive')
      .replaceAll('sr ', 'senior '),
  );
}

function inferFunction(title: string) {
  const normalized = normalizeRoleTitle(title);
  for (const [functionName, keywords] of Object.entries(functionKeywords)) {
    if (keywords.some((keyword) => normalized.includes(keyword))) {
      return functionName;
    }
  }
  return 'Other';
}

function normalizeLocation(location: string) {
  const clean = normalizeWhitespace(location);
  if (!clean || clean.toLowerCase() === 'remote') {
    return { display: clean || 'Remote', city: 'Remote', region: 'Remote', cluster: 'Remote' };
  }

  const parts = clean.split(',').map((part) => normalizeWhitespace(part));
  const city = parts[0] ?? '';
  const region = parts[1] ?? '';
  const cityKey = city.toLowerCase();
  let cluster = region || city;

  for (const [clusterName, cities] of Object.entries(cityClusters)) {
    if (cities.includes(cityKey)) {
      cluster = clusterName;
      break;
    }
  }

  if (region === 'Canada') {
    cluster = 'Remote';
  }

  return { display: clean, city, region, cluster };
}

function sequenceSimilarity(left: string, right: string) {
  const a = normalizeRoleTitle(left);
  const b = normalizeRoleTitle(right);
  if (!a || !b) return 0;
  if (a === b) return 1;

  const leftWords = new Set(a.split(' '));
  const rightWords = new Set(b.split(' '));
  let intersection = 0;
  leftWords.forEach((word) => {
    if (rightWords.has(word)) intersection += 1;
  });
  const overlap = intersection / Math.max(leftWords.size, rightWords.size);
  const substringBoost = a.includes(b) || b.includes(a) ? 0.18 : 0;
  return Math.min(1, overlap + substringBoost);
}

function formatCurrency(value: number) {
  return `${(value / 1000).toFixed(1).replace(/\.0$/, '')}K`.replace(/^/, '$');
}

function quantile(values: number[], ratio: number) {
  const ordered = [...values].sort((left, right) => left - right);
  if (!ordered.length) return 0;
  const index = Math.round((ordered.length - 1) * ratio);
  return ordered[index];
}

function confidenceLabel(tier: number, sampleSize: number) {
  if (tier <= 2 && sampleSize >= 8) return 'High confidence';
  if (sampleSize >= 5) return 'Good directional read';
  return 'Low-sample estimate';
}

function scoreHire(hire: BenchmarkHireRecord, query: ReturnType<typeof buildQuery>) {
  let score = 0;
  const titleScore = sequenceSimilarity(hire.roleTitle, query.roleTitle);
  score += titleScore * 4;
  if (hire.function === query.function) score += 2.5;
  const stageGap = Math.abs(hire.stageRank - query.stageRank);
  score += Math.max(0, 1.8 - stageGap * 0.7);

  if (hire.geoCluster === query.location.cluster) score += 1.6;
  else if (hire.normalizedRegion && hire.normalizedRegion === query.location.region) score += 0.8;
  else if (query.location.cluster === 'Remote' || hire.geoCluster === 'Remote') score += 0.4;

  return { score: Number(score.toFixed(4)), titleScore };
}

function buildQuery(form: PlannerForm) {
  const roleTitle = form.roleTitle.trim() || 'Founding engineer';
  const companyStage = normalizeStage(form.companyStage || 'Seed');
  const location = normalizeLocation(form.companyLocation || 'Remote');
  const inferredFunction = inferFunction(roleTitle);
  const selectedFunction = form.function === 'Other' ? inferredFunction : form.function || inferredFunction;

  return {
    roleTitle,
    normalizedRoleTitle: normalizeRoleTitle(roleTitle),
    companyStage,
    stageRank: stageOrder[companyStage],
    location,
    function: selectedFunction,
    hiringPriority: form.hiringPriority || 'Not sure',
    optionalContext: form.optionalContext.trim(),
  };
}

function selectBenchmarkSample(query: ReturnType<typeof buildQuery>) {
  const scored = hires.map((hire) => {
    const { score, titleScore } = scoreHire(hire, query);
    return { hire, score, titleScore };
  });

  const tiers = [
    (entry: typeof scored[number]) =>
      entry.hire.normalizedRoleTitle === query.normalizedRoleTitle &&
      entry.hire.companyStage === query.companyStage &&
      entry.hire.geoCluster === query.location.cluster,
    (entry: typeof scored[number]) =>
      entry.hire.normalizedRoleTitle === query.normalizedRoleTitle &&
      entry.hire.companyStage === query.companyStage,
    (entry: typeof scored[number]) =>
      entry.hire.function === query.function &&
      entry.hire.companyStage === query.companyStage &&
      entry.titleScore >= 0.5,
    (entry: typeof scored[number]) => entry.hire.function === query.function && entry.titleScore >= 0.45,
    (entry: typeof scored[number]) => entry.hire.function === query.function,
  ];

  for (let index = 0; index < tiers.length; index += 1) {
    const sample = scored
      .filter(tiers[index])
      .sort((left, right) => right.score - left.score || left.hire.sourceRowIndex - right.hire.sourceRowIndex)
      .slice(0, 18);

    if (sample.length >= 5 || index === tiers.length - 1) {
      return { tier: index + 1, sample };
    }
  }

  return { tier: tiers.length, sample: [] as typeof scored };
}

function buildBenchmark(query: ReturnType<typeof buildQuery>): Benchmark & { tier: number; lowUsd: number; medianUsd: number; highUsd: number } {
  const { tier, sample } = selectBenchmarkSample(query);
  const costs = sample.map((entry) => entry.hire.costPerHireUsd);
  const low = quantile(costs, 0.25);
  const median = quantile(costs, 0.5);
  const high = quantile(costs, 0.75);

  return {
    tier,
    sampleSize: sample.length,
    confidenceLabel: confidenceLabel(tier, sample.length),
    low: formatCurrency(low),
    median: formatCurrency(median),
    high: formatCurrency(high),
    lowUsd: low,
    medianUsd: median,
    highUsd: high,
    comparables: sample.slice(0, 5).map((entry) => ({
      roleTitle: entry.hire.roleTitle,
      costPerHire: entry.hire.costPerHireDisplay,
      companyStage: entry.hire.companyStage,
      companyLocation: entry.hire.companyLocation,
      notableInvestors: entry.hire.notableInvestors,
      score: Number(entry.score.toFixed(2)),
    })),
  };
}

function scoreRecruiter(recruiter: RecruiterSeedRecord, query: ReturnType<typeof buildQuery>) {
  let score = 0;
  if (recruiter.functions.includes(query.function)) score += 4;
  if (recruiter.stage_focus.includes(query.companyStage)) score += 3;
  if (recruiter.geo_focus.includes(query.location.cluster) || recruiter.geo_focus.includes('Remote')) score += 2;
  if (recruiter.hiring_priority_focus.includes(query.hiringPriority)) score += 2;
  const keywords = query.normalizedRoleTitle.split(' ');
  if (keywords.some((keyword) => recruiter.sample_role.toLowerCase().includes(keyword))) score += 1;
  return score;
}

function buildRecruiterMatches(query: ReturnType<typeof buildQuery>): RecruiterMatch[] {
  return [...recruiterSeeds]
    .sort((left, right) => scoreRecruiter(right, query) - scoreRecruiter(left, query) || left.name.localeCompare(right.name))
    .slice(0, 3)
    .map((recruiter) => ({
      name: recruiter.name,
      location: recruiter.location,
      yearsExperience: recruiter.years_experience,
      headline: recruiter.headline,
      bio: recruiter.bio,
      sampleRole: recruiter.sample_role,
      sampleCost: recruiter.sample_cost_display,
      sampleStage: recruiter.sample_stage,
      accent: recruiter.accent,
    }));
}

function buildRouteRecommendation(query: ReturnType<typeof buildQuery>, benchmark: ReturnType<typeof buildBenchmark>) {
  const reasons: string[] = [];

  if (['Pre-seed', 'Seed', 'Series A'].includes(query.companyStage)) {
    reasons.push('Early-stage teams usually benefit most from an embedded recruiter who can shape the brief, not just source against it.');
  }
  if (['Need process help', 'Need full-cycle recruiter'].includes(query.hiringPriority)) {
    reasons.push('This brief points toward hands-on marketplace support instead of a narrow sourcing-only engagement.');
  }
  if (benchmark.sampleSize >= 5) {
    reasons.push('Dover already has enough comparable marketplace hires to anchor the search in real cost expectations.');
  } else {
    reasons.push('The market signal here is thinner, so the best path is a scoped marketplace search with a wider comparison set.');
  }

  if (query.companyStage === 'Series C+' && query.hiringPriority === 'Need pipeline') {
    return {
      label: 'Hybrid route',
      detail: 'Use Dover for specialist search support while keeping your internal team in the driver seat.',
      reasons,
    };
  }

  return {
    label: 'Use Dover marketplace',
    detail: 'A fractional recruiter is the fastest path to calibrated, embedded execution for this hire.',
    reasons,
  };
}

function buildSummary(query: ReturnType<typeof buildQuery>, benchmark: ReturnType<typeof buildBenchmark>) {
  const location = query.location.cluster || query.location.display || 'the market';
  return `${query.companyStage} ${query.function.toLowerCase()} hiring in ${location} is clustering around ${benchmark.median} on Dover's marketplace. The strongest move is a self-serve estimate first, then an embedded recruiter match if you need speed plus process ownership.`;
}

export function planHiring(form: PlannerForm): PlannerResult {
  const query = buildQuery(form);
  const benchmark = buildBenchmark(query);

  return {
    query: {
      roleTitle: query.roleTitle,
      companyStage: query.companyStage,
      companyLocation: query.location.display || 'Remote',
      function: query.function,
      hiringPriority: query.hiringPriority,
      optionalContext: query.optionalContext,
    },
    benchmark,
    recruiters: buildRecruiterMatches(query),
    routeRecommendation: buildRouteRecommendation(query, benchmark),
    summary: buildSummary(query, benchmark),
    methodology:
      "Benchmarks come from 901 real Dover marketplace hires. The planner prioritizes comparable roles by function, company stage, and location, then widens the sample when exact matches are sparse.",
  };
}
