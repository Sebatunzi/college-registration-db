-- =====================================================================
--  College Registration System - Relational Schema
--  Portable SQL: runs on MySQL 8.0.16+ and PostgreSQL 12+.
--  Tables are created parent-first so every FOREIGN KEY resolves.
-- =====================================================================

DROP TABLE IF EXISTS registration;
DROP TABLE IF EXISTS programme_course;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS course;
DROP TABLE IF EXISTS lecturer;
DROP TABLE IF EXISTS programme;
DROP TABLE IF EXISTS department;

-- ---------------------------------------------------------------------
-- DEPARTMENT: academic unit that offers programmes and employs lecturers
-- ---------------------------------------------------------------------
CREATE TABLE department (
    department_id    INT           NOT NULL,
    department_code  VARCHAR(10)   NOT NULL,
    department_name  VARCHAR(100)  NOT NULL,
    office_location  VARCHAR(100)  NULL,
    phone            VARCHAR(20)   NULL,
    CONSTRAINT pk_department      PRIMARY KEY (department_id),
    CONSTRAINT uq_department_code UNIQUE (department_code),
    CONSTRAINT uq_department_name UNIQUE (department_name)
);

-- ---------------------------------------------------------------------
-- PROGRAMME: award a student studies for (Certificate, Diploma, Degree)
-- ---------------------------------------------------------------------
CREATE TABLE programme (
    programme_id     INT           NOT NULL,
    programme_code   VARCHAR(10)   NOT NULL,
    programme_name   VARCHAR(120)  NOT NULL,
    award_level      VARCHAR(20)   NOT NULL,
    duration_years   SMALLINT      NOT NULL,
    department_id    INT           NOT NULL,
    CONSTRAINT pk_programme       PRIMARY KEY (programme_id),
    CONSTRAINT uq_programme_code  UNIQUE (programme_code),
    CONSTRAINT ck_programme_award CHECK (award_level IN ('Certificate', 'Diploma', 'Degree')),
    CONSTRAINT ck_programme_years CHECK (duration_years BETWEEN 1 AND 5),
    CONSTRAINT fk_programme_department FOREIGN KEY (department_id)
        REFERENCES department (department_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ---------------------------------------------------------------------
-- LECTURER: member of teaching staff, belongs to one department
-- ---------------------------------------------------------------------
CREATE TABLE lecturer (
    lecturer_id      INT           NOT NULL,
    staff_number     VARCHAR(20)   NOT NULL,
    title            VARCHAR(10)   NULL,
    first_name       VARCHAR(50)   NOT NULL,
    last_name        VARCHAR(50)   NOT NULL,
    email            VARCHAR(100)  NOT NULL,
    phone            VARCHAR(20)   NULL,
    department_id    INT           NOT NULL,
    CONSTRAINT pk_lecturer        PRIMARY KEY (lecturer_id),
    CONSTRAINT uq_lecturer_staff  UNIQUE (staff_number),
    CONSTRAINT uq_lecturer_email  UNIQUE (email),
    CONSTRAINT fk_lecturer_department FOREIGN KEY (department_id)
        REFERENCES department (department_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ---------------------------------------------------------------------
-- COURSE: unit of study (module) coordinated by exactly one lecturer
-- ---------------------------------------------------------------------
CREATE TABLE course (
    course_id        INT           NOT NULL,
    course_code      VARCHAR(10)   NOT NULL,
    course_title     VARCHAR(120)  NOT NULL,
    credit_units     SMALLINT      NOT NULL,
    lecturer_id      INT           NOT NULL,
    CONSTRAINT pk_course          PRIMARY KEY (course_id),
    CONSTRAINT uq_course_code     UNIQUE (course_code),
    CONSTRAINT ck_course_credits  CHECK (credit_units BETWEEN 1 AND 6),
    CONSTRAINT fk_course_lecturer FOREIGN KEY (lecturer_id)
        REFERENCES lecturer (lecturer_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ---------------------------------------------------------------------
-- STUDENT: person admitted to exactly one programme
-- ---------------------------------------------------------------------
CREATE TABLE student (
    student_id       INT           NOT NULL,
    reg_number       VARCHAR(20)   NOT NULL,
    first_name       VARCHAR(50)   NOT NULL,
    last_name        VARCHAR(50)   NOT NULL,
    gender           CHAR(1)       NOT NULL,
    date_of_birth    DATE          NOT NULL,
    email            VARCHAR(100)  NOT NULL,
    phone            VARCHAR(20)   NULL,
    admission_date   DATE          NOT NULL,
    status           VARCHAR(15)   NOT NULL DEFAULT 'Active',
    programme_id     INT           NOT NULL,
    CONSTRAINT pk_student         PRIMARY KEY (student_id),
    CONSTRAINT uq_student_regno   UNIQUE (reg_number),
    CONSTRAINT uq_student_email   UNIQUE (email),
    CONSTRAINT ck_student_gender  CHECK (gender IN ('M', 'F')),
    CONSTRAINT ck_student_status  CHECK (status IN ('Active', 'Suspended', 'Graduated', 'Withdrawn')),
    CONSTRAINT ck_student_dates   CHECK (admission_date > date_of_birth),
    CONSTRAINT fk_student_programme FOREIGN KEY (programme_id)
        REFERENCES programme (programme_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ---------------------------------------------------------------------
-- PROGRAMME_COURSE: resolves the M:N "programme includes course"
-- (curriculum: which courses belong to which programme, and when)
-- ---------------------------------------------------------------------
CREATE TABLE programme_course (
    programme_id     INT           NOT NULL,
    course_id        INT           NOT NULL,
    year_of_study    SMALLINT      NOT NULL,
    semester_no      SMALLINT      NOT NULL,
    is_core          BOOLEAN       NOT NULL DEFAULT TRUE,
    CONSTRAINT pk_programme_course PRIMARY KEY (programme_id, course_id),
    CONSTRAINT ck_pc_year     CHECK (year_of_study BETWEEN 1 AND 5),
    CONSTRAINT ck_pc_semester CHECK (semester_no IN (1, 2)),
    CONSTRAINT fk_pc_programme FOREIGN KEY (programme_id)
        REFERENCES programme (programme_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_pc_course    FOREIGN KEY (course_id)
        REFERENCES course (course_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ---------------------------------------------------------------------
-- REGISTRATION: a student registering for a course in a given semester
-- (resolves the M:N "student takes course" and records the result)
-- ---------------------------------------------------------------------
CREATE TABLE registration (
    registration_id   INT          NOT NULL,
    student_id        INT          NOT NULL,
    course_id         INT          NOT NULL,
    academic_year     CHAR(9)      NOT NULL,          -- e.g. '2026/2027'
    semester_no       SMALLINT     NOT NULL,
    registration_date DATE         NOT NULL,
    status            VARCHAR(15)  NOT NULL DEFAULT 'Pending',
    final_grade       VARCHAR(2)   NULL,
    CONSTRAINT pk_registration    PRIMARY KEY (registration_id),
    CONSTRAINT uq_registration_once UNIQUE (student_id, course_id, academic_year, semester_no),
    CONSTRAINT ck_reg_semester    CHECK (semester_no IN (1, 2)),
    CONSTRAINT ck_reg_status      CHECK (status IN ('Pending', 'Approved', 'Dropped', 'Completed')),
    CONSTRAINT ck_reg_grade       CHECK (final_grade IS NULL
                                         OR final_grade IN ('A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'E', 'F')),
    CONSTRAINT ck_reg_grade_when  CHECK (final_grade IS NULL OR status = 'Completed'),
    CONSTRAINT fk_registration_student FOREIGN KEY (student_id)
        REFERENCES student (student_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_registration_course  FOREIGN KEY (course_id)
        REFERENCES course (course_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Indexes on foreign keys used in joins and look-ups
CREATE INDEX ix_programme_department ON programme (department_id);
CREATE INDEX ix_lecturer_department  ON lecturer (department_id);
CREATE INDEX ix_course_lecturer      ON course (lecturer_id);
CREATE INDEX ix_student_programme    ON student (programme_id);
CREATE INDEX ix_pc_course            ON programme_course (course_id);
CREATE INDEX ix_registration_course  ON registration (course_id);
