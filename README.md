# 🍽️ SipSync — Restaurant Management & Digital Ordering Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)](https://supabase.com/)
[![Render](https://img.shields.io/badge/Render-46E3B7?style=flat&logo=render&logoColor=black)](https://render.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A modern, decoupled hospitality management engine and digital ordering platform custom-built for **Raidan Restaurant** (Frazer Town, Bengaluru) to eliminate floor friction, synchronize inventory state in real-time, and streamline kitchen and billing operations.

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
  └── Dynamic NPCI UPI QR Generator
             │
             ▼ REST API (HTTPS / JSON)
[ Render ASGI Service (FastAPI) ]
  ├── Modular Routers (Menu, Reservations, Orders)
  ├── Pydantic V2 Request & Response Validation
  └── SQLAlchemy 2.0 Connection Pooler
             │
             ▼ Connection Pool (Port 5432)
[ Supabase Cloud (PostgreSQL) ]
  ├── Dynamic Inventory & Stock States
  ├── Reservation Schedules
  └── Customer Profiles & Order Logs
✨ Key Features
Interactive Floor Matrix: Real-time management across 22 operational units, including Ground Floor Standard Tables (T-01 to T-14), First Floor Majlis Carpet Cabins (M-01 to M-07), and the Private VIP Family Hall (VIP-01). Color-coded states indicate Vacant (Green), Cooking (Yellow), Dining (Blue), and Reserved (Purple).

Kitchen Display System (KDS): Automated polling with Web Audio API chime notifications (playKitchenChime()) for incoming customer orders, complete with 76mm/80mm thermal receipt printing formats (printKOT() & printCustomerBill()).

Dynamic UPI QR Billing: Generates NPCI-compliant deep-link payment payloads (raidan@upi) parameterized with exact transaction totals, alongside Cash and Card offline settlement options.

Sales Analytics & Item Performance: Built-in visual metrics tracking top-selling dishes by volume, category revenue contribution shares, and shift-wise revenue logs.

Table Reservations: Seamless guest booking portal with strict phone validation, date/time scheduling, and automated table assignment upon guest arrival.

🛠️ Technology Stack
Backend: Python 3.13, FastAPI, Uvicorn, SQLAlchemy 2.0, Psycopg3, Pydantic V2.

Database: PostgreSQL hosted on Supabase Cloud.

Frontend: HTML5, Vanilla JavaScript (ES6+), CSS3 (Grid/Flexbox), Chart.js (v4.4), QRCode.js.

Deployment: Render Web Services & Static Sites, custom domain routing via CNAME.

🚀 Local Development Setup
1. Clone the Repository
DOS
git clone [https://github.com/mohammedifteqhar/sipsync.git](https://github.com/mohammedifteqhar/sipsync.git)
cd sipsync
2. Configure Environment Variables
Create a .env file inside backend/app/ with your credentials:

Code snippet
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres
MANAGER_KEY=sipsync-admin-2026
3. Set Up Backend Virtual Environment
DOS
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
4. Run the Development Server
DOS
uvicorn app.main:app --reload --port 8000
API Docs: http://localhost:8000/docs

Frontend: Open frontend/index.html or frontend/order.html in your browser.

📄 License
Distributed under the MIT License. See LICENSE for more information.

👨‍💻 Author
Mohammed Ifteqhar
B.E. in Artificial Intelligence & Machine Learning

Vijaya Vittala Institute of Technology (VTU), Bengaluru

💻 Technical Skills
Python

FastAPI

Machine Learning

Deep Learning

SQL & PostgreSQL

REST API Development

Full-Stack Development

Data Science

TensorFlow & PyTorch

🔗 Connect With Me
GitHub: Mohammed Ifteqhar

LinkedIn: Mohammed Ifteqhar