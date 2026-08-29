-- Demonstration data only. Password values are bcrypt hashes, never plaintext.
-- Demo password for all seeded users: ChangeMe123! (change these accounts outside local demos).

INSERT INTO roles (id, name, description) VALUES
    (1, 'ADMIN', 'System administrator'),
    (2, 'DOCTOR', 'Healthcare provider'),
    (3, 'PATIENT', 'Registered patient');

INSERT INTO departments (id, name, description) VALUES
    (1, 'General Medicine', 'Primary and preventive care'),
    (2, 'Pediatrics', 'Healthcare for children and adolescents'),
    (3, 'Dermatology', 'Skin, hair, and nail care');

INSERT INTO users (id, role_id, email, password_hash, first_name, last_name, phone) VALUES
    (1, 1, 'admin.demo@example.com', '$2b$12$I5wUFKXuKQXJh474WMwsPu3uc2FFG7c6W4rx5h2iLnNCbPUv7nXkm', 'Alex', 'Morgan', '+10000000001'),
    (2, 2, 'maya.patel@example.com', '$2b$12$I5wUFKXuKQXJh474WMwsPu3uc2FFG7c6W4rx5h2iLnNCbPUv7nXkm', 'Maya', 'Patel', '+10000000002'),
    (3, 2, 'james.chen@example.com', '$2b$12$I5wUFKXuKQXJh474WMwsPu3uc2FFG7c6W4rx5h2iLnNCbPUv7nXkm', 'James', 'Chen', '+10000000003'),
    (4, 2, 'aiden.ross@example.com', '$2b$12$I5wUFKXuKQXJh474WMwsPu3uc2FFG7c6W4rx5h2iLnNCbPUv7nXkm', 'Aiden', 'Ross', '+10000000004'),
    (5, 3, 'olivia.bennett@example.com', '$2b$12$I5wUFKXuKQXJh474WMwsPu3uc2FFG7c6W4rx5h2iLnNCbPUv7nXkm', 'Olivia', 'Bennett', '+10000000005'),
    (6, 3, 'noah.williams@example.com', '$2b$12$I5wUFKXuKQXJh474WMwsPu3uc2FFG7c6W4rx5h2iLnNCbPUv7nXkm', 'Noah', 'Williams', '+10000000006'),
    (7, 3, 'emma.thompson@example.com', '$2b$12$I5wUFKXuKQXJh474WMwsPu3uc2FFG7c6W4rx5h2iLnNCbPUv7nXkm', 'Emma', 'Thompson', '+10000000007'),
    (8, 3, 'liam.anderson@example.com', '$2b$12$I5wUFKXuKQXJh474WMwsPu3uc2FFG7c6W4rx5h2iLnNCbPUv7nXkm', 'Liam', 'Anderson', '+10000000008'),
    (9, 3, 'sophia.martin@example.com', '$2b$12$I5wUFKXuKQXJh474WMwsPu3uc2FFG7c6W4rx5h2iLnNCbPUv7nXkm', 'Sophia', 'Martin', '+10000000009');

INSERT INTO doctors (id, user_id, department_id, specialization, qualification, experience, consultation_fee) VALUES
    (1, 2, 1, 'General Medicine', 'MD, Internal Medicine', 12, 95.00),
    (2, 3, 1, 'Family Medicine', 'MD, Family Medicine', 9, 85.00),
    (3, 4, 2, 'Pediatrics', 'MD, Pediatrics', 15, 110.00);

INSERT INTO patients (id, user_id, date_of_birth, gender, address, emergency_contact, blood_group) VALUES
    (1, 5, '1990-04-12', 'F', 'Demo address 1', 'Demo contact 1', 'O+'),
    (2, 6, '1987-09-21', 'M', 'Demo address 2', 'Demo contact 2', 'A+'),
    (3, 7, '1995-02-08', 'F', 'Demo address 3', 'Demo contact 3', 'B+'),
    (4, 8, '1982-11-30', 'M', 'Demo address 4', 'Demo contact 4', 'AB+'),
    (5, 9, '2001-06-17', 'F', 'Demo address 5', 'Demo contact 5', 'O-');

INSERT INTO doctor_schedules (doctor_id, day_of_week, start_time, end_time, appointment_duration, break_start, break_end) VALUES
    (1, 1, '09:00:00', '17:00:00', 30, '12:00:00', '13:00:00'),
    (1, 3, '09:00:00', '17:00:00', 30, '12:00:00', '13:00:00'),
    (2, 2, '10:00:00', '18:00:00', 30, '13:00:00', '14:00:00'),
    (2, 4, '10:00:00', '18:00:00', 30, '13:00:00', '14:00:00'),
    (3, 1, '08:00:00', '16:00:00', 30, '12:00:00', '13:00:00'),
    (3, 5, '08:00:00', '16:00:00', 30, '12:00:00', '13:00:00');

INSERT INTO appointments (id, patient_id, doctor_id, appointment_date, appointment_time, reason, status, consultation_fee, payment_status) VALUES
    (1, 1, 1, '2026-09-07', '09:00:00', 'Annual physical', 'CONFIRMED', 95.00, 'SUCCESS'),
    (2, 2, 2, '2026-09-08', '10:30:00', 'Follow-up visit', 'PENDING', 85.00, 'PENDING'),
    (3, 3, 3, '2026-09-11', '11:00:00', 'Routine consultation', 'COMPLETED', 110.00, 'SUCCESS');

INSERT INTO medical_records (id, patient_id, doctor_id, appointment_id, diagnosis, symptoms, notes, treatment) VALUES
    (1, 3, 3, 3, 'Seasonal allergies', 'Sneezing and congestion', 'Demo clinical note.', 'Rest, fluids, and prescribed medication.');

INSERT INTO prescriptions (id, patient_id, doctor_id, appointment_id, prescription_date) VALUES
    (1, 3, 3, 3, '2026-09-11');

INSERT INTO prescription_items (prescription_id, medicine, dosage, frequency, duration, instructions) VALUES
    (1, 'Demo Allergy Relief', '10 mg', 'Once daily', '7 days', 'Take with water.');

INSERT INTO bills (id, patient_id, appointment_id, consultation_fee, additional_charges, discount, tax, total_amount, payment_status, invoice_date) VALUES
    (1, 1, 1, 95.00, 0.00, 0.00, 9.50, 104.50, 'SUCCESS', '2026-09-07'),
    (2, 3, 3, 110.00, 15.00, 5.00, 12.00, 132.00, 'SUCCESS', '2026-09-11');

INSERT INTO payments (id, bill_id, patient_id, amount, payment_method, transaction_id, payment_status, payment_date) VALUES
    (1, 1, 1, 104.50, 'CARD', 'DEMO-TXN-0001', 'SUCCESS', '2026-09-07 09:05:00'),
    (2, 2, 3, 132.00, 'CASH', 'DEMO-TXN-0002', 'SUCCESS', '2026-09-11 11:45:00');

INSERT INTO notifications (user_id, notification_type, message, read_status) VALUES
    (5, 'APPOINTMENT_CONFIRMED', 'Your demo appointment has been confirmed.', FALSE),
    (3, 'APPOINTMENT_BOOKED', 'A demo patient appointment is awaiting review.', FALSE),
    (7, 'PRESCRIPTION_CREATED', 'A demo prescription was added to your record.', TRUE),
    (7, 'PAYMENT_SUCCESSFUL', 'Your demo payment was recorded successfully.', TRUE);
