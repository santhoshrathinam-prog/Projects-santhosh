-- ====================================================================
-- Real Estate House Building Inventory Management System
-- Database Schema DDL for MySQL 8.0+
-- Database: real_estate_inventory
-- ====================================================================

CREATE DATABASE IF NOT EXISTS real_estate_inventory
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE real_estate_inventory;

-- 1. Admins Table
CREATE TABLE IF NOT EXISTS admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Builders / Site Engineers Table
CREATE TABLE IF NOT EXISTS builders (
    builder_id INT AUTO_INCREMENT PRIMARY KEY,
    builder_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status ENUM('Active', 'Inactive') NOT NULL DEFAULT 'Active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Houses Under Construction Table
CREATE TABLE IF NOT EXISTS houses (
    house_id INT AUTO_INCREMENT PRIMARY KEY,
    house_number VARCHAR(50) NOT NULL UNIQUE,
    house_type VARCHAR(50) NOT NULL,
    bhk VARCHAR(20) NOT NULL,
    area_sqft DECIMAL(10, 2) NOT NULL,
    location VARCHAR(150) NOT NULL,
    construction_stage ENUM('Foundation', 'Structure', 'Brickwork', 'Plumbing', 'Electrical', 'Flooring', 'Painting', 'Finishing', 'Completed') NOT NULL DEFAULT 'Foundation',
    progress_pct DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    status ENUM('Planned', 'Under Construction', 'On Hold', 'Completed') NOT NULL DEFAULT 'Planned',
    start_date DATE NULL,
    expected_completion_date DATE NULL,
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Builder-House Assignments Table
CREATE TABLE IF NOT EXISTS builder_house_assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    builder_id INT NOT NULL,
    house_id INT NOT NULL,
    assigned_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Active', 'Reassigned', 'Completed') NOT NULL DEFAULT 'Active',
    notes VARCHAR(255) NULL,
    INDEX idx_bha_builder (builder_id),
    INDEX idx_bha_house (house_id),
    CONSTRAINT fk_bha_builder FOREIGN KEY (builder_id) REFERENCES builders(builder_id) ON DELETE CASCADE,
    CONSTRAINT fk_bha_house FOREIGN KEY (house_id) REFERENCES houses(house_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Suppliers Table
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NULL,
    address TEXT NULL,
    materials_supplied TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Construction Materials Master Table
CREATE TABLE IF NOT EXISTS materials (
    material_id INT AUTO_INCREMENT PRIMARY KEY,
    material_name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    available_quantity DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    minimum_stock_level DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    unit_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    supplier_id INT NULL,
    storage_location VARCHAR(100) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_mat_category (category),
    INDEX idx_mat_supplier (supplier_id),
    CONSTRAINT fk_mat_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. House-Wise Material Requirements Table
CREATE TABLE IF NOT EXISTS material_requirements (
    requirement_id INT AUTO_INCREMENT PRIMARY KEY,
    house_id INT NOT NULL,
    material_id INT NOT NULL,
    required_quantity DECIMAL(12, 2) NOT NULL,
    notes VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_house_material (house_id, material_id),
    INDEX idx_mr_house (house_id),
    INDEX idx_mr_material (material_id),
    CONSTRAINT fk_mr_house FOREIGN KEY (house_id) REFERENCES houses(house_id) ON DELETE CASCADE,
    CONSTRAINT fk_mr_material FOREIGN KEY (material_id) REFERENCES materials(material_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Inventory Transactions History Table (IN / OUT)
CREATE TABLE IF NOT EXISTS inventory_transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_type ENUM('IN', 'OUT') NOT NULL,
    material_id INT NOT NULL,
    house_id INT NULL,
    builder_id INT NULL,
    supplier_id INT NULL,
    quantity DECIMAL(12, 2) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_cost DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    transaction_date DATE NOT NULL,
    invoice_number VARCHAR(100) NULL,
    purpose VARCHAR(255) NULL,
    notes TEXT NULL,
    status ENUM('COMPLETED', 'CANCELLED') NOT NULL DEFAULT 'COMPLETED',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_it_mat (material_id),
    INDEX idx_it_house (house_id),
    INDEX idx_it_date (transaction_date),
    CONSTRAINT fk_it_mat FOREIGN KEY (material_id) REFERENCES materials(material_id) ON DELETE RESTRICT,
    CONSTRAINT fk_it_house FOREIGN KEY (house_id) REFERENCES houses(house_id) ON DELETE SET NULL,
    CONSTRAINT fk_it_builder FOREIGN KEY (builder_id) REFERENCES builders(builder_id) ON DELETE SET NULL,
    CONSTRAINT fk_it_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. Builder Construction Stage & Progress Updates Table
CREATE TABLE IF NOT EXISTS construction_updates (
    update_id INT AUTO_INCREMENT PRIMARY KEY,
    house_id INT NOT NULL,
    builder_id INT NOT NULL,
    stage VARCHAR(50) NOT NULL,
    progress_pct DECIMAL(5, 2) NOT NULL,
    work_completed TEXT NULL,
    work_pending TEXT NULL,
    remarks TEXT NULL,
    update_date DATE NOT NULL,
    status ENUM('PENDING', 'APPROVED', 'REJECTED') NOT NULL DEFAULT 'PENDING',
    reviewed_by INT NULL,
    review_date DATETIME NULL,
    review_notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cu_house (house_id),
    INDEX idx_cu_builder (builder_id),
    INDEX idx_cu_status (status),
    CONSTRAINT fk_cu_house FOREIGN KEY (house_id) REFERENCES houses(house_id) ON DELETE CASCADE,
    CONSTRAINT fk_cu_builder FOREIGN KEY (builder_id) REFERENCES builders(builder_id) ON DELETE CASCADE,
    CONSTRAINT fk_cu_admin FOREIGN KEY (reviewed_by) REFERENCES admins(admin_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. Builder Material Stock & Usage Updates Table
CREATE TABLE IF NOT EXISTS stock_updates (
    stock_update_id INT AUTO_INCREMENT PRIMARY KEY,
    house_id INT NOT NULL,
    builder_id INT NOT NULL,
    material_id INT NOT NULL,
    opening_stock DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    material_received DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    material_used DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    remaining_stock DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    update_date DATE NOT NULL,
    remarks TEXT NULL,
    status ENUM('PENDING', 'APPROVED', 'REJECTED') NOT NULL DEFAULT 'PENDING',
    reviewed_by INT NULL,
    review_date DATETIME NULL,
    review_notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_su_house (house_id),
    INDEX idx_su_builder (builder_id),
    INDEX idx_su_mat (material_id),
    INDEX idx_su_status (status),
    CONSTRAINT fk_su_house FOREIGN KEY (house_id) REFERENCES houses(house_id) ON DELETE CASCADE,
    CONSTRAINT fk_su_builder FOREIGN KEY (builder_id) REFERENCES builders(builder_id) ON DELETE CASCADE,
    CONSTRAINT fk_su_mat FOREIGN KEY (material_id) REFERENCES materials(material_id) ON DELETE CASCADE,
    CONSTRAINT fk_su_admin FOREIGN KEY (reviewed_by) REFERENCES admins(admin_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
