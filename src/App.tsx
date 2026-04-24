import { FormEvent, useEffect, useMemo, useState } from 'react';

type PlannerOptions = {
  stages: string[];
  functions: string[];
  priorities: string[];
  featuredCities: string[];
  exampleRoles: string[];
};

type ComparableHire = {
  roleTitle: string;
  costPerHire: string;
  companyStage: string;
  companyLocation: string;
  notableInvestors: string;
  score: number;
};

type Benchmark = {
  sampleSize: number;
  confidenceLabel: string;
  low: string;
  median: string;
  high: string;
  comparables: ComparableHire[];
};

type RecruiterMatch = {
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

type PlannerResult = {
  query: {
    roleTitle: string;
    companyStage: string;
    companyLocation: string;
    function: string;
    hiringPriority: string;
    optionalContext: string;
  };
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

type PlannerForm = {
  roleTitle: string;
  companyStage: string;
  companyLocation: string;
  function: string;
  hiringPriority: string;
  optionalContext: string;
};

const defaultOptions: PlannerOptions = {
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

const initialForm: PlannerForm = {
  roleTitle: 'Founding engineer',
  companyStage: 'Seed',
  companyLocation: 'San Francisco, CA',
  function: 'Engineering',
  hiringPriority: 'Need full-cycle recruiter',
  optionalContext:
    'Founder-led search. Need someone who can help shape the brief, build pipeline, and keep process tight.',
};

const accentClass: Record<string, string> = {
  forest: 'badge-forest',
  navy: 'badge-navy',
  gold: 'badge-gold',
  violet: 'badge-violet',
  sky: 'badge-sky',
  rose: 'badge-rose',
};

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export default function App() {
  const [plannerOptions, setPlannerOptions] = useState<PlannerOptions>(defaultOptions);
  const [form, setForm] = useState<PlannerForm>(initialForm);
  const [result, setResult] = useState<PlannerResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [methodologyOpen, setMethodologyOpen] = useState(false);

  useEffect(() => {
    fetchJson<PlannerOptions>('/api/options/')
      .then(setPlannerOptions)
      .catch(() => {
        // Keep sensible defaults if the API is not up yet.
      });
  }, []);

  useEffect(() => {
    void submitPlanner(initialForm);
  }, []);

  async function submitPlanner(nextForm: PlannerForm) {
    setLoading(true);
    setError(null);
    try {
      const plannerResult = await fetchJson<PlannerResult>('/api/planner/', {
        method: 'POST',
        body: JSON.stringify(nextForm),
      });
      setResult(plannerResult);
    } catch (submitError) {
      setError('The planner could not load a result. Make sure the Django API is running on port 8000.');
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void submitPlanner(form);
  }

  const stageLabel = useMemo(
    () => `${form.companyStage} startup${form.companyStage === 'Series C+' ? '' : ''}`,
    [form.companyStage],
  );

  return (
    <main className="app-shell">
      <section className="hero-grid">
        <div className="hero-copy">
          <div className="eyebrow">Dover Hiring Planner</div>
          <h1>Self-serve planning for your next critical hire.</h1>
          <p className="hero-body">
            Turn Dover&rsquo;s marketplace data into a real decision: expected cost, comparable hires,
            and the recruiter profile most likely to help you move fast.
          </p>
          <div className="hero-metrics">
            <div className="metric-card">
              <span className="metric-label">Marketplace hires</span>
              <strong>901</strong>
            </div>
            <div className="metric-card">
              <span className="metric-label">Recruiter network</span>
              <strong>60+</strong>
            </div>
            <div className="metric-card">
              <span className="metric-label">Use case</span>
              <strong>Founder-first</strong>
            </div>
          </div>
        </div>

        <form className="planner-panel" onSubmit={handleSubmit}>
          <div className="panel-header">
            <div>
              <p className="panel-kicker">What are you hiring for?</p>
              <h2>Build a hiring plan in under a minute.</h2>
            </div>
            <button type="submit" className="primary-button" disabled={loading}>
              {loading ? 'Planning…' : 'See my hiring plan'}
            </button>
          </div>

          <label className="field">
            <span>Role</span>
            <input
              value={form.roleTitle}
              onChange={(event) => setForm((current) => ({ ...current, roleTitle: event.target.value }))}
              placeholder="Founding engineer"
            />
          </label>

          <div className="field-grid">
            <label className="field">
              <span>Stage</span>
              <select
                value={form.companyStage}
                onChange={(event) =>
                  setForm((current) => ({ ...current, companyStage: event.target.value }))
                }
              >
                {plannerOptions.stages.map((stage) => (
                  <option key={stage} value={stage}>
                    {stage}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Function</span>
              <select
                value={form.function}
                onChange={(event) => setForm((current) => ({ ...current, function: event.target.value }))}
              >
                {plannerOptions.functions.map((functionOption) => (
                  <option key={functionOption} value={functionOption}>
                    {functionOption}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="field-grid">
            <label className="field">
              <span>Location</span>
              <input
                list="featured-cities"
                value={form.companyLocation}
                onChange={(event) =>
                  setForm((current) => ({ ...current, companyLocation: event.target.value }))
                }
                placeholder="San Francisco, CA"
              />
              <datalist id="featured-cities">
                {plannerOptions.featuredCities.map((city) => (
                  <option key={city} value={city} />
                ))}
              </datalist>
            </label>

            <label className="field">
              <span>Need most help with</span>
              <select
                value={form.hiringPriority}
                onChange={(event) =>
                  setForm((current) => ({ ...current, hiringPriority: event.target.value }))
                }
              >
                {plannerOptions.priorities.map((priority) => (
                  <option key={priority} value={priority}>
                    {priority}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <label className="field">
            <span>Context</span>
            <textarea
              value={form.optionalContext}
              onChange={(event) =>
                setForm((current) => ({ ...current, optionalContext: event.target.value }))
              }
              rows={4}
              placeholder="What makes this hire hard? What do you already know? Where do you need leverage?"
            />
          </label>

          <div className="chip-row">
            {plannerOptions.exampleRoles.map((exampleRole) => (
              <button
                type="button"
                key={exampleRole}
                className="chip"
                onClick={() => setForm((current) => ({ ...current, roleTitle: exampleRole }))}
              >
                {exampleRole}
              </button>
            ))}
          </div>
        </form>
      </section>

      {error ? <div className="error-banner">{error}</div> : null}

      {result ? (
        <section className="results-grid">
          <div className="results-stack">
            <article className="summary-card">
              <div>
                <p className="summary-label">Hiring plan</p>
                <h3>
                  {result.query.roleTitle} for a {stageLabel.toLowerCase()} in {result.query.companyLocation}
                </h3>
              </div>
              <p>{result.summary}</p>
              <button
                type="button"
                className="ghost-button"
                onClick={() => setMethodologyOpen((current) => !current)}
              >
                {methodologyOpen ? 'Hide methodology' : 'Why this benchmark'}
              </button>
              {methodologyOpen ? <p className="methodology-copy">{result.methodology}</p> : null}
            </article>

            <div className="benchmark-grid">
              <article className="benchmark-hero">
                <p className="summary-label">Expected cost</p>
                <div className="benchmark-number">{result.benchmark.median}</div>
                <p className="benchmark-caption">
                  Median marketplace cost for this search profile
                </p>
                <div className="range-bar">
                  <span>{result.benchmark.low}</span>
                  <span>{result.benchmark.high}</span>
                </div>
              </article>

              <article className="mini-stat">
                <span className="mini-label">Confidence</span>
                <strong>{result.benchmark.confidenceLabel}</strong>
              </article>

              <article className="mini-stat">
                <span className="mini-label">Sample size</span>
                <strong>{result.benchmark.sampleSize} hires</strong>
              </article>

              <article className="mini-stat">
                <span className="mini-label">Priority</span>
                <strong>{result.query.hiringPriority}</strong>
              </article>
            </div>

            <article className="table-card">
              <div className="section-heading">
                <div>
                  <p className="summary-label">Comparable hires</p>
                  <h3>Closest marketplace signals</h3>
                </div>
                <span className="trust-pill">Real Dover marketplace data</span>
              </div>

              <div className="comparables-list">
                {result.benchmark.comparables.map((comparable) => (
                  <div key={`${comparable.roleTitle}-${comparable.companyLocation}-${comparable.costPerHire}`} className="comparable-row">
                    <div>
                      <strong>{comparable.roleTitle}</strong>
                      <p>
                        {comparable.companyStage} • {comparable.companyLocation}
                      </p>
                    </div>
                    <div className="comparable-meta">
                      <strong>{comparable.costPerHire}</strong>
                      <span>{comparable.notableInvestors}</span>
                    </div>
                  </div>
                ))}
              </div>
            </article>
          </div>

          <aside className="sidebar-stack">
            <article className="route-card">
              <p className="summary-label">Recommended route</p>
              <h3>{result.routeRecommendation.label}</h3>
              <p>{result.routeRecommendation.detail}</p>
              <ul className="reason-list">
                {result.routeRecommendation.reasons.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
              <a className="primary-link" href="https://www.dover.com/marketplace" target="_blank" rel="noreferrer">
                Access recruiter marketplace
              </a>
            </article>

            <article className="matches-card">
              <div className="section-heading compact">
                <div>
                  <p className="summary-label">Best recruiter fit</p>
                  <h3>Who should help first</h3>
                </div>
              </div>

              <div className="recruiter-list">
                {result.recruiters.map((recruiter) => (
                  <article className="recruiter-card" key={recruiter.name}>
                    <div className="recruiter-top">
                      <div className={`avatar-badge ${accentClass[recruiter.accent] ?? 'badge-forest'}`}>
                        {recruiter.name
                          .split(' ')
                          .map((part) => part[0])
                          .join('')
                          .slice(0, 2)}
                      </div>
                      <div>
                        <h4>{recruiter.name}</h4>
                        <p>
                          {recruiter.yearsExperience} years • {recruiter.location}
                        </p>
                      </div>
                    </div>
                    <p className="recruiter-headline">{recruiter.headline}</p>
                    <p className="recruiter-bio">{recruiter.bio}</p>
                    <div className="recruiter-sample">
                      Recent signal: {recruiter.sampleStage} team spent {recruiter.sampleCost} on{' '}
                      {recruiter.sampleRole}.
                    </div>
                  </article>
                ))}
              </div>
            </article>
          </aside>
        </section>
      ) : (
        <section className="empty-state">
          <p>Planner results will appear here once the first request completes.</p>
        </section>
      )}
    </main>
  );
}
