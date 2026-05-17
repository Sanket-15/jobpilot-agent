# JobPilot Agent

JobPilot Agent is a bilingual AI job-search assistant that analyzes job descriptions, compares them with a candidate profile, generates tailored application content, checks for unsupported claims, suggests ATS improvements, tracks applications locally, and helps prepare next actions.

## Important Disclaimer

JobPilot helps prepare application materials, but the user must review and submit everything manually.

JobPilot must not invent experience, companies, dates, tools, certifications, metrics, or achievements. No auto-apply functionality is included.

## Feature Overview

### V1 - Application Package Generator

- Paste job description.
- Paste candidate profile/CV.
- Parse job information.
- Analyze match.
- Generate tailored CV summary and bullet points.
- Generate cover letter.
- Suggest ATS improvements.
- Check unsupported claims.
- Generate interview questions.
- Recommend next action.

### V2 - Local Job Tracker

- Save analyzed jobs.
- Track status.
- Add notes.
- Add follow-up date.
- Update/delete saved jobs.
- Local SQLite only.

### V3 - Profile Memory

- Save candidate profiles locally.
- Reuse profiles for applications.
- Edit/delete saved profiles.
- Manual paste still supported.

### V4 - Export

- Export generated application package as Markdown.
- Export generated application package as plain text.
- Manual download only.
- No PDF/DOCX yet.

### V5 - ATS Resume Scanner

- Paste job description and CV.
- Get ATS score.
- Identify supported keywords.
- Identify missing keywords.
- Identify needs-clarification keywords.
- Get bullet improvements.
- Get formatting risks.
- Get safe next action.

### V6 - Profile Normalizer

- Paste raw CV/profile/LinkedIn-style text.
- Normalize into clean candidate profile.
- Supports English/German mixed input.
- Review/edit before saving.
- Save to Profile Memory.

### V7 - Resume Translator / Localization

- Paste English/German CV or profile text.
- Localize to English or German.
- Choose the target market.
- Review/edit before saving.
- Save localized version to Profile Memory.
- No file upload yet.
- No scraping.
- No cloud storage.
- No auto-apply.

### V8 - Job URL Import

- Paste a job posting URL.
- JobPilot tries to extract job text.
- Extracted text is shown for review/edit.
- Manual paste fallback remains available.
- Source URL can be saved to tracker.
- Single user-provided URL only.
- No crawling.
- No job search yet.
- No scraping at scale.
- No login bypass.
- No auto-apply.

### V9 - CV File Import

- Upload PDF, LaTeX, TXT, or Markdown CV/profile files.
- Extract readable text locally in memory.
- Review/edit extracted text before normalization.
- Send extracted text into Profile Normalizer.
- Save cleaned profile to Profile Memory.
- No OCR.
- No DOCX yet.
- No uploaded files are saved.
- No cloud storage.
- No auto-apply.

### V10 - Job Search + Filtering

- Search jobs from safe API/feed providers.
- Use Adzuna as the primary provider if API credentials are configured.
- Use Arbeitnow and Remotive as free/fallback providers.
- Filter by keyword, location, remote-only, and skills/tags.
- Review job details before saving.
- Save selected jobs to the local tracker.
- No scraping at scale.
- No browser automation.
- No login bypass.
- No auto-apply.
- No AI ranking yet.

### V11 - Job Ranking

- Rank searched jobs against a saved profile.
- Show match score and confidence.
- Show strong matches, gaps, risks, and next action.
- Save ranked jobs to tracker.
- AI ranking is user-triggered.
- Ranking is limited to avoid unnecessary API usage.
- No auto-apply.
- No mass application generation.

### V12 - Controlled Apply Flow + Application Logging

- Select a saved job.
- Prepare a manual document checklist.
- Track CV, cover letter, certificates, links, salary expectation, availability, and work authorization readiness.
- Generate an optional copy-only application message draft.
- Confirm manual review and manual submission.
- Log application activity locally.
- Update tracker status to Applied after manual submission.
- View application history.
- No auto-apply.
- No job portal submission.
- No browser automation.
- No email sending.
- No cloud storage.

## How It Works

1. Paste or select a profile.
2. Paste a job description or import one from a single job URL.
3. Generate an application package.
4. Review claim warnings.
5. Export the package or save the job to the tracker.
6. Search, rank, or prepare saved jobs as needed.
7. Log manual application activity only after user review/submission.

## Why This Project Matters

JobPilot demonstrates an agentic workflow with orchestration, structured outputs, safety checks, local state, bilingual handling, ATS analysis, and human-in-the-loop review.

## Tech Stack

- Python
- Streamlit
- Gemini API
- Pydantic
- SQLite
- python-dotenv
- requests
- Beautiful Soup
- pypdf

## Folder Structure

```text
jobpilot-agent/
├── app.py
├── agent.py
├── skills.py
├── schemas.py
├── prompts.py
├── claim_checker.py
├── tracker.py
├── profile_store.py
├── export_utils.py
├── ats_scanner.py
├── profile_normalizer.py
├── resume_localizer.py
├── job_url_importer.py
├── cv_file_importer.py
├── job_search.py
├── job_ranker.py
├── apply_flow.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env`:

```text
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL_NAME=gemini-2.0-flash
ADZUNA_APP_ID=your_adzuna_app_id_here
ADZUNA_APP_KEY=your_adzuna_app_key_here
```

Adzuna is optional. If `ADZUNA_APP_ID` and `ADZUNA_APP_KEY` are not set, JobPilot will continue using free/fallback providers such as Arbeitnow and Remotive.

Run the app:

```bash
streamlit run app.py
```

## Privacy And Safety Notes

- `data/jobs.db` stores local tracker and saved profile data.
- `data/jobs.db` may contain personal data.
- `data/jobs.db` is ignored by Git.
- Saved tracker rows may include a user-provided source job URL.
- `.env` is ignored by Git.
- API keys should never be committed.
- Adzuna credentials are optional and should never be committed.
- Localized profiles may contain personal data.
- Localized profiles are saved locally in `data/jobs.db` only when the user clicks Save Localized Profile to Profile Memory.
- Uploaded CVs may contain personal data.
- JobPilot extracts uploaded CV text in memory and does not save uploaded files.
- Only profiles explicitly saved by the user are stored locally in `data/jobs.db`.
- Generated content must be reviewed by the user.
- Only add keywords or claims if they reflect real experience.
- No auto-apply.
- No scraping.
- No cloud storage.

Do not use real phone numbers, private emails, birthdates, or full personal CV data in public screenshots or demo inputs.

## Current Limitations

- Job URL import is single-URL only and may fail on blocked, login-only, or JavaScript-rendered pages.
- CV file import does not support OCR or DOCX yet.
- Job search uses safe API/feed providers only.
- Job ranking is AI-assisted and user-triggered only.
- Application logs may contain personal data.
- Application logs are stored locally in `data/jobs.db` only.
- JobPilot stores only file names/notes typed by the user, not actual application files.
- No PDF/DOCX export yet.
- No authentication.
- No deployment.
- No automatic job applications.
- AI output requires human review.

## Roadmap

- Additional provider integrations.
- Optional DOCX/PDF export improvements.
- Optional OCR.
- Optional login/cloud sync only if deployed as a real product.

## Demo Data Warning

Use fake demo data in GitHub screenshots and portfolio demos. Do not include real phone numbers, private emails, birthdates, or full personal CV data.
