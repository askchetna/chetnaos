# ChetnaOS Backend + Frontend Setup Guide

## Backend Setup

### Installation
```bash
pip install fastapi uvicorn pydantic
```

### Running the Backend

**Option 1: Using uvicorn module (Recommended)**
```bash
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

**Option 2: Using Python module**
```bash
python -m backend.app
```

**Option 3: Direct run (for development)**
```bash
cd backend
python app.py
```

The backend will start on `http://127.0.0.1:8000`

### Available Endpoints

- `POST /chetna` - ChetnaOS conscious runtime chat endpoint
- `POST /evaluate` - Land evaluation endpoint
- `POST /roi` - ROI calculation endpoint
- `POST /crop` - Crop planning endpoint
- `GET /health` - Health check endpoint

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Frontend Setup

### Running the Frontend

**Option 1: Using Live Server (VS Code Extension)**
1. Install "Live Server" extension in VS Code
2. Right-click on `frontend/index.html`
3. Select "Open with Live Server"
4. Frontend will open at `http://localhost:5500/frontend/index.html`

**Option 2: Using Python HTTP Server**
```bash
cd frontend
python -m http.server 5500
```
Then open: `http://localhost:5500/index.html`

**Option 3: Using Node.js http-server**
```bash
npx http-server frontend -p 5500
```

### Frontend URLs

- Main Chat: `http://localhost:5500/frontend/index.html`
- Kalpavriksha Menu: `http://localhost:5500/frontend/kalpavriksha_ui/index.html`
- Land Evaluator: `http://localhost:5500/frontend/kalpavriksha_ui/land.html`
- ROI Calculator: `http://localhost:5500/frontend/kalpavriksha_ui/roi.html`
- Crop Planner: `http://localhost:5500/frontend/kalpavriksha_ui/crop.html`

## Configuration

### Backend Configuration
- **Port**: 8000 (FastAPI default)
- **Host**: 127.0.0.1
- **CORS**: Enabled for all origins (`*`)

### Frontend Configuration
- All fetch URLs point to: `http://127.0.0.1:8000`
- No hardcoded file paths
- All relative paths are correct

## Testing Endpoints

### Test /chetna endpoint:
```bash
curl -X POST http://127.0.0.1:8000/chetna \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello ChetnaOS"}'
```

### Test /evaluate endpoint:
```bash
curl -X POST http://127.0.0.1:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "ph": 7.0,
    "water_depth": 80,
    "soil": "loamy",
    "temp": 28,
    "road": "highway"
  }'
```

### Test /roi endpoint:
```bash
curl -X POST http://127.0.0.1:8000/roi \
  -H "Content-Type: application/json" \
  -d '{
    "acres": 2,
    "model": "sandalwood"
  }'
```

### Test /crop endpoint:
```bash
curl -X POST http://127.0.0.1:8000/crop \
  -H "Content-Type: application/json" \
  -d '{
    "soil_ph": 7.0,
    "temp": 28,
    "water_depth": 10,
    "soil_type": "loamy",
    "road_access": "highway",
    "acres": 1
  }'
```

## Troubleshooting

### Import Errors
If you see "attempted relative import with no known parent package":
- Make sure you're running from the project root
- Use `python -m backend.app` instead of `python backend/app.py`

### CORS Errors
- Backend CORS is configured to allow all origins
- Make sure backend is running on port 8000
- Check browser console for specific CORS errors

### Connection Errors
- Verify backend is running: `curl http://127.0.0.1:8000/health`
- Check frontend fetch URLs point to `http://127.0.0.1:8000`
- Ensure no firewall is blocking port 8000

## Project Structure

```
ChetnaOS.v1/
├── backend/
│   ├── __init__.py
│   ├── app.py          # Main FastAPI application
│   ├── api.py          # Kalpavriksha routes
│   ├── chetna_core.py  # ChetnaOS core logic
│   ├── memory.py
│   ├── dharma_net.py
│   ├── world_state.py
│   └── evolution_engine.py
├── kalpavriksha/
│   ├── __init__.py
│   ├── evaluator.py
│   ├── roi.py
│   └── crop_planner.py
└── frontend/
    ├── index.html
    ├── app.js
    └── kalpavriksha_ui/
        ├── index.html
        ├── land.html
        ├── roi.html
        ├── crop.html
        ├── style.css
        └── js/
            ├── app.js
            ├── roi.js
            └── crop.js
```

