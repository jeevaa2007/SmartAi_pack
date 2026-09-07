# SmartPack AI: Technical Infrastructure Scaffolding

AI-Powered Packing Quality Verification Platform for Dark Store Operations.

---

## Workspace Layout
```
d:\SmartPackAI\
├── .gitignore                     # Git tracking exclusions
├── docker-compose.yml             # Container orchestration definitions
├── .env.example                   # Baseline environments options
├── README.md                      # Infrastructure documentation
│
├── backend/                       # FastAPI codebase
│   ├── requirements.txt           # Dependency specifications
│   ├── Dockerfile                 # Multi-stage security container
│   ├── alembic.ini                # Migrations controller
│   └── src/
│       ├── main.py                # App configuration gateway
│       ├── core/                  # Settings, exceptions, logging configurations
│       ├── database/              # Connections & dependency injections
│       ├── security/              # Cryptographic validators (passlib)
│       └── [placeholders]         # models/, services/, repositories/, etc.
│
├── frontend/                      # TypeScript Next.js App Router codebase
│   ├── package.json               # Node dependency declarations
│   ├── tsconfig.json              # absolute path configuration mapping
│   ├── next.config.js             # Transpile libraries, output standalone setting
│   ├── Dockerfile                 # Multi-stage container (production server runner)
│   └── src/
│       ├── app/                   # Layout, CSS, sitemap config
│       ├── components/            # flicker-free registry
│       ├── services/              # Axios instance configuration
│       ├── styles/                # custom Ant Design theme tokens
│       └── [placeholders]         # layouts/, hooks/, types/, etc.
│
└── ai_engine/                     # Computer Vision codebase
    └── [placeholders]             # models/, training/, datasets/, rules/, etc.
```

---

## Getting Started

### 1. Developer Environment Variables
Copy `.env.example` to `.env` inside the workspace root:
```bash
cp .env.example .env
```
Ensure `JWT_SECRET` contains a cryptographically secure key and `DATABASE_URL` matches your database address.

### 2. Startup Commands
*   **Docker Container Orchestration:**
    ```bash
    docker compose up --build
    ```
*   **Locally (Standard Execution):**
    *   *Backend:* `cd backend && python -m uvicorn src.main:app --reload`
    *   *Frontend:* `cd frontend && npm run dev`

---

## Coding Protocols

### Python Code Standards (PEP 8)
*   **Formatting:** Enforced automatically via VS Code settings using `Ruff` or `black` formatting engine.
*   **Types:** Standard Python type annotations are required on all functions and variables.
*   **Naming Style:**
    *   Classes: PascalCase
    *   Variables & Methods: snake_case
    *   Constants: UPPERCASE_SNAKE

### TypeScript / Next.js Standards
*   **Style Rules:** Enforced via `eslint` and `prettier` config files.
*   **Imports:** Always import utilizing absolute path maps:
    ```typescript
    import { themeConfig } from '@/styles/theme';
    ```

---

## Logging Configuration
Logs are written to `backend/logs/` and split by category:
*   `sys.log`: Framework startups, system configuration validations, and shutdowns.
*   `db.log`: Output of all SQLAlchemy statements.
*   `ai.log`: OpenCV captures, YOLO inference scores, and coordinate evaluations.
*   `error.log`: Capture warning and critical level exceptions across all services.
*   `audit.log`: Trace trails of supervisor override events and authorization events.

---

## Error Handling Specifications
Custom API exceptions inherit from `AppException` in `backend/src/core/exceptions.py`. The gateway intercepts validation flaws and server exceptions, parsing them to clients in a standard structure:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input validation failed on incoming request parameters.",
    "details": [
      {
        "field": "order_id",
        "issue": "Field must be a valid UUID format."
      }
    ]
  }
}
```
