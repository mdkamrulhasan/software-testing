"""Project-wide fixtures go here.

Nothing lives here yet, on purpose: every fixture so far (sample_cart,
empty_cart, cart_with_one_item, db_connection, ...) is only needed by one
subpackage's tests, so each is defined in that subpackage's own
conftest.py (tests/pricing/conftest.py, tests/accounts/conftest.py)
instead -- the narrowest visibility that still avoids copy-pasting, per
the "conftest.py Hierarchy" slide.

Promote a fixture up to this file only once two *different* subpackages
both need it. That is the rule of thumb to teach in later weeks, when
this file stops being empty.
"""
