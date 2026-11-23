# DocVera

DocVera is a document workspace with a React frontend and a FastAPI backend. Users can create an account, upload PDF/CSV/TXT documents, ask questions against extracted content, and translate text. The backend also includes answer grounding verification and an audit trail.

## Contents

- [Features](#features)
- [Technology and tools](#technology-and-tools)
- [Project layout](#project-layout)
- [How the processes work](#how-the-processes-work)
- [API routes](#api-routes)
- [Run locally on Windows](#run-locally-on-windows)
- [Configuration](#configuration)
- [Tests](#tests)
- [Current implementation notes](#current-implementation-notes)

## Features

- Account registration and login with bearer-token authentication.
- Per-user document listing, upload, viewing, and deletion.
- PDF, CSV, and plain text extraction, chunking, and indexing.
- Document question answering with retrieved excerpts and citations.
- Text translation to English, Hindi, Telugu, or Tamil.
- Backend endpoints for checking whether answer claims are supported by cited text.
- Request logging and a database-backed audit trail for significant actions.
- Responsive React interface with overview, document workspace, and translation screens.

## Technology and tools

| Area | Tools/libraries | Purpose |
| --- | --- | --- |
| Frontend | React 18, React DOM | Single-page user interface |
| Frontend build/dev server | Vite 6, `@vitejs/plugin-react` | Local development and production bundle |
| Icons and styling | `lucide-react`, CSS, Google Fonts (DM Sans and Manrope) | Interface icons and presentation |
| API | FastAPI, Uvicorn, Pydantic 2 | HTTP routes, request validation, and ASGI server |
| Persistence | SQLAlchemy 2, SQLite by default | Relational records for users, documents, queries, translations, verification reports, and audit events |
| Authentication | bcrypt, PyJWT, `cryptography` | Password hashing and signed JWT access tokens |
| Document processing | `python-multipart`, `pypdf`, Python `csv` and file I/O | File upload, PDF text extraction, CSV and TXT parsing |
| Retrieval and grounding | scikit-learn TF-IDF and cosine similarity, NumPy | Keyword-oriented chunk ranking and claim similarity checks |
| Translation | `deep-translator` using Google Translate | External text translation service |
| Tests | pytest, httpx | Backend test suite and HTTP test client support |

No external generative LLM is called by the question answering implementation. See [Current implementation notes](#current-implementation-notes).

## Project layout

```text
docvera/
├── README.md
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       └── styles.css
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── core/                 # settings, database, security
│   │   ├── models/               # SQLAlchemy tables and Pydantic schemas
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   ├── documents/
│   │   │   ├── query/
│   │   │   ├── verification/
│   │   │   ├── translation/
│   │   │   └── audit/
│   │   └── utils/                # logger
│   └── tests/                    # pytest tests and sample documents
└── scripts/                      # pipeline verification and demo data helpers
```

### Backend module responsibilities

- **`app/main.py`** creates the FastAPI app, initializes database tables at startup, configures development CORS, installs request logging, registers feature routers, and provides `/health`.
- **`app/core/config.py`** centralizes environment-backed settings: signing key, database URL, upload directory and size limit, allowed MIME types, and supported translation languages.
- **`app/core/database.py`** configures the SQLAlchemy engine/session, request-scoped database dependency, model metadata, and table creation.
- **`app/core/security.py`** hashes and verifies passwords, creates and decodes JWTs, and enforces document ownership.
- **`app/models/`** defines database entities and API schemas for users, documents/chunks, query records/citations, translation records, verification reports, and audit logs.
- **`app/features/auth/`** implements registration, login, bearer-token user lookup, and authenticated-user dependencies.
- **`app/features/documents/`** validates upload MIME type, size and PDF signature; stores and removes uploaded files; parses PDF/CSV/TXT; chunks content; and persists document processing status and chunks.
- **`app/features/query/`** creates per-document TF-IDF indexes, retrieves relevant chunks, assembles an extractive response with citations, persists query history, and logs the action.
- **`app/features/verification/`** extracts claims from a saved query answer, checks each against cited excerpts with TF-IDF/cosine similarity, and stores a grounding report.
- **`app/features/translation/`** calls the translation provider, stores translation requests/results, and exposes translation history.
- **`app/features/audit/`** logs HTTP method/path/status/duration and stores user action events such as document upload/deletion, queries, translations, and verification.
- **`app/utils/logger.py`** configures application logging.

## How the processes work

### 1. Sign up and authentication

1. The frontend posts email/password to `/auth/register` or `/auth/login`.
2. The backend stores a bcrypt password hash and, on successful login, returns a JWT.
3. The frontend keeps the token in browser `localStorage` and sends it as `Authorization: Bearer <token>` for protected API calls.
4. The backend resolves the token to a user and scopes document and history queries to that user.

### 2. Upload and document processing

1. The frontend sends a multipart upload to `/documents/upload`.
2. The backend checks the allowed content type, configured maximum size (10 MB by default), and PDF magic bytes for PDF uploads.
3. It creates a document row, writes the file under the configured upload directory, and processes it synchronously.
4. PDF pages are extracted with `pypdf`; CSV rows are read with `csv.DictReader`; TXT is read as UTF-8.
5. Text is divided into overlapping chunks (500 characters with 50-character overlap by default); CSV rows become individual table chunks.
6. Chunks are saved to SQLite and document status is moved through parsing, chunking, indexing, and ready (or failed).
7. The frontend refreshes its document list and opens the document workspace.

### 3. Ask a question

1. The frontend posts a document ID, question, language preference, and plain-language setting to `/query/`.
2. The backend checks document ownership, loads the document chunks, and builds a TF-IDF index if one is not cached.
3. Cosine similarity ranks chunks against the question; up to five relevant chunks are selected.
4. The response includes the selected source excerpts as the answer and as citations. Query history and an audit event are saved.

### 4. Translate text

The frontend posts text and language codes to `/translation/text`. The backend validates the target language, sends the text to Google Translate through `deep-translator`, stores the result, and returns it. The service splits long input into pieces of at most 4,500 characters before translation.

### 5. Verify an answer

The backend verification route takes a saved query record ID. It divides the answer into claims, compares claims with the excerpts saved as citations, calculates the fraction classified as grounded, persists the report, and logs the operation. This route exists in the API but is not currently exposed as a control in the frontend.

### 6. Audit and health

The middleware records each HTTP request in application logs. Feature services also write selected user actions to the audit database table. `/audit/` returns the authenticated user’s action history. `/health` is a lightweight API health check.

## API routes

All protected routes require `Authorization: Bearer <access_token>`.

| Method | Route | Auth | Purpose |
| --- | --- | --- | --- |
| `GET` | `/health` | No | API health response |
| `POST` | `/auth/register` | No | Create a user |
| `POST` | `/auth/login` | No | Login and receive JWT |
| `GET` | `/auth/me` | Yes | Current user profile |
| `POST` | `/documents/upload` | Yes | Upload and process a PDF, CSV, or TXT |
| `GET` | `/documents/` | Yes | List the current user’s documents |
| `GET` | `/documents/{document_id}` | Yes | Get one owned document |
| `DELETE` | `/documents/{document_id}` | Yes | Delete an owned document and its stored file |
| `POST` | `/query/` | Yes | Ask about a document and receive citations |
| `GET` | `/query/history` | Yes | List the current user’s saved questions |
| `POST` | `/translation/text` | Yes | Translate text and save the result |
| `GET` | `/translation/history` | Yes | List saved translations |
| `POST` | `/verify/` | Yes | Verify a saved query answer’s claims |
| `GET` | `/verify/{report_id}` | Yes | Get a verification report |
| `GET` | `/audit/` | Yes | List the current user’s audit events |

Interactive API documentation is available at `http://localhost:8000/docs` while the backend is running.

## Run locally on Windows

### Prerequisites

- Python 3.10 or newer.
- Node.js and npm.
- Internet access for Google Fonts and translation requests.

### 1. Start the backend

In PowerShell from the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. On startup, it creates the configured database tables. By default, SQLite uses `backend/docvera.db` when launched from the `backend` directory.

### 2. Start the frontend

Open another PowerShell window at the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL printed in the terminal (normally `http://localhost:5173`). The frontend expects the API at `http://localhost:8000` by default.

### Production frontend build

```powershell
cd frontend
npm run build
npm run preview
```

The production assets are generated in `frontend/dist/`.

## Configuration

Backend settings are read from environment variables or `backend/.env` (when starting the app from `backend`). Defaults are defined in `backend/app/core/config.py`.

| Setting | Default | Description |
| --- | --- | --- |
| `SECRET_KEY` | Development placeholder | JWT signing key; set a long random secret for real deployments |
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token lifetime |
| `DATABASE_URL` | `sqlite:///./docvera.db` | SQLAlchemy connection string |
| `UPLOAD_DIR` | `uploads` | Directory for user-uploaded files |
| `MAX_FILE_SIZE_MB` | `10` | Maximum permitted upload size |
| `ALLOWED_MIME_TYPES` | PDF, CSV, plain text | Accepted upload content types |
| `SUPPORTED_TARGET_LANGS` | `en, hi, te, ta` | Translation target language codes |

To point the frontend to a different API, create `frontend/.env.local`:

```dotenv
VITE_API_URL=http://your-api-host
```

Restart Vite after changing frontend environment variables. In a deployed setup, configure CORS to allow only the frontend’s origin and replace the default signing key.

## Tests

Backend tests are in `backend/tests/`. Run them from the `backend` directory after installing requirements:

```powershell
pytest
```

The test modules cover authentication, document processing, query, translation, verification, and audit behavior. Sample PDF and CSV input files are in `backend/tests/sample_data/`.

## Current implementation notes

- Question answering is extractive: it returns matching source passages. There is no OpenAI, Gemini, or other generative LLM integration in `query/llm_client.py`.
- Retrieval uses scikit-learn TF-IDF and cosine similarity. It is keyword-oriented rather than semantic search.
- The query response’s language value is stored, but the current answer-generation function does not translate the cited passages. Translation is provided separately by `/translation/text`.
- Verification uses lexical TF-IDF similarity as a grounding heuristic; its score is not a guarantee that a claim is factually correct.
- Translation requires an available network connection and relies on the external Google Translate service via `deep-translator`.
- PDF extraction reads embedded text. Image-only/scanned PDFs need OCR support, which is not included.
- The frontend currently includes login/registration, overview, upload/list/delete, document Q&A/history, and text translation. Verification and audit are backend API features without dedicated frontend screens.
- CORS currently allows all origins for development. Restrict this before public deployment.
