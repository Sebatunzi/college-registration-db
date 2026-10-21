-- =====================================================================
--  College Registration System - Sample Data (for demonstration)
--  Run after 01_schema.sql. Insert order follows the foreign keys.
-- =====================================================================

INSERT INTO department (department_id, department_code, department_name, office_location, phone) VALUES
(1, 'ICT', 'Information & Communication Technology', 'Block A, Room 12', '+256700100100'),
(2, 'BUS', 'Business Studies',                       'Block B, Room 03', '+256700100200');

INSERT INTO programme (programme_id, programme_code, programme_name, award_level, duration_years, department_id) VALUES
(1, 'DIT',  'Diploma in Information Technology', 'Diploma',     2, 1),
(2, 'DCS',  'Diploma in Computer Science',       'Diploma',     2, 1),
(3, 'CBA',  'Certificate in Business Admin',     'Certificate', 1, 2);

INSERT INTO lecturer (lecturer_id, staff_number, title, first_name, last_name, email, phone, department_id) VALUES
(1, 'STF-001', 'Mr.',  'Peter',  'Okello',   'p.okello@college.ac.ug',   '+256771000001', 1),
(2, 'STF-002', 'Ms.',  'Grace',  'Namubiru', 'g.namubiru@college.ac.ug', '+256771000002', 1),
(3, 'STF-003', 'Dr.',  'Samuel', 'Mugisha',  's.mugisha@college.ac.ug',  NULL,            2);

INSERT INTO course (course_id, course_code, course_title, credit_units, lecturer_id) VALUES
(1, 'ICT101', 'Introduction to Computing',      3, 1),
(2, 'ICT102', 'Database Design & Management',   4, 2),
(3, 'ICT103', 'Programming Fundamentals',       4, 1),
(4, 'BUS101', 'Principles of Management',       3, 3),
(5, 'GEN101', 'Communication Skills',           2, 3);

-- Curriculum: GEN101 is shared by all programmes (shows the M:N relationship)
INSERT INTO programme_course (programme_id, course_id, year_of_study, semester_no, is_core) VALUES
(1, 1, 1, 1, TRUE), (1, 2, 1, 2, TRUE), (1, 5, 1, 1, TRUE),
(2, 1, 1, 1, TRUE), (2, 3, 1, 1, TRUE), (2, 2, 1, 2, FALSE), (2, 5, 1, 1, TRUE),
(3, 4, 1, 1, TRUE), (3, 5, 1, 1, TRUE);

INSERT INTO student (student_id, reg_number, first_name, last_name, gender, date_of_birth, email, phone, admission_date, status, programme_id) VALUES
(1, '2026/DIT/001', 'Aisha',   'Nakato',   'F', '2005-03-14', 'aisha.nakato@students.college.ac.ug',   '+256752000001', '2026-08-18', 'Active', 1),
(2, '2026/DIT/002', 'Brian',   'Ssempala', 'M', '2004-11-02', 'brian.ssempala@students.college.ac.ug', NULL,            '2026-08-18', 'Active', 1),
(3, '2026/DCS/001', 'Claire',  'Atim',     'F', '2005-07-21', 'claire.atim@students.college.ac.ug',    '+256752000003', '2026-08-18', 'Active', 2),
(4, '2026/CBA/001', 'Daniel',  'Kato',     'M', '2006-01-09', 'daniel.kato@students.college.ac.ug',    '+256752000004', '2026-08-19', 'Active', 3);

INSERT INTO registration (registration_id, student_id, course_id, academic_year, semester_no, registration_date, status, final_grade) VALUES
(1, 1, 1, '2026/2027', 1, '2026-08-25', 'Approved', NULL),
(2, 1, 5, '2026/2027', 1, '2026-08-25', 'Approved', NULL),
(3, 2, 1, '2026/2027', 1, '2026-08-26', 'Approved', NULL),
(4, 2, 5, '2026/2027', 1, '2026-08-26', 'Pending',  NULL),
(5, 3, 1, '2026/2027', 1, '2026-08-25', 'Approved', NULL),
(6, 3, 3, '2026/2027', 1, '2026-08-25', 'Approved', NULL),
(7, 3, 5, '2026/2027', 1, '2026-08-25', 'Dropped',  NULL),
(8, 4, 4, '2026/2027', 1, '2026-08-27', 'Approved', NULL),
(9, 4, 5, '2026/2027', 1, '2026-08-27', 'Approved', NULL);
