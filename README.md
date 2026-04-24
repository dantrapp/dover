# Dover Hiring Planner

A self-serve hiring planner inspired by Dover's marketplace.

The app helps a founder estimate:
- expected marketplace cost for a hire
- comparable recent hires
- likely recruiter fit
- whether Dover marketplace is the right route

The demo is built from the real public `901`-row cost-per-hire dataset.

## Stack

- Frontend: React + Vite
- Backend: Django + Django REST Framework
- Data: CSV export of Dover's public Airtable data

For the fastest public demo path, the current frontend can run fully client-side from generated JSON artifacts in `src/data/`.

## Local development

Frontend:

```bash
npm install
npm run dev
```

Backend:

```bash
./venv/bin/pip install -r requirements.txt
./venv/bin/python backend/manage.py migrate
./venv/bin/python backend/manage.py bootstrap_planner
./venv/bin/python backend/manage.py runserver 127.0.0.1:8000
```

## Data refresh

Rescrape the Airtable source:

```bash
./venv/bin/python scrape_dover.py
```

Re-export frontend data artifacts:

```bash
./venv/bin/python scripts/export_planner_data.py
```

## Environment

Copy `.env.example` and provide:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`

## Vercel deploy

Frontend project:

- root directory: `.`
- framework: Vite
- uses [vercel.json](/Users/dt/Desktop/codex/dover/vercel.json)
- env: `VITE_API_BASE_URL=https://your-backend-project.vercel.app`

Backend project:

- root directory: `backend`
- zero-config Django deployment on Vercel
- uses [backend/vercel.json](/Users/dt/Desktop/codex/dover/backend/vercel.json)
- envs:
  - `DJANGO_SECRET_KEY`
  - `DJANGO_DEBUG=false`
  - `DJANGO_ALLOWED_HOSTS=.vercel.app`
  - `DJANGO_CSRF_TRUSTED_ORIGINS=https://your-frontend-project.vercel.app`
  - `CORS_ALLOWED_ORIGINS=https://your-frontend-project.vercel.app`
  - `DATABASE_URL=postgresql://...`
  - `DATABASE_SSLMODE=require`

## Notes

- `.gitignore` excludes local databases, virtualenvs, build output, and `.env` files.
- The Django backend remains in the repo as the fuller-stack version of the planner.
