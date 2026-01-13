# Job Auto-Applier

A FastAPI-based automated system for monitoring company career pages, discovering job openings, and analyzing job relevance using AI.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Setup](#setup)
  - [Prerequisites](#prerequisites)
  - [Local Development](#local-development)
  - [Docker Deployment](#docker-deployment)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Request Flows](#request-flows)
- [Development](#development)
- [Roadmap](#roadmap)

---

## Overview

Job Auto-Applier automates the tedious process of monitoring multiple company career pages for new job openings. It uses browser automation (Playwright) to scrape career pages and AI (Google Gemini) to analyze job matches against your profile.

### Key Capabilities

| Capability                 | Description                                           |
| -------------------------- | ----------------------------------------------------- |
| **Career Page Monitoring** | Automatically scrapes configured company career pages |
| **Job Discovery**          | Extracts job listings, titles, and descriptions       |
| **AI-Powered Matching**    | Analyzes job fit using Gemini 1.5 Flash               |
| **Scheduled Scanning**     | Runs daily scans via APScheduler                      |
| **RESTful API**            | Manage companies and profiles via HTTP endpoints      |

---

## Features

- **Add Companies**: Register company career page URLs for monitoring
- **User Profile**: Store resume text and job preferences for AI matching
- **Automated Scraping**: Playwright-based scraper handles JavaScript-heavy sites
- **Smart Matching**: AI evaluates match score (0-100), reasoning, and missing skills
- **Manual Trigger**: On-demand scan via API endpoint
- **Background Processing**: Non-blocking job processing with FastAPI BackgroundTasks

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Job Auto-Applier                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   FastAPI   │───▶│   Routers   │───▶│    Core     │───▶│  Database   │  │
│  │   (main)    │    │  (API Layer)│    │  (Business) │    │  (SQLModel) │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                                     │                             │
│         │           ┌─────────────────────────┼─────────────────────────┐   │
│         │           │                         │                         │   │
│         ▼           ▼                         ▼                         │   │
│  ┌─────────────┐  ┌─────────────┐    ┌─────────────┐                    │   │
│  │  Scheduler  │  │   Scraper   │───▶│  Analyzer   │                    │   │
│  │ (APScheduler)│  │ (Playwright)│    │  (Gemini)   │                    │   │
│  └─────────────┘  └─────────────┘    └─────────────┘                    │   │
│                           │                  │                          │   │
│                           │                  │                          │   │
│                           ▼                  ▼                          │   │
│                   ┌─────────────┐    ┌─────────────┐                    │   │
│                   │   Career    │    │   Gemini    │                    │   │
│                   │   Pages     │    │    API      │                    │   │
│                   │  (External) │    │  (External) │                    │   │
│                   └─────────────┘    └─────────────┘                    │   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component             | Responsibility                                    |
| --------------------- | ------------------------------------------------- |
| **FastAPI (main.py)** | Application entry point, lifespan management      |
| **Routers**           | HTTP endpoint handlers for companies and profiles |
| **Scheduler**         | APScheduler for 24-hour interval job scans        |
| **Scraper**           | Playwright browser automation for page scraping   |
| **Analyzer**          | Gemini API integration for job matching           |
| **Database**          | SQLModel/SQLite for data persistence              |

---

## Project Structure

```
auto-applier/
│
├── app/                           # Main application package
│   ├── __init__.py
│   ├── main.py                    # FastAPI entry point, lifespan hooks
│   ├── config.py                  # pydantic-settings configuration
│   │
│   ├── api/                       # API layer
│   │   ├── __init__.py
│   │   └── routers/
│   │       ├── __init__.py        # Combined router export
│   │       ├── companies.py       # Company CRUD endpoints
│   │       └── profile.py         # User profile endpoints
│   │
│   ├── core/                      # Business logic layer
│   │   ├── __init__.py
│   │   ├── scraper.py             # Playwright web scraping engine
│   │   ├── analyzer.py            # Gemini AI job matching
│   │   └── scheduler.py           # APScheduler background jobs
│   │
│   ├── db/                        # Database layer
│   │   ├── __init__.py
│   │   ├── database.py            # Engine, session, connection
│   │   └── models.py              # SQLModel table definitions
│   │
│   └── utils/                     # Shared utilities
│       ├── __init__.py
│       └── verify.py              # System verification helpers
│
├── tests/                         # Test suite
│   └── __init__.py
│
├── data/                          # Database storage (Docker volume)
│
├── Dockerfile                     # Multi-stage Docker build
├── docker-compose.yml             # Container orchestration
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
├── SYSTEM_DESIGN_AND_SPEC.md      # Detailed system specification
└── README.md                      # This file
```

---

## Tech Stack

| Category             | Technology              | Purpose                               |
| -------------------- | ----------------------- | ------------------------------------- |
| **Framework**        | FastAPI                 | Async web framework with OpenAPI docs |
| **ORM**              | SQLModel                | SQLAlchemy + Pydantic integration     |
| **Database**         | SQLite                  | Lightweight, portable data storage    |
| **Scraping**         | Playwright              | Browser automation for dynamic pages  |
| **AI/LLM**           | Google Gemini 1.5 Flash | Job matching and analysis             |
| **Scheduling**       | APScheduler             | Background task scheduling            |
| **Containerization** | Docker                  | Deployment and isolation              |

---

## Setup

### Prerequisites

- Python 3.10+
- Docker and Docker Compose (for containerized deployment)
- Google Gemini API key

### Local Development

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd auto-applier
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

5. **Run the application**

   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the API**
   - API Base: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Deployment

1. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

2. **Build and run (Production)**

   ```bash
   docker compose up --build -d
   ```

3. **Run in development mode (with hot reload)**

   ```bash
   docker compose --profile dev up app-dev --build
   ```

4. **View logs**

   ```bash
   docker compose logs -f app
   ```

5. **Stop containers**

   ```bash
   docker compose down
   ```

---

## Configuration

All configuration is managed via environment variables. See `.env.example` for available options.

| Variable            | Required | Default                       | Description                   |
| ------------------- | -------- | ----------------------------- | ----------------------------- |
| `DATABASE_URL`      | No       | `sqlite:///./auto_applier.db` | Database connection string    |
| `GEMINI_API_KEY`    | Yes      | -                             | Google Gemini API key         |
| `OPENAI_API_KEY`    | No       | -                             | OpenAI API key (alternative)  |
| `EMAIL_SMTP_SERVER` | No       | -                             | SMTP server for notifications |
| `EMAIL_PORT`        | No       | `587`                         | SMTP port                     |
| `EMAIL_USERNAME`    | No       | -                             | SMTP username                 |
| `EMAIL_PASSWORD`    | No       | -                             | SMTP password                 |

---

## API Reference

### Base URL

```
http://localhost:8000
```

### Endpoints

#### Health Check

```http
GET /
```

Returns application status.

**Response:**

```json
{
  "message": "Job Auto Applier is running"
}
```

---

#### Companies

**Create Company**

```http
POST /companies/
Content-Type: application/json

{
  "name": "Google",
  "career_page_url": "https://careers.google.com/jobs/"
}
```

**List Companies**

```http
GET /companies/
```

---

#### User Profile

**Create/Update Profile**

```http
POST /profile/
Content-Type: application/json

{
  "name": "John Doe",
  "resume_text": "Senior Python Developer with 5 years experience...",
  "preferences": "Remote, Python, AI/ML roles"
}
```

**Get Profile**

```http
GET /profile/
```

---

#### Manual Scan

**Trigger Scan**

```http
POST /scan-now/
```

Triggers a background job scan for all active companies.

**Response:**

```json
{
  "message": "Scan triggered in background"
}
```

---

## Request Flows

### Daily Scan Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Scheduler   │────▶│   Scraper    │────▶│   Analyzer   │────▶│   Database   │
│ (24h trigger)│     │ (Playwright) │     │   (Gemini)   │     │   (SQLite)   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │                    │
       │                    │                    │                    │
       │              ┌─────▼─────┐        ┌─────▼─────┐        ┌─────▼─────┐
       │              │  Career   │        │  Gemini   │        │   Store   │
       │              │   Page    │        │    API    │        │   Jobs    │
       │              └───────────┘        └───────────┘        └───────────┘
       │
       └──── 1. Scheduler triggers run_daily_scan()
              2. For each active company:
                 a. Launch headless browser
                 b. Navigate to career page
                 c. Extract job links
              3. For each new job:
                 a. Visit job page
                 b. Extract description
                 c. Send to Gemini for analysis
                 d. Save job with match score
```

### Add Company Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────▶│  Router  │────▶│  Session │────▶│ Database │
│ (HTTP)   │     │(companies)│    │ (SQLModel)│    │ (SQLite) │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                │                │                │
     │                │                │                │
     │    POST /companies/             │                │
     │    {name, url}                  │                │
     │                │                │                │
     │                └───── session.add(company) ─────▶│
     │                                 │                │
     │◀──── 201 Created ───────────────┴────────────────┘
```

### Job Matching Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Job Matching Process                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────┐                                                      │
│  │ Job Description│                                                     │
│  │ (scraped text) │─────────┐                                           │
│  └───────────────┘          │                                           │
│                             ▼                                           │
│                    ┌─────────────────┐                                  │
│  ┌───────────────┐ │                 │    ┌─────────────────────────┐   │
│  │  User Profile │─▶   Gemini API   │───▶│ {                       │   │
│  │ (resume/prefs)│ │                 │    │   "match_score": 85,    │   │
│  └───────────────┘ └─────────────────┘    │   "reasoning": "...",   │   │
│                                           │   "missing_skills": []  │   │
│                                           │ }                       │   │
│                                           └─────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Development

### Code Style

- Follow PEP 8 guidelines
- Type hints required for all function arguments and return values
- Docstrings required for all modules, classes, and functions

### Running Tests

```bash
pytest tests/
```

### Project Conventions

| Convention         | Description                                      |
| ------------------ | ------------------------------------------------ |
| **Imports**        | Use absolute imports from `app` package          |
| **Models**         | Define in `app/db/models.py` using SQLModel      |
| **Endpoints**      | Separate routers by domain in `app/api/routers/` |
| **Business Logic** | Keep in `app/core/`, not in routers              |

---

## Roadmap

### Phase 1 (Current)

- [x] FastAPI scaffold with SQLModel
- [x] Generic Playwright scraper
- [x] Gemini AI job matching
- [x] Company and profile management API
- [x] APScheduler integration
- [x] Docker containerization

### Phase 2 (Planned)

- [ ] Email/Discord notifications
- [ ] Dynamic navigation with AI
- [ ] Pagination handling (infinite scroll)
- [ ] Job status tracking (Applied, Rejected)

### Phase 3 (Future)

- [ ] Auto-apply functionality
- [ ] React/Next.js dashboard
- [ ] Multi-user support
- [ ] PostgreSQL migration

---

## License

This project is for personal use.

---

## Contributing

Contributions are welcome. Please follow the development conventions outlined above.
