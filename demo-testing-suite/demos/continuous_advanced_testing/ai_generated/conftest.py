"""The AI-generated suites were asked to use the integration fixtures."""

from tests.integration.conftest import (  # noqa: F401  (fixtures)
    client, connection, db_path, payments, provider, repository, service, stock,
)
