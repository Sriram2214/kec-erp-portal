# 🎓 KEC Examination ERP (Kings Engineering College)

A premium, full-stack Examination Management System designed for **Kings Engineering College (KEC)**. This portal provides a unified interface for Admins, Faculty, and Students to manage academic data, attendance, internal marks, and end-semester examinations.

---

## 🚀 Project Overview

The KEC ERP is a "Next-Gen" institutional platform built to handle the entire lifecycle of an academic semester. From master data management to generating high-quality PDF Hall Tickets, it is designed for scale, security, and speed.

### 🌟 Key Features

### 🏛️ Admin Portal ("God Mode")
- **Visual Analytics**: Interactive charts showing student and faculty distribution.
- **Master Data Management**: Centralized control over Degrees, Departments, Batches, and Regulations.
- **Publication Controls**: Global toggles to release/unrelease Hall Tickets and Results.
- **Bulk Data Handling**: High-speed Excel upload for student and faculty records.
- **Student Management**: Individual control over hall ticket generation and result publication.

### 👨‍🏫 Faculty Portal
- **Class Assignments**: View assigned courses and batches.
- **Attendance Tracking**: Real-time, day-wise attendance entry for assigned classes.
- **Internal Assessment**: Direct entry of IA marks and assignment scores.

### 👨‍🎓 Student Portal
- **Dashboard**: Quick view of status and announcements.
- **Hall Tickets**: Download official PDF Hall Tickets (once released by Admin).
- **Results**: View semester-wise grades and performance analysis.

---

## 🛠️ Tech Stack

- **Frontend**: React 18, Vite, Chart.js, Vanilla CSS (Premium Aesthetics).
- **Backend**: Flask (Python), Flask-SQLAlchemy, Flask-Login.
- **Server**: Waitress (Production-grade WSGI).
- **Database**: SQLite with WAL mode (Concurrent-safe for 1000+ users).
- **Deployment**: Docker, Docker Compose.
- **Reports**: ReportLab (High-fidelity PDF generation), OpenPyXL (Excel processing).

---

## 📦 Installation & Setup

### 🐳 Option A: Docker (Easiest / Recommended)
Perfect for sharing with friends or deploying to a server.
1. Ensure Docker Desktop is running.
2. Open a terminal in the project root.
3. Run:
   ```bash
   docker-compose up --build -d
   ```
4. Access the portal at: `http://localhost:5000`

### 💻 Option B: Local Development
1. **Backend**:
   - Install dependencies: `pip install -r requirements.txt`
   - Run: `python run.py`
2. **Frontend**:
   - Go to `frontend/`: `cd frontend`
   - Install: `npm install`
   - Run: `npm run dev`
3. Access at: `http://localhost:3000`

---

## 📂 Project Structure

```text
KCE ERP/
├── app/                # Flask Backend Logic
│   ├── api/            # Modular API Routes
│   ├── static/dist/    # Compiled React Frontend
│   └── models.py       # Database Schema
├── frontend/           # React Source Code
│   ├── src/            # Components, Pages, Context
│   └── public/         # Static assets (Banners, Logos)
├── instance/           # Database & Local storage
├── Dockerfile          # Multi-stage Docker build
└── wsgi.py             # Production entry point
```

---

## 📝 License
Proprietary software for Kings Engineering College (KEC). All rights reserved.
