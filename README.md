# Job Application Tracker

A Flask and MySQL web application for organizing job opportunities, tracking applications, managing company contacts, and evaluating how well your skills match job requirements.

## Features

- **Dashboard:** View an overview of companies, jobs, and applications.
- **Companies:** Add, view, edit, and delete company records.
- **Jobs:** Manage job listings, descriptions, salary ranges, job types, and skill requirements.
- **Applications:** Track application dates, statuses, resume versions, and interview information.
- **Contacts:** Store and manage professional contacts associated with companies.
- **Job Match:** Compare your skills against job requirements and rank opportunities by match percentage. Uses Google's Gemini API to identify potential technical skill equivalencies.

## Technologies

- Python
- Flask
- MySQL
- HTML and CSS
- Google Gemini API
- mysql-connector-python

## Project Structure

```text
assignment5/
├── app.py
├── database.py
├── job_matcher.py
├── ai_matcher.py
├── schema.sql
├── requirements.txt
├── AI_USAGE.md
├── .gitignore
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── companies.html
│   ├── jobs.html
│   ├── applications.html
│   ├── contacts.html
│   ├── job_match.html
│   ├── edit_company.html
│   ├── edit_job.html
│   ├── edit_application.html
│   └── edit_contact.html
└── static/
    └── style.css
```

## Prerequisites

Before running the application, install:

- Python 3.10 or newer
- MySQL Server
- Git

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Alessandra005/job-app-tracker
cd assignment5
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows PowerShell:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MySQL

Create the database and tables by running `schema.sql` in MySQL:

```bash
mysql -u root -p < schema.sql
```

Enter your MySQL password when prompted.

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=job_trackers

GEMINI_API_KEY=your_gemini_api_key
```

Replace the example values with your own credentials.

The Gemini API key is used for AI-assisted skill equivalency matching. The application can still use its standard skill-matching logic if an API key is unavailable.

**Important:** Never commit your `.env` file or share your API keys.

### 6. Run the application

```bash
python app.py
```

Open your browser and visit:

http://127.0.0.1:5000

## Job Match

Enter your skills as a comma-separated list. The application compares them with each job's required and preferred skills.

The matching calculation uses:

- Required skills: 70% of the score
- Preferred skills: 30% of the score

Gemini can suggest direct technical skill equivalencies. These suggestions are validated before being included in the matching calculation.

## Database

The application uses four related MySQL tables:

- `companies`
- `jobs`
- `applications`
- `contacts`

Foreign keys connect jobs and contacts to companies, and applications to jobs. JSON columns store job requirements and interview information.

See `schema.sql` for the database definitions.

## AI Documentation

See [AI_USAGE.md](AI_USAGE.md) for information about the generative AI tools used, prompts, implementation decisions, and lessons learned.