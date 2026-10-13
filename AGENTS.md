# Novias del Gato - Agent Guidelines & Workflow Rules

This document specifies the mandatory workflows, constraints, and quality gates for AI agents operating in this repository.

---

## 1. Core Operating Constraints

- **No Direct Commits to `main`**: Agents must never commit directly to the `main` or `master` branches. All changes must be developed on descriptive feature, bugfix, or documentation branches (`feat/*`, `fix/*`, `docs/*`).
- **No Destructive Git Actions**: Commands such as `git reset --hard`, `git restore <file>`, `git clean -fd`, and force-pushes (`git push --force`) are strictly prohibited without the user's explicit written approval.
- **Secret Redaction**: Never print, commit, or log sensitive information (tokens, secrets, private keys, database passwords, API credentials). Use environment variables and `.env` files (which must be ignored in `.gitignore`).
- **Session Modes**:
  - `learning`: The user drives and writes the reasoning, the agent asks guiding questions.
  - `delivery`: The agent may draft code and plans, presenting rationale and trade-offs.

---

## 2. Verification Gates (Pre-Commit Checklist)

Before any commit is proposed or executed, agents must execute and verify the following commands from the repository or `api/` directory:

1. **Ruff Formatting**:
   ```bash
   uv run ruff format --check .
   ```
2. **Ruff Linting**:
   ```bash
   uv run ruff check .
   ```
3. **Static Type Checking (Pyright)**:
   ```bash
   uv run pyright
   ```
4. **Automated Test Suite (Pytest)**:
   ```bash
   uv run pytest
   ```

No commit may be generated if any of these checks fail or report unhandled errors.

---

## 3. Architecture & Domain Directives

- **API-First Architecture**: Endpoints and schemas in `api/` must stay aligned with `docs/openapi_unified.yaml`.
- **SSO Identity Provider Pattern**: Authentication logic must be decoupled behind the `IdentityProvider` interface/adapter protocol. Do not hardcode vendor-specific auth checks in core routes.
- **Edge Inference Model Invariant**: Vector embeddings (1280 floats via MobileNetV2) are generated on client devices (WebAssembly/WebGL via ONNX Runtime Web). The backend never runs heavy deep learning inference on check-ins; it performs spatial proximity checks (PostGIS) and cosine similarity queries (`pgvector`).
- **Spatial & Vector Integrity**: Coordinates must use EPSG:4326 (WGS84). Embeddings must be 1280-dimension L2-normalized float vectors.

---

## 4. Agent Directory & Delegation

When working on specialized sub-domains:
- **Anne Droid** (`profile/agents/anne-droid.md`): Consult for UX flow, client accessibility, or backend API contract changes that impact the UI. Delegate to Anne for frontend component styling, PWA camera/canvas interaction, or client-side tests on `feat/anne/*` branches.
- Do not invoke Anne Droid for backend-only logic, database migrations, or Docker infrastructure.
