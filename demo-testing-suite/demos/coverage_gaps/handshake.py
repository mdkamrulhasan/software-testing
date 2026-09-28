"""A Python analogue of Apple's "goto fail" bug (CVE-2014-1266).

The Week 5 reading notes that the C bug's exact shape (a misleadingly
indented `goto`) cannot happen in Python, but "an early return that
accidentally short-circuits later validation is easy to write in any
language." This is that bug, deliberately shipped.

KNOWN BUG (deliberate, for the "goto fail" case study):
    The second `if` is a botched copy-paste of the first: it lost its
    `not`. Because the first check has already returned for a falsy
    hash_ok, the second condition is always true, so the params and
    signature checks below it can never run and a handshake with a
    forged signature is accepted. See test_handshake.py for how a
    coverage report exposes this while every test passes.

Why not a bare `return True` instead? Code after an unconditional
return is statically dead: CPython drops it at compile time, and
coverage.py does not count it as a statement at all, so the report
would say 100%. The bypass has to be conditional, as the real bug's
`goto fail` was (it jumped out with err still 0), for the tool to see
the lines it skips.
"""


def verify_handshake(hash_ok, params_ok, signature_ok):
    if not hash_ok:
        return False
    if hash_ok:  # KNOWN BUG -- copy-paste of the check above, lost its `not`
        return True
    if not params_ok:
        return False
    if not signature_ok:
        return False
    return True
