# AI Research Agent

An AI-powered research assistant built with **FastAPI**, **LangGraph**, and **React**. Give it a topic and it will plan research questions, search the web, rank the evidence, write a source-backed Markdown report, ask a human to approve or request changes, and then answer follow-up questions about the report.

## Features

- Multi-step agentic workflow powered by LangGraph
- Web research using Tavily, with FlashRank relevance reranking
- Streamed Markdown report generation
- Inline numbered citations with an auto-generated References section
- Human-in-the-loop review: approve or request changes
- Streaming follow-up Q&A grounded in the report
- Thread-based state with LangGraph checkpointing

## Workflow

```text
User topic
    |
planner          -> research questions + report metadata (title, sections)
    |
researcher       -> Tavily web search + FlashRank reranking
    |
writer           -> streamed Markdown report with citations
    |
human_review     -> approve -> END -> follow-up chat
    |
    +-> request changes -> researcher (revision loop, max 3 retries)
```

A follow-up question sent to an existing thread skips the pipeline and goes straight to the `follow_up` node.

## Project Structure

```text
RAG/
├── main.py                  # FastAPI app and API routes
├── requirements.txt         # Python dependencies
├── .env                     # API keys (not committed)
├── app/
│   ├── graph.py             # LangGraph nodes and edges
│   ├── state.py             # Shared ResearchState schema
│   ├── config.py            # Gemini LLM setup
│   ├── planner.py           # Research questions + report outline
│   ├── researcher.py        # Tavily search + FlashRank reranking
│   ├── writer.py            # Streams the report
│   ├── citations.py         # Source numbering + References section
│   ├── human_review.py      # interrupt() human-in-the-loop gate
│   ├── routers.py           # Review routing logic
│   └── followup.py          # Follow-up answer generation
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── components/
    │   │   ├── ResearchInput.jsx
    │   │   ├── ReportViewer.jsx
    │   │   ├── Markdown.jsx
    │   │   ├── HumanReview.jsx
    │   │   └── FollowUpChat.jsx
    │   └── services/
    │       └── api.js
    ├── package.json
    └── vite.config.js
```

## Tech Stack

**Frontend**

- React 19
- Vite
- Tailwind CSS 4
- react-markdown + remark-gfm
- axios

**Backend**

- Python 3.12
- FastAPI
- LangGraph
- LangChain
- Tavily
- FlashRank

**AI**

- Google Gemini via `langchain-google-genai`

## Prerequisites

- Python 3.12+
- Node.js 18+
- Google Gemini API key
- Tavily API key

## Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
```

`.env` is already listed in `.gitignore`.

## Backend Setup

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

The backend runs at `http://127.0.0.1:8000`.

The first run after installing FlashRank may be slower while its reranking model loads.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on Vite's default port (`http://localhost:5173`). The backend URL is configured in `frontend/src/services/api.js`.

## API Endpoints

| Method | Endpoint      | Body                                   | Response                          |
|--------|---------------|----------------------------------------|-----------------------------------|
| POST   | `/research`   | `{ "topic": "..." }`                   | NDJSON stream                     |
| POST   | `/review`     | `{ "thread_id", "approved", "feedback" }` | Approval status or revised report |
| POST   | `/follow-up`  | `{ "thread_id", "question" }`          | NDJSON stream                     |

### Streaming events

`/research` returns newline-delimited JSON (`application/x-ndjson`) with these event types:

- `thread_id` — thread created for this research session
- `report_meta` — title, subtitle, and category
- `report_chunk` — a piece of the streamed report
- `review_ready` — final report and metadata, ready for human review

`/follow-up` streams `followup_chunk` events.

## How Citations Work

1. `researcher.py` collects web results from Tavily and reranks them with FlashRank.
2. `citations.py` deduplicates sources by URL and assigns numbers `[1]`, `[2]`, ...
3. `writer.py` sends the numbered evidence to the LLM and requires citations only from that evidence.
4. The LLM writes the report without a References section.
5. `validate_report` removes any References section the model wrote and appends a clean, deterministic one.
6. `Markdown.jsx` renders the report and turns inline `[n]` citations into links.

## Deployment

### Backend — Render (recommended)

- Create a new Web Service from the repository.
- Build command: `pip install -r requirements.txt`
- Start command:

  ```bash
  uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
  ```

- Add `GOOGLE_API_KEY` and `TAVILY_API_KEY` in the Render dashboard.
- Update the CORS `allow_origins` list in `main.py` to your frontend domain before going live.
- Use an instance with enough memory (about 1 GB) for the FlashRank model.

Run a **single worker/instance**. The app uses an in-memory checkpointer, so multiple processes would not share thread state.

### Frontend — Vercel (recommended)

- Import the repository and set the project root to `frontend`.
- Framework preset: Vite
- Build command: `npm run build`
- Output directory: `dist`
- Before deploying, update the backend URL in `frontend/src/services/api.js` to your deployed backend URL.

If the frontend is served over HTTPS, the backend must also use HTTPS (Render and Railway provide this by default).

## Limitations

- Thread state is stored in memory and is lost when the backend restarts.
- The app is designed to run as a single backend instance.
- Reports are grounded in Tavily snippets, not full-page verification.
- There is no automated fact-checking step in the current MVP.

## Key Concepts Demonstrated

- LangGraph `StateGraph`, conditional edges, and checkpointing
- Human-in-the-loop with `interrupt()` and `Command(resume=...)`
- LLM streaming with `stream_writer` and FastAPI `StreamingResponse`
- Consuming NDJSON streams in React with `ReadableStream`
- Retrieval-grounded report writing with numbered citations

## Frontend Scripts

```bash
npm run dev       # Start development server
npm run build     # Production build
npm run lint      # Run ESLint
npm run preview   # Preview production build
```
