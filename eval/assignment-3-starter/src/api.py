"""The registration system's HTTP API (SPEC.md), built with Flask."""

import re

from flask import Flask, jsonify, request

from errors import (AlreadyEnrolled, CourseFull, NotEligible, NotEnrolled,
                    UnknownCourse, UnknownStudent)

ID_PATTERN = re.compile(r"[A-Za-z0-9]{1,20}")


def create_app(service, api_key):
    app = Flask(__name__)

    def error(status, message):
        return jsonify(error=message), status

    @app.before_request
    def require_api_key():
        if request.path == "/health":
            return None  # probes carry no credentials
        if request.headers.get("X-API-Key") != api_key:
            return error(401, "missing or invalid API key")

    @app.get("/health")
    def health():
        try:
            service.health()
        except Exception:
            return jsonify(status="unavailable"), 503
        return jsonify(status="ok")

    @app.post("/enrollments")
    def enroll():
        body = request.get_json(silent=True)
        problem = validate_enrollment(body)
        if problem:
            return error(400, problem)
        try:
            enrollment = service.enroll(body["student_id"], body["course_code"])
        except UnknownStudent:
            return error(404, f"unknown student: {body['student_id']}")
        except UnknownCourse:
            return error(404, f"unknown course: {body['course_code']}")
        except CourseFull:
            return error(409, "course is full")
        except AlreadyEnrolled:
            return error(409, "already enrolled")
        except NotEligible as exc:
            return error(422, str(exc))
        return jsonify(enrollment), 201

    @app.delete("/enrollments/<student_id>/<course_code>")
    def withdraw(student_id, course_code):
        try:
            service.withdraw(student_id, course_code)
        except NotEnrolled:
            return error(404, "not enrolled")
        return "", 204

    @app.get("/students/<student_id>/schedule")
    def schedule(student_id):
        try:
            return jsonify(service.schedule(student_id))
        except UnknownStudent:
            return error(404, f"unknown student: {student_id}")

    @app.get("/courses/<code>")
    def course(code):
        try:
            return jsonify(service.course(code))
        except UnknownCourse:
            return error(404, f"unknown course: {code}")

    @app.errorhandler(404)
    @app.errorhandler(405)
    def json_errors(exc):  # Flask's defaults are HTML pages
        return error(exc.code, exc.name.lower())

    @app.errorhandler(500)
    def internal_error(exc):  # never an HTML page or a stack trace
        return error(500, "internal error")

    return app


def validate_enrollment(body):
    """Return a message describing what is wrong with `body`, or None."""
    if not isinstance(body, dict):
        return "request body must be a JSON object"
    missing = [f for f in ("student_id", "course_code") if f not in body]
    if missing:
        return f"missing field(s): {', '.join(missing)}"
    for field in ("student_id", "course_code"):
        value = body[field]
        if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
            return f"{field} must be 1-20 letters or digits"
    return None
