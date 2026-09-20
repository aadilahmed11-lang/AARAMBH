# AARAMBH - Beginner Setup

## Easiest option on Windows

1. Install Python 3.11+ and Node.js LTS.
2. Double-click `SETUP_AARAMBH.bat` once.
3. After setup, the script starts the backend and frontend.
4. Open `http://localhost:5173`.
5. Use the demo applicant account from the Login page.

### Demo accounts
- Applicant: `user@aarambh.local` / `user123`
- Partner: `partner@aarambh.local` / `partner123`
- Admin: `admin@aarambh.local` / `admin123`

## Database

AARAMBH now defaults to a local SQLite database (`aarambh.db`) so a beginner does not need MySQL. The first backend run automatically creates the tables and demo catalogue.

MySQL remains supported by setting `DATABASE_URL` in `backend/.env`.

## Voice

Use Google Chrome or another browser that supports the Web Speech API. Select English, हिन्दी or தமிழ் and press the floating microphone. Voice is processed in the browser for the prototype; no cloud speech provider is required.

Allow microphone access when the browser asks.
