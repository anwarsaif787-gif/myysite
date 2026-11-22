# myysite — Sami Physiotherapy & Rehab. Center

Django 6.1 website for a physiotherapy clinic: services, testimonials, gallery,
blog, FAQ, contact form and appointment booking.

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo    # optional demo content
python manage.py runserver
```

Locally the project uses SQLite and the console email backend by default, so no
environment variables are required. Open http://127.0.0.1:8000 and the admin at
http://127.0.0.1:8000/admin (create a login with `python manage.py createsuperuser`).

## Environment variables

Copy `.env.example` for the full list. In production set:

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Django secret key (required) |
| `DEBUG` | `False` in production |
| `ALLOWED_HOSTS` | Comma-separated hosts, e.g. `.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated `https://...` origins |
| `DATABASE_URL` | PostgreSQL connection string |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | Gmail address + app password |
| `DEFAULT_FROM_EMAIL` | Sender address |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | R2/S3 credentials |
| `AWS_STORAGE_BUCKET_NAME` | R2/S3 bucket for uploaded media |
| `AWS_S3_ENDPOINT_URL` | R2 endpoint (leave blank for AWS S3) |
| `AWS_S3_REGION_NAME` | `auto` for R2 |
| `AWS_S3_CUSTOM_DOMAIN` | Optional public media domain |

Without `AWS_STORAGE_BUCKET_NAME`, uploaded media is written to local `media/`.

## Deploy to Render

1. Push this repo to GitHub.
2. In Render, create a **PostgreSQL** instance.
3. Create a **Web Service** from the repo (Python runtime):
   - Build command: `bash build.sh`
   - Start command: `gunicorn myysite.wsgi:application`
4. Add the environment variables above; set `DATABASE_URL` from the database.
5. The build script seeds demo content on the first deploy and creates an admin
   account automatically. The login is `admin`; the generated password is shown
   under the service's **Environment** tab as `DJANGO_SUPERUSER_PASSWORD`.

`render.yaml` can provision the web service and database automatically.

## Tests

```bash
python manage.py test
python manage.py check --deploy
```
