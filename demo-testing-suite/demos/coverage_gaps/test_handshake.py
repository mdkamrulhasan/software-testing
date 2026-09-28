"""Every test here passes, yet handshake.py accepts forged signatures.

Run from demo-testing-suite/:

    pytest demos/coverage_gaps/test_handshake.py \
        --cov=handshake --cov-branch --cov-report=term-missing

The Missing column lists 30-34, the params and signature checks after
the botched copy-pasted `if`: no input, however constructed, can reach
them. That is the Week 5 reading's point about "goto fail". Even plain
statement coverage (drop --cov-branch) flags unreachable code
immediately, while the suite stays green.

Try adding the missing negative test, verify_handshake(True, True,
False) is False, and watch it fail. That test is left out on purpose
so the demo starts from a passing suite.
"""

from handshake import verify_handshake


def test_valid_handshake_is_accepted():
    assert verify_handshake(True, True, True) is True


def test_bad_hash_is_rejected():
    assert verify_handshake(False, True, True) is False
