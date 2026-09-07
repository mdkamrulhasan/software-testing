"""tmp_path demo: tests that touch the filesystem should use pytest's
built-in tmp_path fixture, never a real project directory.

"tmp_path: A Safe Temporary Directory" slide.
"""

from app.reports.report_writer import save_report


def test_save_report(tmp_path):
    # tmp_path is injected by pytest itself -- no @pytest.fixture needed
    # anywhere in this project for it to work.
    result_path = save_report(tmp_path, "report.txt", "Sales: $1,200")

    assert result_path.exists()
    assert result_path.read_text() == "Sales: $1,200"
