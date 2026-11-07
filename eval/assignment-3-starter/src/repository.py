"""All of the registration system's SQL, in one place."""


class RegistrationRepository:
    """Reads and writes students, courses, and enrollments.

    It never commits. The caller (RegistrationService) decides where each
    transaction starts and ends, with `with connection:` blocks.
    """

    def __init__(self, connection):
        self.connection = connection

    # -- set-up (used by seeding and by tests) -----------------------------
    def add_student(self, student_id, name):
        self.connection.execute("INSERT INTO students VALUES (?, ?)", (student_id, name))

    def add_course(self, code, title, credits, capacity, prerequisite=None):
        self.connection.execute(
            "INSERT INTO courses (code, title, credits, capacity, prerequisite) "
            "VALUES (?, ?, ?, ?, ?)", (code, title, credits, capacity, prerequisite))

    def add_completed(self, student_id, course_code):
        self.connection.execute("INSERT INTO completed VALUES (?, ?)",
                                (student_id, course_code))

    # -- reads -------------------------------------------------------------
    def get_student(self, student_id):
        row = self.connection.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        return dict(row) if row else None

    def get_course(self, code):
        row = self.connection.execute(
            "SELECT * FROM courses WHERE code = ?", (code,)).fetchone()
        return dict(row) if row else None

    def has_completed(self, student_id, course_code):
        row = self.connection.execute(
            "SELECT 1 FROM completed WHERE student_id = ? AND course_code = ?",
            (student_id, course_code)).fetchone()
        return row is not None

    def current_credits(self, student_id):
        """Total credits of the courses the student is enrolled in."""
        row = self.connection.execute(
            "SELECT COALESCE(SUM(c.credits), 0) FROM enrollments e "
            "JOIN courses c ON c.code = e.course_code WHERE e.student_id = ?",
            (student_id,)).fetchone()
        return row[0]

    def enrolled_courses(self, student_id):
        rows = self.connection.execute(
            "SELECT c.code, c.title, c.credits FROM enrollments e "
            "JOIN courses c ON c.code = e.course_code "
            "WHERE e.student_id = ? ORDER BY c.code", (student_id,))
        return [dict(row) for row in rows]

    # -- writes --------------------------------------------------------------
    def take_seat(self, code):
        """Take one seat. Returns False, and changes nothing, if the course
        is full."""
        cursor = self.connection.execute(
            "UPDATE courses SET seats_taken = seats_taken + 1 "
            "WHERE code = ? AND seats_taken < capacity", (code,))
        return cursor.rowcount == 1

    def release_seat(self, code):
        self.connection.execute(
            "UPDATE courses SET seats_taken = seats_taken - 1 WHERE code = ?", (code,))

    def add_enrollment(self, student_id, course_code):
        """Raises sqlite3.IntegrityError if the student is already enrolled."""
        self.connection.execute("INSERT INTO enrollments VALUES (?, ?)",
                                (student_id, course_code))

    def remove_enrollment(self, student_id, course_code):
        """Remove one student's enrollment in a course. Returns False if
        there was none."""
        cursor = self.connection.execute(
            "DELETE FROM enrollments WHERE course_code = ?", (course_code,))
        return cursor.rowcount >= 1
