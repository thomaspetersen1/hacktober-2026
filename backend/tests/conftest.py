import os

# Tests always use backend/data/props.csv, even if .env has Snowflake set up.
# Set before app.config is imported so the cached settings pick it up.
os.environ["CATALOG_SOURCE"] = "local"
