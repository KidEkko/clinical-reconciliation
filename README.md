# Clinical Data Reconciliation

AI-powered medication reconciliation and data quality validation system using Google Gemini.

## Local Setup

This application requires running both a backend server and a frontend development server. Follow these steps in order:

### Step 1: Backend Setup

1. Navigate to the backend directory and create a virtual environment:

```bash
cd backend
python -m venv .venv
```

2. Activate the virtual environment:

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows PowerShell:**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
.venv\Scripts\activate.bat
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Get a Gemini API key:
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Sign in with your Google account
   - Click "Get API Key" in the left sidebar
   - Create a new API key or use an existing one
   - Copy the API key

5. Create a `.env` file in the `backend` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
APP_API_KEY=dev-only-key
```

6. Start the backend server (keep this terminal open):

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. You should see output confirming the server is running.

### Step 2: Frontend Setup

**Open a new terminal** and:

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Create a `.env` file in the `frontend` directory:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_APP_API_KEY=dev-only-key
VITE_SHOW_DEV_TOOLS=true
```

**Environment Variables:**
- `VITE_API_BASE_URL` - Backend API endpoint
- `VITE_APP_API_KEY` - API key for authentication
- `VITE_SHOW_DEV_TOOLS` - Show "Load Example Data" button (set to `false` for production demos)

4. Start the frontend development server:

```bash
npm run dev
```

**Available scripts:**
- `npm run dev` - Development mode with dev tools enabled
- `npm run dev:demo` - Demo mode with dev tools hidden (uses `.env.demo`)
- `npm run build` - Production build

The frontend will be available at `http://localhost:5173` (or another port if 5173 is in use).

### Quick Start Summary

You need **two terminals running simultaneously**:

1. **Terminal 1** - Backend: `cd backend && uvicorn app.main:app --reload`
2. **Terminal 2** - Frontend: `cd frontend && npm run dev`

Once both are running, open your browser to the frontend URL (displayed in Terminal 2) to use the application.

## Testing the Application

### Load Example Data (Recommended)

The easiest way to test the application is to use the **"Load Example Data"** button in the top-right corner of the frontend. This will:

- Populate the current tab with example API responses
- Let you test the accept/reject functionality
- Show different clinical scenarios (conflicts, complete records, data quality issues)
- **Does not consume API quota** - uses pre-defined mock data

### Upload Sample JSON Files

Sample request files are provided in `sample-data/` if you want to test actual API calls:

- `reconciliation-example.json` - Standard medication reconciliation case
- `reconciliation-conflict.json` - Conflicting medication sources
- `data-quality-complete.json` - Complete patient record
- `data-quality-issues.json` - Record with quality issues

**To use:** Upload any of these files through the frontend UI upload component.

⚠️ **Note:** Uploading files sends real requests to the Gemini API and consumes your quota.

### Run Tests

Ensure you're in the `backend` directory with your virtual environment activated, then run:

```bash
python -m pytest
```

Run a specific test file:

```bash
python -m pytest tests/test_reconcile_validation.py
```

Run with verbose output:

```bash
python -m pytest -v
```

### Common Issues

If you get `ModuleNotFoundError: No module named 'app'`, make sure:
- you are running commands from the `backend` folder
- `pytest.ini` exists in `backend`
- your package folders contain `__init__.py`

Example `pytest.ini`:

```ini
[pytest]
pythonpath = .
testpaths = tests
```

---

## Architecture & Design

### LLM Choice

Google Gemini provides native JSON-mode with schema enforcement, good latency for small prompts, and a free tier for local testing. The API is straightforward and the safety/grounding controls are well documented.

### Prompting Strategy

The prompts in `backend/app/services/prompts.py` are designed to minimize model confusion by being explicit about evaluation criteria.

Key aspects:
- **Detailed scoring rubrics**: Each quality dimension (completeness, accuracy, timeliness, plausibility) has explicit 0-100 scoring bands so the model knows what score to assign based on the data state.
- **Reference ranges**: Vital sign normal ranges are included directly in the prompt so the model doesn't have to guess what "plausible" means for blood pressure or heart rate.
- **Conflict resolution priority**: For medication reconciliation, the prompt spells out exactly how to weight recent vs. reliable sources, preventing arbitrary tie-breaking.
- **Confidence calibration**: Explicit guidance on what confidence scores mean (0.9+ for agreement, 0.5-0.6 for equal conflict, etc.) keeps outputs consistent.
- **Edge case handling**: Common scenarios like "all sources agree" or "all data is stale" have prescribed behaviors to avoid hallucinated logic.

This approach trades prompt length for consistency. The model gets less room to improvise, which is exactly what you want when dealing with clinical data.

### Technology Stack

**Backend:**
- Python FastAPI - Simple, effective request handling with well-documented packages
- Google Gemini API - AI-powered analysis with structured JSON responses
- Pytest - Command-line testing

**Frontend:**
- TypeScript React - Type-safe component architecture
- TailwindCSS v4 - Utility-first styling
- ShadCN UI - Pre-built accessible components
- Vite - Fast development server and build tool
- Sonner - Toast notifications

### Key Design Decisions & Tradeoffs

#### 1. In-Memory Caching vs. Redis
**Decision:** Simple in-memory cache with TTL and size limits
**Rationale:** Zero dependencies, fast lookups (~50ms vs ~2s API calls), appropriate for single-server prototype. Production would need Redis for persistence and multi-instance support.

#### 2. Shared Secret Authentication vs. OAuth
**Decision:** Simple X-API-Key header authentication
**Rationale:** Demonstrates a basic auth flow. Healthcare production requires HIPAA compliance, RBAC, and audit logging; this prototype shows understanding while staying within assessment scope.

#### 3. Gemini Model Fallback Chain
**Decision:** Try multiple Gemini models (3.1 Flash Lite → 2.5 Flash -> 2.0 Flash) on rate limits
**Rationale:** Graceful degradation maximizes availability. Different models may vary in quality, but better user experience than immediate failures. 

#### 4. Detailed Prompts vs. Short Prompts
**Decision:** Long, explicit prompts with scoring rubrics and clinical reference ranges
**Rationale:** "Trade prompt length for consistency" - clinical data requires deterministic, predictable outputs. Model gets less room to improvise, which is exactly what you want for healthcare.

#### 5. Client-Side Duplicate Detection
**Decision:** Frontend compares reconciliation results to prevent duplicate cards
**Rationale:** Combined with backend caching for fast responses. Provides immediate user feedback via toast notifications when cache hits occur.

#### 6. Record Types for Flexible Data
**Decision:** Use `Record<string, any>` instead of strict interfaces for vital signs and lab values
**Rationale:** Pragmatic choice - vital signs vary by patient and context. Enforcing strict schemas would be brittle for clinical data that varies in completeness.

---

## Future Improvements

**Development Time:** Approximately 16 hours

### With More Time, I Would Improve:

#### Authentication & Security
- **Better API Key System**: Implement hashed API keys with expiration, rotation support, and per-user rate limiting
- **Rate Limiting**: Add token bucket or leaky bucket algorithm using Python's `time` module for more sophisticated rate limit handling across multiple instances
- **Request Correlation**: Add correlation IDs for request tracing and structured logging (JSON format) for production observability

#### Frontend UX Enhancements
- **Card Height Limits**: Implement max-height with scroll for cards to prevent extremely long pages and improve scanability
- **Pagination**: Add pagination for card lists (e.g., 10 cards per page) to improve performance with large datasets
- **Re-submission for Rejected Items**: Add ability to re-submit rejected AI suggestions with additional context or modified input, creating an iterative refinement workflow
- **Loading States**: Enhanced loading indicators beyond skeletons (progress percentages, estimated time remaining)

#### Backend Scalability
- **Distributed Caching**: Migrate to Redis for shared cache across multiple backend instances
- **Database Integration**: Add PostgreSQL for persistent storage of reconciliation history and audit trails. Would come easily with a Vercel integration.
- **Async Processing**: Implement background job queue (Celery/Redis) for batch processing and long-running LLM calls
- **Metrics & Monitoring**: Add Prometheus metrics for API latency, cache hit rates, LLM token usage

#### Testing & Quality
- **Integration Tests**: Add end-to-end API tests using TestClient
- **Load Testing**: Use Locust or k6 to verify performance under concurrent load
- **Contract Testing**: Add schema validation tests for LLM responses to catch prompt regressions

#### Clinical Features
- **Confidence Threshold Tuning**: Allow users to configure minimum confidence scores for auto-acceptance
- **Batch Upload**: Support uploading multiple patient records at once with progress tracking
- **Export Functionality**: Generate PDF/CSV reports of reconciliation results for clinical documentation
- **Version History**: Track changes to reconciliation decisions over time with rollback capability
