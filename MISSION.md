# Mission: CorporateMemory
**Enterprise B2B SaaS Logic & RAG Platform (Arabic/RTL)**

## 🚀 Overview
CorporateMemory is a B2B SaaS Enterprise RAG platform designed for companies to strictly organize their knowledge. It features strict multi-tenancy, an Arabic-first UI, and leverages Google Gemini 1.5 Pro with managed File Search.

## 🏗 Architecture
- **Monorepo**: Shared codebase for unified development.
- **Backend**: Python FastAPI (Async) + Google GenAI SDK.
- **Frontend**: Next.js 15 (App Router) + Tailwind v4 + Shadcn UI.
- **Database**: PostgreSQL + SQLAlchemy (Async) + Alembic.
- **AI**: Gemini 1.5 Pro + File Search API.

## 📅 Implementation Plan

### Phase 1: Foundation Setup
- [ ] Initialize Monorepo (`/backend`, `/frontend`, `/shared`).
- [ ] Configure `docker-compose.yml` for PostgreSQL.
- [ ] Set up minimal FastAPI app with Health Check.
- [ ] Set up Next.js 15 app with Tailwind v4.

### Phase 2: Database & Multi-Tenancy (Backend)
- [ ] Design Schema: `Tenant` (Organization), `Workspace`, `User`.
- [ ] Design Schema: `Document` (Metadata for uploaded files).
- [ ] Implement Dependency Injection for DB Sessions.
- [ ] Implement "Tenant Resolution" middleware (Header-based or Subdomain).

### Phase 3: RAG Pipeline with Gemini
- [ ] Integreate `google-genai` SDK.
- [ ] creating `FileSearchStore` manager.
- [ ] **Critical**: Ensure 1-to-1 mapping of `Workspace ID` <-> `FileSearchStore ID`.
- [ ] Implement File Upload Endpoint:
    - Upload to local temp -> Upload to Gemini File API -> Poll for Active State -> Link to Workspace Store.

### Phase 4: Frontend Dashboard (RTL)
- [ ] Configure `html dir="rtl"` and Tailwind logical properties.
- [ ] Build Layout: Sidebar (Collapsible), Topbar (User Profile).
- [ ] Implement Tabs: Dashboard, Database (Files), Chat.
- [ ] Connect "Database" tab to backend upload API.

### Phase 5: Smart Chat Interface
- [ ] Build Chat UI (User Message / AI Response).
- [ ] Connect to backend RAG endpoint.
- [ ] Display "Citations" returned by Gemini API.
- [ ] System Prompt Engineering: Force Professional Arabic.

### Phase 6: Polish & Bonus
- [ ] Audio Summary generation (Gemini -> Text Script -> TTS).
- [ ] Deployment Configuration (Dockerfile).
