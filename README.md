# StudyRad

> Meet your study group. A Discord-style platform where students find rooms and buddies who share their study interests.

## Table of contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Architecture](#architecture)
- [Data model](#data-model)
- [Getting started](#getting-started)
- [Configuration](#configuration)
- [REST API](#rest-api)
- [Testing](#testing)
- [CI/CD](#cicd)
- [Project structure](#project-structure)
- [Roadmap](#roadmap)


## Features

- **Study rooms**: create a room under a topic, with you as the host.
- **Topics**: browse rooms by topic from the sidebar.
- **Messaging**: post and delete messages inside a room. Commenting automatically adds you to the room's participants.
- **Recent activity feed**: latest messages across rooms.
- **Search**: one search bar matching room name, description and topic (Django `Q` objects).
- **Accounts**: register, log in and log out; decorator-based authorisation protects create, edit and delete actions.
- **Profiles**: custom user model with editable profile and photo upload.
- **Responsive UI**: works on mobile; flash messages for user feedback.
- **REST API**: Django REST Framework endpoints for study rooms and their content, with CORS enabled.
- **Containerised**: runs in Docker.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12+, Django 6, Django REST Framework, django-filter |
| Database | SQLite |
| Frontend | Django templates, HTML, CSS, JavaScript |
| Media | Pillow (profile photos) |
| API extras | django-cors-headers |
| Tooling | Docker, pytest, GitHub Actions |

## Architecture

StudyRad follows a three-tier layout.

```
Browser / API client
        |
Presentation   Django templates  +  DRF serializers / viewsets
        |
Application    Django views, permissions, service functions
        |
Data           Django ORM models  ->  SQLite
```

Requests to the project's `urls.py` are routed to the `base` app, which owns the models, views, templates and the API.


## Data model

```
User (custom)     extends AbstractUser (username login) + name, email (unique), bio, avatar
Topic             name
Room              host -> User, topic -> Topic, name, description,
                  participants <-> User (many-to-many), created, updated
Message           user -> User, room -> Room, body, created, updated
```

Each room has one topic and one host (both nullable: deleting a user or topic keeps the room). Any participant can post messages in a room.


## Getting started

### Option 1: Docker

```bash
git clone https://github.com/sougandhini/StudyRad.git
cd StudyRad
# create a .env file with the variables listed under Configuration
docker build -t studyrad ./studyrad
docker run --rm -p 8000:8000 --env-file .env studyrad
```

Open http://localhost:8000.

### Option 2: Local

Requires Python 3.12 or newer (Django 6.x).

```bash
git clone https://github.com/sougandhini/StudyRad.git
cd StudyRad/studyrad            # the folder that contains manage.py
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```


## ## Configuration

Settings are read from environment variables (copy `.env.example` to `.env`).

| Variable | Purpose | Example |
|---|---|---|
| `DJANGO_SECRET_KEY` | Django secret key | a long random string |
| `DEBUG` | Debug mode (default `True`) | `False` in production |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |

## REST API

Base path: `/api/v1/` (browsable API root at `/api/v1/`). The original read-only endpoints under `/studyrad/` are legacy and will be retired. OpenAPI/Swagger docs are on the roadmap.

Conventions: JSON everywhere; one error envelope `{"error": {"status": 400, "details": {...}}}`; list endpoints are paginated and bounded (`page_size` max 50).

| Status | Method and path | Description | Auth |
|---|---|---|---|
| Planned | `GET /topics/` | List topics with room counts; `search`, `ordering` | Public |
| Planned | `GET /rooms/` | List rooms; filters `topic`, `host`, `mine`, `created_after`, `min_participants`; `search`, `ordering`, `page`, `page_size` | Public |
| Planned | `POST /rooms/` | Create a room (host is the caller) | Required |
| Planned | `GET /rooms/{id}/` | Room detail with participants | Public |
| Planned | `PATCH`, `DELETE /rooms/{id}/` | Update or delete a room | Host only |
| Planned | `POST /rooms/{id}/join/`, `POST /rooms/{id}/leave/` | Join or leave a room (idempotent) | Required |
| Planned | `GET`, `POST /rooms/{id}/messages/` | Cursor-paginated messages; post a message | Read public, write required |
| Planned | `PATCH`, `DELETE /messages/{id}/` | Edit within 15 minutes, delete | Author (delete: author or host) |
| Planned | `POST /auth/register/`, `/auth/token/`, `/auth/token/refresh/`, `/auth/logout/` | JWT authentication | Public |
| Planned | `GET`, `PATCH /users/me/`, `GET /users/{id}/` | Own profile, public profile | Required / Public |
| Planned | `GET /feed/` | Recent messages from joined rooms | Required |
| Planned | `GET /rooms/recommended/`, `GET /users/buddies/`, `GET /stats/` | Discovery | Required / Public |

Flip the Status column to `Done` as you ship each endpoint, and tick the roadmap boxes below.

Example:

```bash
curl "http://localhost:8000/api/v1/rooms/?topic=python&ordering=-participants_count&page_size=5"
```

```json
{
  "count": 12,
  "next": "http://localhost:8000/api/v1/rooms/?page=2&page_size=5&topic=python",
  "previous": null,
  "results": [
    {
      "id": 7,
      "name": "Data structures",
      "topic": {"id": 2, "name": "Python"},
      "host": {"id": 3, "name": "asha"},
      "participants_count": 14,
      "created": "2026-10-01T09:30:00Z"
    }
  ]
}
```

## Testing

Tests use `pytest`, `pytest-django`, `factory-boy` and `pytest-cov`.

```bash
pytest                              # run everything with coverage
pytest base/tests/api/test_rooms.py # one module (run from the folder with manage.py)
pytest --cov-report=html            # open htmlcov/index.html
```

What is covered for each API: success paths, validation errors, authentication (401), permissions (403), not-found (404), pagination, filtering, search, ordering, query-count budgets and side effects. CI fails if coverage drops below the configured threshold.

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`) runs on every push and pull request:

1. **lint**: `ruff check`
2. **test**: migrations check and `pytest` with coverage on Python 3.12 and 3.13
3. **docker**: builds the image; on pushes to `main` it publishes to GitHub Container Registry (`ghcr.io/sougandhini/studyrad`)

Run the published image:

```bash
docker run --rm -p 8000:8000 --env-file .env ghcr.io/sougandhini/studyrad:main
```

## Project structure

```
StudyRad/
├── .github/workflows/ci.yml
└── studyrad/                 # Django project root (contains manage.py)
    ├── Dockerfile  requirements.txt  requirements-dev.txt  pytest.ini  ruff.toml
    ├── studyrad/             # settings, root urls, wsgi
    └── base/
        ├── models.py  views.py  urls.py  forms.py
        ├── templates/  static/
        ├── api/              # legacy v0 read-only endpoints
        ├── api/v1/           # serializers, viewsets, permissions, filters, pagination
        └── tests/            # factories, conftest, api tests
```

## Roadmap

- [x] Core platform: rooms, topics, messages, search, auth, profiles
- [x] Docker
- [ ] DRF v1 Topics and Rooms: pagination, filtering, search, ordering, permissions
- [ ] DRF v1 membership and messages
- [ ] Automated tests for the v1 API with a coverage gate (extend to the template views)
- [ ] GitHub Actions CI and image publishing
- [ ] JWT auth, feed and recommendations endpoints
- [ ] Deployment to a cloud platform

