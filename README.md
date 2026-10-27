# BuildWise AI — Construction Intelligence Starter

A full-stack React + Vite frontend and FastAPI backend for preliminary multimodal construction safety review, crack observations, project planning/cost estimates, and property valuation frameworks.

## Requirements
- Python 3.9+ (Python 3.11 recommended)
- Node.js 20+ and npm
- An API key for an OpenAI-compatible multimodal model

## Run locally

### 1. Backend
```bash
cd backend
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Copy .env.example to .env, then set OPENAI_API_KEY and optionally OPENAI_MODEL.
# PowerShell: $env:OPENAI_API_KEY="your-key"
# macOS/Linux: export OPENAI_API_KEY="your-key"
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs  
Health check: http://localhost:8000/health

### 2. Frontend (new terminal)
```bash
cd frontend
npm install
# Copy .env.example to .env and set VITE_API_URL=http://localhost:8000 if needed.
npm run dev
```
Vite prints the local URL, normally http://localhost:5173.

## Deployment

### Backend (Render / similar Docker host)
1. Push this repository to your own Git provider.
2. Create a Web Service from the repository and select Docker.
3. Set the Dockerfile path to `backend/Dockerfile` and the root directory to `backend` (depending on host configuration, use one approach, not both).
4. Add `OPENAI_API_KEY`, `OPENAI_MODEL`, and `FRONTEND_ORIGIN` as service environment variables. Set `FRONTEND_ORIGIN` to your deployed frontend origin.
5. Deploy and verify `/health` and `/docs`.

### Frontend (Vercel / Netlify / static host)
1. Create a project from the repository with `frontend` as the root directory.
2. Build command: `npm run build`; output directory: `dist`.
3. Add `VITE_API_URL` with the deployed backend URL, then redeploy.

The frontend and backend URLs will be assigned by your hosting provider. This archive does **not** create or host a public deployment automatically.

## API routes
- `GET /health`
- `POST /api/analyze/safety` — multipart fields: `description`, optional `image`
- `POST /api/analyze/cracks` — multipart fields: `description`, optional `image`
- `POST /api/plan` — JSON `{"description":"...", "project":{"area_sqft":1000,"floors":1,"location":"India","quality":"standard"}}`
- `POST /api/valuation` — same JSON structure

## Important limitations
- This is a deployable starter, not a certified engineering or appraisal product.
- Model output is generated at request time and depends on API access, model availability, prompt quality, and input quality.
- AI responses are requested as JSON objects; application-level schemas and strict validation should be added before production.
- Cost and material values are indicative and must be checked against local rates, drawings, quantities, codes, and site conditions.
- Image analysis cannot certify that a structure is safe. Obtain an on-site assessment from a qualified professional for suspected structural hazards.
- Add authentication, rate limiting, audit logging, privacy controls, and automated tests before exposing it to real users.
