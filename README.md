# Sales Drop Assistant (demo)

A chat-style assistant that answers "why did sales drop?" using demo data.

Question -> **TypeSafe Jev** router (keyword fallback) -> **Open Knowledge Format (OKF)** knowledge bundle -> CrewAI agent + read-only SQLite tools -> OpenAI -> React. All data is **demo data**.

- **Jev** (TypeSafe) reads the question and picks which OKF concepts are relevant.
- **OKF** (Google's Open Knowledge Format): `knowledge\` is a bundle of Markdown files with YAML frontmatter (`type`, `title`, `description`, `tags`) linked to each other. The UI shows each concept used.

The UI shows the active router under the title after you click Analyze:
- `Jev (TypeSafe)` - Jev is connected.
- `Jev unavailable — keyword fallback` - key is set but the call failed.
- `Demo router — Jev not connected` - no `JEV_API_KEY` set.

## Setup (Windows, run from this folder)

```
python -m venv venv
venv\Scripts\activate
pip install -r backend\requirements.txt
copy .env.example .env
```
Edit `.env`:
- `OPENAI_API_KEY` (required for answers; without it the UI shows cards + setup instructions)
- `OPENAI_MODEL` (optional, default `gpt-4.1-mini`)
- `JEV_API_KEY` (optional, enables the Jev router)

`.env` is git-ignored. Never commit keys.

## Run (two terminals)

Backend:
```
venv\Scripts\activate
cd backend
uvicorn main:app --port 8000
```
Frontend:
```
cd frontend
npm install
npm run dev
```
Open http://localhost:5173. Restart the backend after changing `.env`. Delete `backend\demo.db` to re-seed.

## Customize

- Router: edit `backend\jev.py` (`route()` returns knowledge file names).
- Suggested questions on the home screen: `SUGGESTIONS` in `frontend\src\App.jsx`.
- Look and feel: `frontend\src\styles.css`.
