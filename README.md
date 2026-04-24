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

## Notes

- `.gitignore` excludes local databases, virtualenvs, build output, and `.env` files.
- The Django backend remains in the repo as the fuller-stack version of the planner.
