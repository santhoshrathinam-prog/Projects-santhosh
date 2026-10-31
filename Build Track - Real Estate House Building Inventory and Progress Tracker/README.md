# Build Track - Real Estate House Building Inventory and Progress Tracker

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask_3.0-lightgrey.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/Database-MySQL_8.0-orange.svg)](https://www.mysql.com/)
[![Academic](https://img.shields.io/badge/Academic-SRM_IST_MCA_2026-brightgreen.svg)]()

> **Master of Computer Applications (MCA - Semester III)**  
> **Course**: Mini Project / Internship Viva Voce (NOV 2026)  
> **Institution**: Directorate of Online Education, SRM Institute of Science and Technology, Kattankulathur  
> **Student**: Santhosh Rathinam M (`EA2532251010685`)  

---

## 📌 Executive Summary

**Build Track** is a centralized, role-based real estate inventory management and house building milestone tracking web platform. It addresses the systemic challenges of materials shrinkage, ghost stock allocations, unverified contractor milestone claims, and lack of visual proof in multi-plot residential construction projects.

By unifying **inward material dispatch logging**, **concurrency-controlled outward allocations (ACID)**, and **real-time WebRTC camera progress snapshots**, Build Track guarantees 100% auditable construction workflows from foundation excavation to handover.

---

## 🚀 Key Functional Capabilities

1. **Role-Based Access Control (RBAC)**:
   - **Admin / Management**: Complete system governance, project budgeting, role provisioning, and audit ledger.
   - **Builder / Project Manager**: Multi-house milestone sign-offs, stage progression, material requisitions.
   - **Site Engineer**: Live material inward logging, physical stock dispatch, WebRTC camera photo evidence capture.
   - **Civil Estimator & Auditor**: Bill of Quantities (BOQ) planning, stock reconciliation, consumption anomaly detection.

2. **ACID Transaction & Concurrency Engine**:
   - Implements pessimistic row-level locking (`SELECT ... FOR UPDATE`) in MySQL to prevent negative stock balances and double-allocations during simultaneous site dispatches.

3. **Field Evidence Verification (WebRTC Camera Integration)**:
   - Built-in HTML5 WebRTC MediaStream API capturing live high-resolution on-site photos directly from laptops, tablets, or phones without third-party apps.

4. **Automated Stock Warning System**:
   - Proactive alert triggers for safety stock thresholds across cement, steel, sand, aggregate, bricks, and electricals.

---

## 🏗️ System Architecture

Build Track follows a clean 3-tier decoupled architecture:

- **Presentation Layer**: Responsive UI built with HTML5, CSS3, Bootstrap 5, Chart.js, and WebRTC MediaStream capture.
- **Application Logic Tier**: Python 3.10+ Flask framework with role decorators, session management, and validation.
- **Data Persistence Layer**: MySQL 8.0 relational database with normalized schema (3NF), foreign keys, and cascading constraints.

---

## 📂 Repository Structure

```
Build Track - Real Estate House Building Inventory and Progress Tracker/
├── app.py                             # Core Flask backend application & routing
├── config.py                          # Application settings & database configurations
├── db.py                              # Database connection manager & transaction helpers
├── seed_data.py                       # Automated realistic database seeding script
├── requirements.txt                   # Production Python package dependencies
├── .env.example                       # Environment configuration template
├── build_viva_slides.py               # Automated 18-slide Viva Voce PowerPoint generator
├── compile_10_chapters_report.py      # Automated 10-chapter master report generator
├── database/
│   └── schema.sql                     # Full MySQL DDL schema with tables and constraints
├── static/
│   ├── css/style.css                  # Custom responsive styling and theme variables
│   └── js/
│       ├── script.js                  # Frontend client logic & WebRTC camera controller
│       └── charts.js                  # Chart.js analytics visualizations
├── templates/                         # 19 Jinja2 HTML templates for all user portals
├── diagrams/                          # Architectural DFDs, UML diagrams, & UI screenshots
└── reports/                           # Academic Project Deliverables:
    ├── Build_Track_Real_Estate_Final_Internship_Report.docx  # 30+ Page Master Report
    ├── Build_Track_Real_Estate_Internship_Viva_Presentation.pptx # 18-Slide Viva Deck
    ├── Build_Track_Real_Estate_Design_Documentation.docx
    ├── Build_Track_Real_Estate_Implementation.docx
    ├── Build_Track_Real_Estate_Testing.docx
    ├── Build_Track_Real_Estate_Tools_and_Technologies.docx
    ├── Build_Track_Real_Estate_Conclusion.docx
    ├── Build_Track_Real_Estate_Appendices.docx
    └── Build_Track_Real_Estate_References.docx
```

---

## ⚙️ Installation & Local Setup

### 1. Prerequisites
- Python 3.10 or higher
- MySQL Server 8.0+

### 2. Clone the Repository
```bash
git clone https://github.com/santhoshrathinam-prog/Projects-santhosh.git
cd "Projects-santhosh/Build Track - Real Estate House Building Inventory and Progress Tracker"
```

### 3. Create & Activate Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Database & Environment
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Update `.env` with your MySQL credentials:
   ```ini
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=real_estate_db
   SECRET_KEY=your_secret_key
   ```
3. Initialize the database schema:
   ```bash
   mysql -u root -p real_estate_db < database/schema.sql
   ```
4. (Optional) Populate demo sample data:
   ```bash
   python seed_data.py
   ```

### 6. Run the Application
```bash
python app.py
```
Open your browser at: `http://127.0.0.1:5000`

---

## 🎓 Academic Verification & Deliverables

- **Student Name**: Santhosh Rathinam M
- **Enrolment Number**: EA2532251010685
- **University**: Directorate of Online Education, SRM Institute of Science and Technology
- **Program**: Master of Computer Applications (MCA - III Semester)
- **Examination**: Internship Viva Voce (NOV 2026)
