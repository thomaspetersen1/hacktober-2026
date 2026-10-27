import os

# Tests never touch Snowflake, even if .env has it set up: props come from backend/data/props.csv...
# Set before app.config is imported so the cached settings pick it up.
os.environ["CATALOG_SOURCE"] = "local"
# ...and the fixed house instead of calling the LLM
os.environ["IDEAS_SOURCE"] = "fixed"
