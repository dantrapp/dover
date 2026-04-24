# Dover Hiring Planner

A self-serve hiring planner inspired by Dover's marketplace.

The app helps a founder answer four questions before opening a search:
- what will this hire likely cost on Dover's marketplace
- what comparable searches look like
- who should help first
- whether Dover marketplace is the right route

The demo is built from Dover's real public `901`-row cost-per-hire dataset and deployed as a working full-stack app.

## Stack

- Frontend: React + Vite
- Backend: Django + Django REST Framework
- Database: Postgres
- Deployment: Vercel + Neon
- Data: CSV export of Dover's public Airtable data

## Local development

Install dependencies:

```bash
./venv/bin/pip install -r requirements.txt
npm install
```

Start the Django API:

```bash
./venv/bin/python backend/manage.py migrate
./venv/bin/python backend/manage.py bootstrap_planner
./venv/bin/python backend/manage.py runserver 127.0.0.1:8000
```

Start the frontend:

```bash
npm run dev
```

## Data refresh

Rescrape the Airtable source into [dover_cost_per_hire.csv](/Users/dt/Desktop/codex/dover/dover_cost_per_hire.csv):

```bash
./venv/bin/python scrape_dover.py
```

Re-export the frontend fallback data artifacts:

```bash
./venv/bin/python scripts/export_planner_data.py
```

## Environment

Copy [.env.example](/Users/dt/Desktop/codex/dover/.env.example) and provide:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `CORS_ALLOWED_ORIGINS`
- `DATABASE_URL`
- `DATABASE_SSLMODE`
- `VITE_API_BASE_URL`

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

The backend deploy runs migrations and imports the bundled dataset automatically via [backend/vercel.json](/Users/dt/Desktop/codex/dover/backend/vercel.json):

```json
"buildCommand": "python manage.py migrate && python manage.py bootstrap_planner"
```

That means Neon is populated on deploy without a separate manual import step.

## Notes

- `.gitignore` excludes local databases, virtualenvs, build output, and `.env` files.
- The shipped app is Django-backed. The frontend JSON planner remains as a fallback path if the API is unavailable.
