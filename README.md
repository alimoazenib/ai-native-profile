# AI-Native Personal Profile

An interactive, autonomous AI-Native personal webpage for the **AI-Native Systems Design** course at **Sharif University of Technology**.

---

## Architecture & Features

1. **Zero-Hallucination Grounding**: The AI model answers strictly using facts stored in `data/profile.json` or live responses from the external API. No background knowledge is hallucinated.
2. **Intent Handling**: Automatically resolves `project_summary`, `reading_suggestion`, and `job_fit` intents. Prompts clarifying questions if inputs are ambiguous.
3. **Explicit Guardrails & Authority Limits**: Rejects requests regarding grades, personal contact information, or unofficial university representation.
4. **Live Explainability Panel**: Inspects and renders the detected Intent, Capability, JSON Fields Read, and External API calls in real time.
5. **External API Integration**: Integrates directly with the **GitHub REST API** to query user repositories and commit metadata.
6. **Creativity Feature**: Includes a real-time Skill Match & Job-Fit Scorer with transparent skill breakdown.

---

## Structure

```
ai-native-profile/
├── Dockerfile          # Container definition
├── requirements.txt    # Python dependencies
├── .dockerignore       # Build exclusions
├── .env.example        # Env template
├── .env                # Local secrets
├── .gitignore          # Git ignore rules
├── README.md           # This file
├── data/
│   └── profile.json    # Ground-truth record (courses, projects, guardrails)
├── static/
│   ├── index.html      # Frontend user interface
│   ├── style.css       # Styling and responsiveness
│   └── app.js          # Frontend client and explainability renderer
└── app/
    ├── __init__.py
    ├── config.py       # Env configuration
    ├── schema.py       # Pydantic schemas
    ├── external_api.py # GitHub REST API client
    ├── agent.py        # Agent + LLM interaction
    └── main.py         # FastAPI application routes
```

---

## Run

**Locally:**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with your values
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Docker:**

```bash
docker build -t ai-native-profile .
docker run -p 8000:8000 --env-file .env ai-native-profile
```

**Health check:** `GET /api/healthz`

---