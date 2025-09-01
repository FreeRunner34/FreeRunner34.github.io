# Work Orders Web App (Flask + SQLite)

A minimal CRUD web application tailored for automotive work orders.

## Features
- Create, view, edit, and delete work orders
- Search by customer, vehicle, status, or complaint
- SQLite database (file-based, zero config)

## Quickstart
```bash
# 1) Create & activate a virtual environment (optional but recommended)
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run the app
python app.py

# App runs at http://127.0.0.1:5000
```

## Project Structure
```
workorders_app/
├─ app.py
├─ requirements.txt
├─ templates/
│  ├─ base.html
│  ├─ index.html
│  ├─ create.html
│  ├─ edit.html
│  └─ detail.html
└─ static/
   └─ style.css
```

## Next Steps / Ideas
- Add login/auth (Flask-Login) and user accounts
- Export to CSV for reporting
- Add file uploads (photos, PDFs)
- Status transitions with timestamps
- Deploy to a VPS or a PaaS like Railway/Render
```


## One-tap Phone Launch (Render)
1. Zip this folder (or use the provided .zip).
2. Go to render.com (create a free account).
3. Create > Web Service > Build and deploy from a repo (recommended) or from the .zip upload.
4. Use the defaults; Render detects Python.
5. When deployed, open the URL in Safari/Chrome on your phone.
6. Tap the browser menu and **Add to Home Screen**. The app behaves like a native app (PWA).

## PWA notes
- `static/manifest.json` + `static/service-worker.js` let you install it to your home screen.
- Offline: pages you visit get cached; forms still need network to save to the DB.


## Auth, CSV Export, and Demo Seed
- **Login**: visit `/login` (default password `admin`, change via `ADMIN_PASSWORD` env var).
- **Protected actions**: create/edit/delete/export/seed require login.
- **CSV Export**: `/export.csv` downloads all work orders.
- **Seed demo data**: `/seed-demo` creates a few sample work orders.
