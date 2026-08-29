-- Healthcare Management & Appointment System
-- MySQL 8.0+ schema. Run this file against the selected database.

CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(30) UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX ix_users_role_id (role_id),
    INDEX ix_users_name (last_name, first_name),
    CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    date_of_birth DATE,
    gender VARCHAR(30),
    address VARCHAR(500),
    emergency_contact VARCHAR(255),
    blood_group VARCHAR(5),
    status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX ix_patients_status (status),
    CONSTRAINT fk_patients_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    description VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

CREATE TABLE doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    department_id INT NOT NULL,
    specialization VARCHAR(120) NOT NULL,
    qualification VARCHAR(255),
    experience INT,
    consultation_fee DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    availability_status VARCHAR(30) NOT NULL DEFAULT 'AVAILABLE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX ix_doctors_department_id (department_id),
    INDEX ix_doctors_specialization (specialization),
    INDEX ix_doctors_availability_status (availability_status),
    CONSTRAINT fk_doctors_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT fk_doctors_department FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE doctor_schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT NOT NULL,
    day_of_week TINYINT NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    appointment_duration INT NOT NULL DEFAULT 30,
    break_start TIME,
    break_end TIME,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    INDEX ix_doctor_schedules_doctor_day (doctor_id, day_of_week),
    INDEX ix_doctor_schedules_doctor_id (doctor_id),
    CONSTRAINT fk_doctor_schedules_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    reason VARCHAR(500),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    consultation_fee DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_doctor_appointment_slot (doctor_id, appointment_date, appointment_time),
    INDEX ix_appointments_patient_id (patient_id),
    INDEX ix_appointments_doctor_id (doctor_id),
    INDEX ix_appointments_appointment_date (appointment_date),
    INDEX ix_appointments_status (status),
    INDEX ix_appointments_payment_status (payment_status),
    CONSTRAINT fk_appointments_patient FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE RESTRICT,
    CONSTRAINT fk_appointments_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE medical_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_id INT NOT NULL UNIQUE,
    diagnosis TEXT,
    symptoms TEXT,
    notes TEXT,
    treatment TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX ix_medical_records_patient_id (patient_id),
    INDEX ix_medical_records_doctor_id (doctor_id),
    CONSTRAINT fk_medical_records_patient FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE RESTRICT,
    CONSTRAINT fk_medical_records_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE RESTRICT,
    CONSTRAINT fk_medical_records_appointment FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE prescriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_id INT NOT NULL UNIQUE,
    prescription_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_prescriptions_patient_id (patient_id),
    INDEX ix_prescriptions_doctor_id (doctor_id),
    CONSTRAINT fk_prescriptions_patient FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE RESTRICT,
    CONSTRAINT fk_prescriptions_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE RESTRICT,
    CONSTRAINT fk_prescriptions_appointment FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE prescription_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prescription_id INT NOT NULL,
    medicine VARCHAR(150) NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    duration VARCHAR(100) NOT NULL,
    instructions VARCHAR(500),
    INDEX ix_prescription_items_prescription_id (prescription_id),
    CONSTRAINT fk_prescription_items_prescription FOREIGN KEY (prescription_id) REFERENCES prescriptions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE bills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    appointment_id INT NOT NULL UNIQUE,
    consultation_fee DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    additional_charges DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    discount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    tax DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    invoice_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_bills_patient_id (patient_id),
    INDEX ix_bills_payment_status (payment_status),
    CONSTRAINT fk_bills_patient FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE RESTRICT,
    CONSTRAINT fk_bills_appointment FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bill_id INT NOT NULL,
    patient_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    transaction_id VARCHAR(100) UNIQUE,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    payment_date DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_payments_bill_id (bill_id),
    INDEX ix_payments_patient_id (patient_id),
    INDEX ix_payments_payment_status (payment_status),
    CONSTRAINT fk_payments_bill FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE RESTRICT,
    CONSTRAINT fk_payments_patient FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    message VARCHAR(500) NOT NULL,
    read_status BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_notifications_user_id (user_id),
    INDEX ix_notifications_user_read (user_id, read_status),
    CONSTRAINT fk_notifications_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;
