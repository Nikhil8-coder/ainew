# Career Choice 🔮

An interactive career guidance app built with Streamlit. Users sign up with their
current stream/background, answer a short guided assessment (plus a free-text
question box with clarifying follow-ups), and get a recommended career direction —
with reasoning for and against, a skill roadmap, and current + 10-year market trends.

## Features
- Username/password accounts, passwords salted and hashed (never stored in plain text)
- Signup captures the user's current stream, used to tailor suggestions
- Guided Q&A plus a free-text question box that asks for clarification on vague input
- Rule-based recommendation engine mapping traits → career paths, with "if you take
  this / if you avoid it / if you'd rather try something adjacent" reasoning
- Skill self-assessment slider with tailored next steps
- Current-year and 10-year-forward market trend notes per career path

## Setup

```bash
git clone <your-repo-url>
cd career-choice
pip install -r requirements.txt
```

Before running, set an admin password as an environment variable (used only for
the creator's private admin view — see below):

```bash
export CAREER_CHOICE_ADMIN_PASSWORD="pick-a-strong-password"
streamlit run app.py
```

On Windows (PowerShell): `$env:CAREER_CHOICE_ADMIN_PASSWORD="pick-a-strong-password"`

## Creator admin view

The app owner can review registered usernames, streams, and account-creation dates
(never passwords — those are hashed and there's no reason to display them) at:

```
<your-deployed-url>/?access_scope=creator_admin_override
```

This link isn't shown anywhere in the app's UI. It's also gated by
`CAREER_CHOICE_ADMIN_PASSWORD` — knowing the URL alone isn't enough to see any
data. Change the default password before deploying; it will not protect anything
if left as-is.

## Notes for further development
- `users_database.json` is a simple local file store, fine for a small class
  project or demo. For a real deployment with multiple users, move this to a
  proper database (e.g. SQLite via `sqlalchemy`, or a hosted Postgres instance) —
  a local JSON file isn't safe for concurrent writes at scale.
- The recommendation logic in `KNOWLEDGE_BASE` (in `app.py`) is a plain Python
  dictionary — add new career paths or edit trend text there directly.
