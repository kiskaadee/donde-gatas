# Technical Architecture: Novias del Gato

## Requirements

### Functional Requirements
*   **Dynamic Geolocation:** Interactive map showing Points of Interest (POI) with availability states: *On-Site*, *Moved*, or *Missing*.
*   **Hybrid Reporting System:** Interface to capture GPS coordinates and image metadata when reporting a sighting.
*   **Visual Validation Engine:** Comparison of image embeddings to ensure the photographed object is indeed the selected sculpture.
*   **Personal Catalog:** Persistence layer tracking which sculptures each unique user has visited, unlocking cultural content.

### Non-Functional Requirements
*   **Geographic Integrity (PostGIS):** Precision within 10 meters for proximity queries.
*   **API-First Methodology:** All business logic must reside in endpoints documented via OpenAPI.
*   **Recognition Latency:** Validation of image and location must not exceed 3 seconds.
*   **Basic Offline Availability:** Allow users to record sightings in low-signal areas and sync when connectivity returns.

## Tech Stack
*   **API / Contract:** OpenAPI (Swagger).
*   **Database:** PostgreSQL + PostGIS (Spatial data).
*   **Vector Search Engine:** `pgvector` (PostgreSQL extension) for storing and comparing image embeddings.
*   **Backend:** Python (FastAPI) for high-performance concurrency, business logic, and spatial/vector database routing.
*   **Identity (Auth):** Google OAuth + JWT.
*   **Frontend:** Next.js (PWA) using WebXR/Camera APIs for the Visual Check-in experience.
*   **Infrastructure:** Docker / Modular Monolith.

## Logical Services

### 1. Identity & Profile Service (SSO Adapter Architecture)
Manages user lifecycle and authentication via a pluggable Identity Provider adapter (`IdentityProvider` protocol).
- **Core Interface**: Decoupled from specific OAuth vendors via `verify_token(token: str) -> AuthUserIdentity`.
- **Implementations**:
  - `GoogleOAuthAdapter`: Production token verification using Google API certs.
  - `MockDevAdapter`: Local development and automated testing adapter issuing valid test sessions without external network dependencies.
  - Future-ready for Authelia / OIDC providers without modifying core routes.
- Maintains user profile attributes including `trust_score` (ranging from 0.0 to 1.0) and unlocked collection counts.

### 2. Integrity & Reputation Engine
Guards against malicious data pollution, spoofing, and bot abuse.
- **Velocity Checks**: Analyzes spatio-temporal deltas between consecutive user submissions (check-ins and tickets):
  $$v = \frac{d(p_1, p_2)}{\Delta t}$$
  If calculated speed $v > 120\text{ km/h}$ (maximum plausible urban velocity) and $\Delta t < 300\text{ s}$, the submission is rejected or tagged as suspicious.
- **Trust Score Adjustment**: Users start at baseline $0.5$. Successful verified crowdsourced reports increment `trust_score` by $+0.05$ (max $1.0$). Submissions caught spoofing or repeatedly rejected penalize trust by $-0.15$ (min $0.0$).

### 3. Hybrid Recognition Service
Validates "Check-ins" using client-side edge embeddings (MobileNetV2 1280-dimension float vector) and server-side spatial proximity:
- Coordinate proximity within 15 meters using PostGIS `ST_DWithin`.
- Cosine similarity threshold: $\text{similarity} = 1.0 - (\text{embedding} \Leftrightarrow \mathbf{v}_{\text{query}}) \ge 0.65$.

### 4. Interaction & Collection Service
Manages the many-to-many relationship between users and sculptures (unlocked achievements, captured photo galleries, and cultural audio/insights).

### 5. Crowdsourcing & Ticket Service
Manages citizen reports for moved, missing, or altered sculptures:
- Accepts coordinates, observed status, verification photo, and optional commentary.
- Groups overlapping submissions into spatial clusters ($\le 20\text{ m}$ radius) over a 48-hour window.

### 6. Location Tracker Service (The Oracle) & Hybrid Consensus Engine
Computes the single source of truth (SSOT) location and status of each sculpture:
- **Cluster Confidence Metric**:
  $$C_{\text{cluster}} = \sum_{i=1}^{N} \text{trust\_score}_i$$
- **Automatic State Transition**: If $C_{\text{cluster}} \ge 3.0$ with $N \ge 3$ distinct submitters and variance $\sigma_{\text{dist}} \le 20\text{ m}$, the Oracle automatically promotes the reported coordinates/status to the official sculpture record.
- **Moderator Escalation**: If $1.5 \le C_{\text{cluster}} < 3.0$ or reports have conflicting statuses, the cluster is held in `pending` state for manual moderator review via `/reports/{id}/verify`.

## Architecture Decision Records (ADR)
*   **Separation of Check-in vs. Ticket:** Allows the system to be usable even with incorrect location data, fostering community correction without blocking the fun.
*   **Single Database (pgvector + PostGIS):** Reduces network latency and synchronization complexity between spatial and vector data.
*   **PWA Priority:** Chosen for immediate access (QR/URL) over the friction of app store downloads, especially for tourists.
*   **SSO Adapter Pattern:** Isolates authentication provider logic behind a clean contract, allowing local offline testing and easy migration to alternative auth providers (e.g. Authelia) without touching business logic.
*   **Hybrid Consensus Threshold:** Combines automated confidence scoring ($\ge 3.0$) with human-in-the-loop moderator verification for ambiguous edge cases, balancing real-time responsiveness with catalog integrity.

