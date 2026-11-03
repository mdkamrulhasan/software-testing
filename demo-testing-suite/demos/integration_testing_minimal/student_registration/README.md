# Student Registration Integration Test

A small Python + pytest example showing an integration test across:

- `RegistrationService` — business logic
- `StudentRepository` — data-access layer
- SQLite — database used by the repository

The test uses a real in-memory SQLite database and the real application classes. It does not use mocks or stubs.

## Project files

- `registration.py` — application components
- `test_registration.py` — pytest integration test
- `pytest.ini` — registers the `integration` marker
- `integration_test_diagram.png` — architecture and test-flow diagram

## Run the example

Install pytest:

```bash
python -m pip install pytest
```

Run only integration tests:

```bash
python -m pytest -v -m integration
```

Run all tests:

```bash
python -m pytest -v
```

Expected result: `1 passed`.
