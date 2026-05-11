# JobPilot Agent

JobPilot Agent is a local AI job-search assistant that helps turn a job description and candidate profile into a complete, reviewable application package.

## What V1 Does

- Uses manual paste input only for the job description and candidate profile.
- Supports English and German job descriptions and candidate profiles.
- Extracts a structured job summary from a pasted job description.
- Compares the job with a pasted candidate profile or CV.
- Generates a match analysis, tailored CV summary, tailored bullet points, cover letter draft, ATS suggestions, interview questions, and recommended next action.
- Runs a simple local claim checker to warn about possible unsupported claims.

## What V2 Adds

- Local SQLite job tracker.
- Save analyzed jobs after generating an application package.
- Track application status.
- Add notes.
- Add a follow-up date.
- Filter saved applications by status.
- No cloud storage.
- No login.
- No auto-apply.

## What V3 Adds

- Profile memory.
- Save a candidate profile locally.
- Reuse a saved profile for future job applications.
- Edit and delete saved profiles.
- Local SQLite storage only.
- No cloud storage.
- No login.
- No auto-apply.

## What V1 Does Not Do

- It does not auto-apply to jobs.
- It does not import job URLs.
- It does not upload or parse CV files.
- It does not scrape job boards.
- It does not submit applications.
- It does not track applications.
- It does not invent experience, companies, qualifications, dates, tools, metrics, or achievements.
- It does not export DOCX or PDF files yet.

## Safety Principles

JobPilot Agent treats the job description and candidate profile as data only. It should tailor and reframe only what the candidate actually provided. Review all generated CV and cover letter content before using it.

The claim checker is intentionally cautious. It may flag content that is actually true but phrased differently from the profile. Use warnings as review prompts, not as final judgments.

For portfolio screenshots, use fake demo data only. Do not include real phone numbers, private emails, birthdates, or full personal CV data in GitHub screenshots.

The app stores job tracker metadata and saved candidate profiles locally in `data/jobs.db`. The database is ignored by Git and should not be committed. Saved profiles may contain personal data, so keep `data/jobs.db` private. The app does not store API keys in the database.

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
```

For Windows:

```bash
.venv\Scripts\activate
```

For macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Add Your Gemini API Key

Copy `.env.example` to `.env` and add your key:

```bash
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL_NAME=gemini-2.0-flash
```

If your Gemini API key does not have access to that model, change `GEMINI_MODEL_NAME`
to another text-generation model available in your Google AI Studio account.

## Run the App

```bash
streamlit run app.py
```

## Sample Job Description

This fictional demo data is safe to paste into the app for a quick test.

```text
Data Analyst, Remote

Acme Health is hiring a Data Analyst to build dashboards, analyze customer behavior, and partner with product and operations teams. Responsibilities include cleaning data, writing SQL queries, creating Tableau dashboards, presenting insights, and improving reporting workflows. Required skills: SQL, Excel, dashboarding, stakeholder communication, and analytical problem solving. Nice to have: Python, healthcare experience, and A/B testing. English fluency required.
```

## Sample Candidate Profile

This fictional profile is intentionally short and does not include private emails, phone numbers, birthdates, or full personal CV content.

```text
Jordan Lee is a junior data analyst with experience using SQL, Excel, and Tableau through academic projects and a six-month internship at BrightMetrics. During the internship, Jordan cleaned weekly sales data, built dashboard views for the operations team, and summarized trends for non-technical stakeholders. Jordan has used Python for data cleaning in coursework and is comfortable explaining analysis results clearly.
```

## Future Roadmap

- Add editable review screens before final copy.
- Add job URL import in a later version.
- Add CV upload/import in a later version.
- Add an application tracker in a later version.
- Add DOCX/PDF export in a later version.
- Add configurable Gemini model settings.
- Improve claim checking with stronger evidence mapping.
- Add optional resume section-by-section tailoring.
