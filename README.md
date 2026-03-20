Note: this project requires you to have your own OpenAI API key.
To confirm that your API key will work with this project:
Bash:
echo $OPENAI_API_KEY

If there is no output, go to https://platform.openai.com/api-keys or retrieve your key and type:
Bash:
export OPENAI_API_KEY='YOUR_API_KEY'

I chose to work with the OpenAI API for a few reasons
- Familiarity: I have worked primarily with GPT in my career, so sticking with what I know helps my confidence in what I'm coding
- Well Tested Python Repository: Due to the popularity of OpenAI, the Python repository is well maintained and documented


Nixing all of the above.
I was going to go with OpenAI since I'm most familiar with it, but there are no free models on OpenAI
Google AI Studio has free options. Many different models have 5/minute and 20/day rates. Structuring a system that goes through 3 (as a basic version) is relatively simple 
Google is reliable, and its documentation matches, if not exceeds, OpenAI's


## Local setup

### Backend
Create and activate a virtual environment, then install dependencies.

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Then install packages:

```bash
pip install -r requirements.txt
```

Create a `.env` file in `backend` with:

```env
OPENAI_API_KEY=your_openai_api_key_here
APP_API_KEY=dev-only-key
```

Run the backend:

```bash
uvicorn app.main:app --reload
```

The API should be available at `http://127.0.0.1:8000`.

### Frontend
Install dependencies:

```bash
cd frontend
npm install
```

Create a `.env` file in `frontend` with:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_APP_API_KEY=dev-only-key
```

Run the frontend:

```bash
npm run dev
```

### Run tests

From the `backend` folder:

```bash
python -m pytest
```

Run one test file:

```bash
python -m pytest tests/test_llm_service.py
```

### Common issues

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