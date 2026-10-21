-- =====================================================================
--  College Registration System - Example Queries (for the demo)
-- =====================================================================

-- Q1. Class list: who is registered for ICT101 this semester?
SELECT s.reg_number, s.first_name, s.last_name, p.programme_code, r.status
FROM registration r
JOIN student   s ON s.student_id   = r.student_id
JOIN programme p ON p.programme_id = s.programme_id
JOIN course    c ON c.course_id    = r.course_id
WHERE c.course_code = 'ICT101' AND r.academic_year = '2026/2027' AND r.semester_no = 1
ORDER BY s.last_name;

-- Q2. Registration slip: a student's courses and total credit load
SELECT c.course_code, c.course_title, c.credit_units, r.status
FROM registration r
JOIN course c ON c.course_id = r.course_id
WHERE r.student_id = 3 AND r.academic_year = '2026/2027' AND r.semester_no = 1
  AND r.status <> 'Dropped';

SELECT r.student_id, SUM(c.credit_units) AS total_credits
FROM registration r
JOIN course c ON c.course_id = r.course_id
WHERE r.academic_year = '2026/2027' AND r.semester_no = 1 AND r.status <> 'Dropped'
GROUP BY r.student_id
ORDER BY r.student_id;

-- Q3. Curriculum: courses in each programme, with the coordinating lecturer
SELECT p.programme_code, c.course_code, c.course_title,
       pc.year_of_study, pc.semester_no, pc.is_core,
       l.title || ' ' || l.last_name AS coordinator   -- MySQL: CONCAT(l.title, ' ', l.last_name)
FROM programme_course pc
JOIN programme p ON p.programme_id = pc.programme_id
JOIN course    c ON c.course_id    = pc.course_id
JOIN lecturer  l ON l.lecturer_id  = c.lecturer_id
ORDER BY p.programme_code, pc.year_of_study, pc.semester_no, c.course_code;

-- Q4. Pending registrations awaiting approval by the Registrar
SELECT r.registration_id, s.reg_number, c.course_code, r.registration_date
FROM registration r
JOIN student s ON s.student_id = r.student_id
JOIN course  c ON c.course_id  = r.course_id
WHERE r.status = 'Pending';

-- Q5. Business-rule check: registrations for courses outside the student's programme
--     (should return no rows)
SELECT r.registration_id, s.reg_number, c.course_code
FROM registration r
JOIN student s ON s.student_id = r.student_id
JOIN course  c ON c.course_id  = r.course_id
LEFT JOIN programme_course pc
       ON pc.programme_id = s.programme_id AND pc.course_id = r.course_id
WHERE pc.course_id IS NULL;
