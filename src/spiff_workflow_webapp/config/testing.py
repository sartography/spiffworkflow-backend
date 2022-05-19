"""Testing.py."""
import os

# just for the matrix builds in CI
if os.environ.get("TEST_DATABASE_TYPE") == "sqlite":
    SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite3"
else:
    SQLALCHEMY_DATABASE_URI = (
        "mysql+mysqlconnector://root:@localhost/spiff_workflow_webapp_testing"
    )

TESTING = True
