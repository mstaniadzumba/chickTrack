import os

# Database location. Defaults to the local SQLite file, but can be overridden with
# an environment variable so we can point at Postgres later without code changes.
DB_URL = os.environ.get("DB_URL", "chicken_management.db")

# Price per chicken (Rand). Used to work out order totals.
CHICKEN_PRICE = 120

# Secret key used to sign login sessions. MUST be set in production (Render) via the
# FLASK_SECRET_KEY environment variable. The fallback is only for local development.
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")
