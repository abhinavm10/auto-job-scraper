# System Design & Specification: Job Auto-Applier / Notification System

## 1. Goal
Build a configurable, automated system to:
1.  Monitor career pages of specified companies.
2.  Discover new job openings daily.
3.  Analyze job relevance using AI based on the user's profile (resume, experience, preferences).
4.  Notify the user of relevant matches.
5.  (Future) Attempt to auto-apply or prepare materials.

## 2. Architecture

We will use a modular micro-service functionality within a monolithic FastAPI application.

### Tech Stack
-   **Backend**: Python 3.10+ with **FastAPI**.
-   **Database**: **SQLite** (via **SQLModel** / SQLAlchemy) for simplicity and portability. easy to migrate to PostgreSQL.
-   **Scraping**: **Playwright** (Python) for handling dynamic JS-heavy career sites.
-   **AI Integration**: **Gemini 1.5 Flash/Pro** (via Google Generative AI SDK) or OpenAI GPT-4o for parsing and matching.
-   **Scheduling**: **APScheduler** (running in-process with FastAPI) for daily cron jobs.
-   **Notifications**: Email (SMTP) or simple Discord Webhook.

### High-Level Components

1.  **Job Source Manager**:
    -   Database models to store `Company` and `CareerPageURL`.
    -   Configuration for specific scraping strategies (if generic scraping fails).

2.  **Scraper Engine**:
    -   Headless browser (Playwright) to visit URLs.
    -   Extracts job links, titles, and descriptions.
    -   Smart logic to detect "Next Page" or infinite scroll.

3.  **AI Analyzer**:
    -   Input: User Profile (Text/JSON), Job Description.
    -   Process: LLM evaluates match score (0-100) and reasoning.
    -   Output: Structured data (Match boolean, Reason, Custom tailored cover letter points).

4.  **User Profile Manager**:
    -   Store user resume (parsed text), years of experience, skills, and "dealbreakers" (e.g., Remote only).

5.  **Notification Service**:
    -   Formats the daily digest of new relevant jobs.
    -   Sends via configured channel.

## 3. Data Models (Draft)

-   `UserProfile`: Name, ResumeText, Skills[], Preferences.
-   `Company`: Name, CareerPageUrl, ScrapeConfig (JSON).
-   `JobListing`: Title, Url, CompanyID, Description, DateFound, Status (New, Applied, Rejected), MatchScore, MatchReason.

## 4. Workflows

### Daily Scan
1.  Scheduler triggers `scan_jobs()`.
2.  For each `Company`:
    -   **Navigation & Discovery**:
        -   Launch Playwright to the base `CareerPageUrl`.
        -   **Dynamic Navigation (Smart Filters)**:
            -   Capture page state (Accessibility Tree / HTML snapshot).
            -   **Decision Step**: Send state + User Preferences (e.g., "Software Engineer, Remote") to a mini-LLM Agent.
            -   **Action**: LLM returns the CSS Selector to click / input to type (e.g., "Click button[name='Department']", "Select option 'Engineering'").
            -   Execute action and wait for reload. Repeat until job list is visible.
        -   **Pagination**: Detect "Next" buttons or "Infinite Scroll" triggers. Loop until no new jobs are found or a limit is reached.
    -   **Listing Extraction**:
        -   Extract `Job Title`, `Link`, and `Location` from the list view.
        -   Filter deduplication: Ignore URLs already in the DB.
3.  **Deep Analysis (For each new job)**:
    -   **Visit**: Navigate to the specific job URL.
    -   **Extract**: Get the full Job Description text.
    -   **Match**: Send `(Job Description, User Profile)` to the **AI Analyzer**.
        -   *Prompt Strategy*: "You are a recruiter. Does this candidate [Profile] fit this job [Job]? Return JSON: {match_score: 0-100, reasoning: '...', missing_skills: [...]}".
    -   **Store**: Save the result to the DB.
4.  If high-match jobs found:
    -   Trigger `Notification Service`.

### Adding a Company
1.  User POSTs URL to `/companies/`.
2.  System attempts a test scrape to verify navigability.
3.  If successful, adds to daily rotation.

## 5. Requirements

-   **Python Environment**: `virtrualenv` or `conda`.
-   **API Keys**: Google GenAI Key (or OpenAI).
-   **Browser Drivers**: Playwright browsers installed.

## 6. Implementation Plan (Phase 1)
1.  **Setup**: FastAPI scaffold, SQLModel setup.
2.  **Scraper**: Generic Playwright script to fetch text from a URL.
3.  **AI**: Prompt engineering for "Is this job relevant?"
4.  **API**: Endpoints to add companies and view results.
5.  **Scheduler**: Link it all together.

## 7. Future Expansions
-   **Auto-Apply**: Selenium/Playwright script to fill forms.
-   **Dashboard**: A React/Next.js frontend to view jobs.
