# College Registration System – Requirements

## 1. Purpose and scope
The system records the college's departments, programmes, courses and lecturers. It lets
admitted students register for the courses in their programme each semester. The Registrar
approves registrations, and lecturers later record final grades.

**In scope:** student records, programme curricula, course allocation to lecturers,
semester course registration (add / drop / approve), recording results.
**Out of scope:** fees and payments, timetabling, hostel allocation, admissions applications.

## 2. Users (actors)
| User | Main needs |
|---|---|
| **Student** | View the courses in their programme, register for and drop courses, print a registration slip, view grades. |
| **Registrar / Academic Registry staff** | Enrol new students, maintain programmes and curricula, open the registration period, approve or reject registrations, produce reports. |
| **Lecturer** | View class lists for the courses they coordinate, enter final grades. |
| **Head of Department (HoD)** | Assign courses to lecturers, view department programmes and registration statistics. |
| **System Administrator** | Manage user accounts, backups and security. |

## 3. Business processes
1. **Set up academic structure**: the Registrar creates departments and programmes, and adds courses to each programme's curriculum (year and semester, core or elective).
2. **Allocate courses**: the HoD assigns a coordinating lecturer to each course.
3. **Enrol student**: the Registrar records an admitted student in one programme and issues a unique registration number.
4. **Register for courses**: each semester the student selects courses from their programme's curriculum, and a registration is created with status *Pending*.
5. **Approve registration**: the Registrar checks eligibility and credit load, then sets the status to *Approved* (or the student *Drops* the course during add/drop).
6. **Record results**: at semester end the lecturer enters a final grade, and the registration becomes *Completed*.
7. **Reporting**: class lists, registration slips, curriculum per programme, pending approvals.

## 4. Entities and attributes
| Entity | Attributes (PK **bold**, FK *italic*) |
|---|---|
| DEPARTMENT | **department_id**, department_code, department_name, office_location, phone |
| PROGRAMME | **programme_id**, programme_code, programme_name, award_level, duration_years, *department_id* |
| LECTURER | **lecturer_id**, staff_number, title, first_name, last_name, email, phone, *department_id* |
| COURSE | **course_id**, course_code, course_title, credit_units, *lecturer_id* |
| STUDENT | **student_id**, reg_number, first_name, last_name, gender, date_of_birth, email, phone, admission_date, status, *programme_id* |
| PROGRAMME_COURSE (associative) | ***programme_id*, *course_id*** (composite PK), year_of_study, semester_no, is_core |
| REGISTRATION (associative) | **registration_id**, *student_id*, *course_id*, academic_year, semester_no, registration_date, status, final_grade |

## 5. Business rules
| # | Rule | How it is enforced |
|---|---|---|
| BR1 | A department offers zero or more programmes; each programme belongs to exactly one department. | `programme.department_id` NOT NULL FK |
| BR2 | A department employs zero or more lecturers; each lecturer belongs to exactly one department. | `lecturer.department_id` NOT NULL FK |
| BR3 | A student is enrolled in exactly one programme; a programme has zero or more students. | `student.programme_id` NOT NULL FK |
| BR4 | A programme includes one or more courses, and a course may be part of many programmes (M:N). | Associative table `programme_course` with composite PK |
| BR5 | Each course is coordinated by exactly one lecturer; a lecturer may coordinate zero or more courses. | `course.lecturer_id` NOT NULL FK |
| BR6 | A student may register for many courses per semester, but for the same course **only once** in a given semester. | UNIQUE (student_id, course_id, academic_year, semester_no) |
| BR7 | A student may only register for courses that are in their own programme's curriculum. | Application check / audit query Q5 in `sql/03_queries.sql` |
| BR8 | Only *Active* students may register, and the total credit load per semester must not exceed 24 credit units. | Application check before insert (query Q2 computes the load) |
| BR9 | Registration status is one of Pending, Approved, Dropped, Completed; a grade can only be recorded when the status is Completed. | CHECK constraints `ck_reg_status`, `ck_reg_grade_when` |
| BR10 | Registration numbers, staff numbers, course codes, programme codes and e-mail addresses are unique. | UNIQUE constraints |
| BR11 | Records that other records depend on cannot be deleted (for example a department that still has programmes). | FKs use ON DELETE RESTRICT |

## 6. Design checks
- **Every table has a primary key**: surrogate INT keys, except `programme_course`, which uses the natural composite key (programme_id, course_id).
- **Relationships are represented consistently**: every 1:N relationship is a NOT NULL foreign key on the "many" side, and every M:N relationship is resolved by an associative table. The diagrams use the same crow's-foot notation throughout.
- **Normalisation (3NF)**: no repeating groups (1NF), no partial dependencies on the composite key (2NF), and no transitive dependencies. For example, a student's department is derived through the programme rather than stored again (3NF).
- **Data types**: VARCHAR for variable-length text, CHAR for fixed-length codes (`gender`, `academic_year` such as '2026/2027'), DATE for dates, SMALLINT for small counts, BOOLEAN for flags, INT for keys.
