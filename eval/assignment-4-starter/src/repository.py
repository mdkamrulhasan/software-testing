"""All of the registration system's SQL, in one place."""


class RegistrationRepository:
    """Reads and writes students, courses, enrollments, and waitlists.

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

    def is_enrolled(self, student_id, course_code):
        row = self.connection.execute(
            "SELECT 1 FROM enrollments WHERE student_id = ? AND course_code = ?",
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
            "DELETE FROM enrollments WHERE student_id = ? AND course_code = ?",
            (student_id, course_code))
        return cursor.rowcount == 1

    # -- waitlist (REQ-9 to REQ-11) -------------------------------------------
    def add_to_waitlist(self, student_id, course_code):
        """Put the student at the end of the course's waitlist and return
        their position. Raises sqlite3.IntegrityError if already on it."""
        row = self.connection.execute(
            "SELECT COALESCE(MAX(position), 0) + 1 FROM waitlist WHERE course_code = ?",
            (course_code,)).fetchone()
        position = row[0]
        self.connection.execute("INSERT INTO waitlist VALUES (?, ?, ?)",
                                (student_id, course_code, position))
        return position

    def waitlist_position(self, student_id, course_code):
        """The student's position on the course's waitlist, or None."""
        row = self.connection.execute(
            "SELECT position FROM waitlist WHERE student_id = ? AND course_code = ?",
            (student_id, course_code)).fetchone()
        return row[0] if row else None

    def first_on_waitlist(self, course_code):
        """The id of the student who joined the course's waitlist first, or None."""
        row = self.connection.execute(
            "SELECT student_id FROM waitlist WHERE course_code = ? "
            "ORDER BY position LIMIT 1", (course_code,)).fetchone()
        return row[0] if row else None

    def remove_from_waitlist(self, student_id, course_code):
        """Returns False if the student was not on the waitlist."""
        cursor = self.connection.execute(
            "DELETE FROM waitlist WHERE student_id = ? AND course_code = ?",
            (student_id, course_code))
        return cursor.rowcount == 1

    def waitlisted_courses(self, student_id):
        """The courses the student is waiting for: code, title, position."""
        rows = self.connection.execute(
            "SELECT c.code, c.title FROM waitlist w "
            "JOIN courses c ON c.code = w.course_code "
            "WHERE w.student_id = ? ORDER BY c.code", (student_id,))
        return [dict(row, position=self.waitlist_position(student_id, row["code"]))
                for row in rows]
