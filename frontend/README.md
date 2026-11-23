# DocVera frontend

React + Vite interface for the DocVera FastAPI backend.

## Run locally (Windows PowerShell)

```powershell
cd frontend
npm install
npm run dev
```

Start the backend separately in another terminal:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

The frontend expects the API at `http://localhost:8000`. To use a different URL, create `frontend/.env.local` with `VITE_API_URL=http://your-api-host` and restart Vite.
