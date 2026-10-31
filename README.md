# 🌱 FarmDirect – Farmer-to-Consumer Agricultural Marketplace

**FarmDirect** is a complete, beginner-friendly web application designed as a **College Mini-Project**. It establishes a direct digital marketplace connecting local agricultural farmers directly with end-consumers, bypassing multi-tiered commission agents and wholesale middlemen to ensure fair remuneration for farmers and fresh produce for consumers.

---

## 📌 Two-Tier Quality & Verification Architecture

To protect consumers and maintain marketplace authenticity, FarmDirect implements a strict **Two-Tier Governance Model**:

```text
               ┌─────────────────────────────────┐
               │    Farmer Registers Account     │
               └────────────────┬────────────────┘
                                │ (verification_status = 'pending')
                                ▼
               ┌─────────────────────────────────┐
               │    Admin Verifies Farmer        │
               └────────────────┬────────────────┘
                                │ (verification_status = 'verified')
                                ▼
               ┌─────────────────────────────────┐
               │   Farmer Adds Product + Photo   │
               └────────────────┬────────────────┘
                                │ (approval_status = 'pending')
                                ▼
               ┌─────────────────────────────────┐
               │     Admin Reviews & Approves    │
               └────────────────┬────────────────┘
                                │ (approval_status = 'approved')
                                ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ Customer Marketplace: Visible & Available for Direct Order  │
   └─────────────────────────────────────────────────────────────┘
```

### 🔒 Customer Marketplace Visibility Rule
Customers can **ONLY** browse, view, add to cart, and purchase crops when **ALL** conditions are satisfied in the database:
1. `f.verification_status = 'verified'` (Farmer is verified by Admin)
2. `p.approval_status = 'approved'` (Product is approved by Admin)
3. `p.product_status = 'available'` (Product is in stock & active)

---

## 📸 Image & Media Upload Architecture

FarmDirect features a lightweight, college-friendly image upload and media management architecture:

### 1. Storage & Path Structure
Uploaded images are safely stored in dedicated filesystem directories, with only relative path references tracked in MySQL:
- **Product Images**: `static/uploads/products/` (`prod_<uuid10>_<secure_filename>.jpg`)
- **Farmer Profiles**: `static/uploads/profiles/farmers/` (`farm_<uuid10>_<secure_filename>.png`)
- **Customer Profiles**: `static/uploads/profiles/customers/` (`cust_<uuid10>_<secure_filename>.png`)
- **Delivery Partner Profiles**: `static/uploads/profiles/delivery/` (`delv_<uuid10>_<secure_filename>.png`)
- **Admin Profiles**: `static/uploads/profiles/admin/` (`admn_<uuid10>_<secure_filename>.png`)

### 2. Validation & Security Controls
- **Max File Size**: 5MB per upload (`MAX_CONTENT_LENGTH = 5 * 1024 * 1024`).
- **Allowed Formats**: `.jpg`, `.jpeg`, `.png`, `.webp`.
- **Security**: Filenames sanitized via `werkzeug.utils.secure_filename` and prefixed with unique UUID tokens to prevent directory traversal and file collisions.
- **Fallbacks**: Responsive SVG placeholder illustrations (`default_product.svg`, `default_avatar.svg`, `default_farmer.svg`) when no photo is uploaded or file is deleted.
- **Laptop Webcam Capture**: Full `navigator.mediaDevices.getUserMedia({ video: true })` integration with live video feed, canvas capture, stream track cleanup, and dual buttons (`[ 📷 Take Photo (Webcam) ]` / `[ 🖼️ Choose from Gallery ]`).

---

## 💳 Demo Payment System Architecture

FarmDirect incorporates a safe, academic-grade **Demo Payment Simulation** designed specifically for college mini-projects:

### 1. Payment Options Supported
- **Cash on Delivery (COD)**:
  - `payment_method = 'cod'`
  - `payment_status = 'pending'`
- **UPI – Demo Simulation (GPay / PhonePe / Paytm)**:
  - `payment_method = 'upi'`
  - `payment_status = 'paid'`
  - Generates a dynamic Demo SVG QR code for visual presentation (`FarmDirect DEMO | Amount: ₹...`).
  - Generates demo transaction reference (e.g. `DEMO-UPI-1772345678`).
- **Debit / Credit Card – Demo Simulation**:
  - `payment_method = 'card'`
  - `payment_status = 'paid'`
  - Clean demo card interface with auto-fill button (`Demo User`, `4111 1111 1111 1111`, `12/30`, `123`).
  - Generates demo transaction reference (e.g. `DEMO-CARD-1772345678`).

### 2. Security & Privacy Safeguards
- **NO Real Money / Real Gateways**: Strictly simulated for viva presentation.
- **NO Financial Data Stored**: Complete card numbers, CVVs, and expiry dates are NEVER sent to backend servers or stored in MySQL.
- **Database Tracking**: Stores only safe fields: `payment_method`, `payment_status` (`paid` / `pending`), and `transaction_id`.


---

## 🛠️ Technology Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python 3.13 + Flask 3.1 | Application routing, business logic, session handling, RBAC |
| **Database** | MySQL 8.0 | Relational database with foreign key constraints & integrity |
| **DB Connector**| `mysql-connector-python` | Secure parameterized query execution |
| **Frontend** | HTML5, CSS3, JavaScript | Nature-green responsive agricultural UI with live photo previews |
| **CSS Framework**| Bootstrap 5.3 + Bootstrap Icons | Grid layout, responsive navigation, modals, badges, cards |
| **Templating** | Flask Jinja2 | Dynamic server-side page rendering and layout inheritance |
| **Security** | Werkzeug Security | Hashed password generation and secure filename sanitization |

---

## 📁 Project Directory Structure

```text
FarmDirect/
│
├── app.py                     # Main Flask application & all route controllers
├── config.py                  # Database, upload directories & file limits config
├── requirements.txt           # Python dependencies
├── .env                       # Local environment variables (MySQL credentials)
├── .env.example               # Template for environment configuration
├── .gitignore                 # Excluded files from version control
├── README.md                  # Comprehensive documentation & viva guide
│
├── static/                    # Static CSS, JS, Default SVGs & Uploads
│   ├── css/
│   │   └── style.css          # Custom styling, card images, avatars, previews
│   ├── js/
│   │   └── script.js          # Live image preview, client validation & dynamic forms
│   ├── images/
│   │   ├── default_product.svg# Fallback SVG for crops without photos
│   │   ├── default_farmer.svg # Fallback SVG for farmer profile cards
│   │   └── default_avatar.svg # Fallback SVG for user accounts
│   └── uploads/
│       ├── products/          # Uploaded agricultural crop images
│       └── profiles/          # Subdirectories for farmers, customers, delivery, admin
│
├── templates/                 # Jinja2 HTML Templates
│   ├── base.html              # Core layout with avatar dropdowns & universal upload modal
│   ├── index.html             # Homepage with product cards and farmer provenance badges
│   ├── about.html             # Project background, architecture & viva info
│   ├── login.html             # Role-aware login page with sample credentials
│   ├── register.html          # Dynamic registration with optional avatar upload
│   ├── products.html          # Public marketplace catalog with product photos & filters
│   ├── product_details.html   # Crop photo, farmer profile card & customer reviews
│   │
│   ├── farmer/                # Farmer Portal
│   │   ├── dashboard.html     # Avatar header, stat cards, recent crops with thumbnails
│   │   ├── products.html      # Crop catalog with photo thumbnails & approval badges
│   │   ├── add_product.html   # Crop submission form with live photo preview & camera
│   │   ├── edit_product.html  # Crop edit form with image replacement & preview
│   │   └── orders.html        # Orders received for the farmer's crops
│   │
│   ├── customer/              # Customer Portal
│   │   ├── dashboard.html     # Customer summary & avatar profile
│   │   ├── cart.html          # Interactive shopping cart with product thumbnails
│   │   ├── checkout.html      # Address confirmation & demo payment options
│   │   ├── orders.html        # Order history with live delivery statuses
│   │   ├── order_details.html # Itemized invoice with produce photos & tracking
│   │   ├── review.html        # Post-delivery crop rating & review submission
│   │   └── complaint.html     # Issue reporting & complaint resolution tracking
│   │
│   ├── delivery/              # Delivery Partner Portal
│   │   └── dashboard.html     # Assigned shipments & live status updater
│   │
│   ├── admin/                 # Administrator Portal
│   │   ├── dashboard.html     # Overview, Section A (Farmer Verification), Section B (Product Approval)
│   │   ├── farmers.html       # Farmer account verification table with avatars
│   │   ├── products.html      # Product approval table with crop photos & farmer avatars
│   │   ├── orders.html        # Platform-wide order monitoring & delivery dispatch
│   │   └── complaints.html    # Customer complaint resolution table
│   │
│   └── errors/
│       ├── 404.html           # 404 Not Found error page
│       └── 500.html           # 500 Internal Server error page
│
└── utils/
    ├── __init__.py
    ├── db.py                  # Database connection helper & automatic schema upgrades
    ├── decorators.py          # @login_required and @role_required RBAC decorators
    └── images.py              # File validation, secure saving, deletion & URL helpers
```

---

## 🗄️ Database Architecture & Schemas

### 1. `users` Table
```sql
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    role ENUM('admin', 'farmer', 'customer', 'delivery_partner') NOT NULL,
    profile_image VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. `farmers` Table
```sql
CREATE TABLE IF NOT EXISTS farmers (
    farmer_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    farm_name VARCHAR(150) NOT NULL,
    farm_address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    farming_type ENUM('organic', 'conventional', 'mixed') NOT NULL DEFAULT 'conventional',
    verification_status ENUM('pending', 'verified', 'rejected') NOT NULL DEFAULT 'pending',
    verified_at TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

### 3. `products` Table
```sql
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    category_id INT NOT NULL,
    product_name VARCHAR(150) NOT NULL,
    description TEXT,
    unit VARCHAR(20) NOT NULL DEFAULT 'kg',
    price DECIMAL(10, 2) NOT NULL,
    available_quantity DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    harvest_date DATE NOT NULL,
    product_status ENUM('available', 'out_of_stock', 'inactive') NOT NULL DEFAULT 'available',
    approval_status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
    image_filename VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);
```

---

## 🚀 Quick Setup & Execution

### 1. Clone or Open Project Folder
```bash
cd "d:/Santhosh Rathinam/farm"
```

### 2. Install Required Python Packages
```bash
pip install -r requirements.txt
```

### 3. Configure Database Connection
Create or edit `.env` in the project root:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=farmdirect_db
DB_PORT=3306
SECRET_KEY=college_mini_project_secret_key_2026
```

### 4. Start the Application
```bash
python app.py
```
Visit `http://127.0.0.1:5000` in your web browser.

---

## 🔑 Default Demonstration Accounts

| Role | Email | Password | Initial State |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@farmdirect.com` | `admin123` | Active & full permissions |
| **Verified Farmer** | `arun@farm.com` | `farmer123` | `verified` – Can add crops |
| **Pending Farmer** | `karthik@farm.com` | `farmer123` | `pending` – Awaiting admin review |
| **Customer** | `priya@gmail.com` | `customer123` | Active – Can place orders & reviews |
| **Delivery Partner**| `delivery@farmdirect.com` | `delivery123` | Active – Handles shipment updates |

---

## 🎓 College Viva Voce Questions & Answers

**Q1: How does the application handle image storage and avoid database bloat?**  
**A:** Uploaded images are stored directly in the server's local file system under organized subdirectories (`static/uploads/products/`, `static/uploads/profiles/...`). The database stores only relative string paths (`uploads/products/prod_123.jpg`), preventing large binary BLOB storage in MySQL and improving query performance.

**Q2: What happens if an image file is missing or deleted from the server?**  
**A:** Helper functions `get_product_image_url()` and `get_user_avatar_url()` check file existence on the disk using Python's `os.path.exists()`. If missing or `None`, they gracefully fall back to optimized SVG vector illustrations (`default_product.svg`, `default_avatar.svg`).

**Q3: How are invalid files or security attacks like directory traversal prevented?**  
**A:** File extensions are strictly whitelisted (`jpg, jpeg, png, webp`), files are restricted to 5MB, filenames are sanitized with `secure_filename()` from Werkzeug, and a random UUID is prepended to ensure uniqueness and prevent file overwrites.

**Q4: How does the Two-Tier verification model work?**  
**A:** 
- **Tier 1 (Farmer Verification)**: When a farmer signs up, `verification_status` is `'pending'`. The admin must verify them in Admin Hub &rarr; Farmer Verification before they can list products.
- **Tier 2 (Product Approval)**: When a verified farmer adds a product, `approval_status` is `'pending'`. It remains hidden from customers until the admin reviews and approves it in Admin Hub &rarr; Product Approvals.
