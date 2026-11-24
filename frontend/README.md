# OpenSource Compass — Frontend

React + Vite frontend for the OpenSource Compass issue discovery and recommendation API.

## Requirements

- Node.js compatible with the versions required by the dependencies in `package.json`
- The OpenSource Compass FastAPI backend running locally (default: `http://localhost:8000`)

## Run locally

```powershell
npm install
npm run dev
```

Open the local URL printed by Vite.

In a second terminal, start the backend from the project root:

```powershell
cd "D:\OpenSource Compass"
.\.venv\Scripts\Activate.ps1
uvicorn app:app --reload
```

## API URL

The frontend defaults to `http://localhost:8000`. To use another API URL, create a local `.env` file in this folder:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Do not commit `.env` files or secrets.

## Production build

```powershell
npm run build
npm run preview
```

## Frontend features

- Skill-based GitHub issue discovery
- Recommendation, difficulty, search, and sorting filters
- AI analysis drawer using the existing backend response
- Saved issues stored in browser local storage
- Skill insights and opportunity readiness breakdown
- Workspace display and search preferences
- Responsive desktop, tablet, and mobile layouts
