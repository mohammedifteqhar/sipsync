# ☕ SipSync — Cloud Cafe Operations & Virtual Concierge

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)](https://supabase.com/)
[![Render](https://img.shields.io/badge/Render-46E3B7?style=flat&logo=render&logoColor=black)](https://render.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A modern, decoupled hospitality management engine and digital guest concierge designed to eliminate floor friction, synchronize inventory state in real-time, and streamline cafe operations.

---

## 🌐 Live Deployments

- **Manager Dashboard**: [sipsync-dashboard.onrender.com](https://sipsync-dashboard.onrender.com)
- **Interactive REST API (Swagger UI)**: [sipsync-api-k9tz.onrender.com/docs](https://sipsync-api-k9tz.onrender.com/docs)

---

## 🏗️ System Architecture

```text
[ Table QR Code / Web Browser ]
             │
             ▼
[ Render CDN (Static Frontend) ]
  ├── Vanilla DOM Engine (Sub-second load)
  ├── Chart.js Visual Analytics
  └── AI Chat Concierge Drawer
             │
             ▼ REST API (HTTPS / JSON)
[ Render ASGI Service (FastAPI) ]
  ├── Modular Routers (Menu, Reservations, Chat)
  ├── Pydantic V2 Request & Response Validation
  └── SQLAlchemy 2.0 Connection Pooler
             │
             ▼ Connection Pool (Port 5432)
[ Supabase Cloud (PostgreSQL) ]
  ├── Dynamic Inventory States
  ├── Reservation Schedules
  └── Customer Profiles & Order Logs