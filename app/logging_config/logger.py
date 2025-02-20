import json
import os
from loguru import logger

# Load config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

# Ensure log directory exists
os.makedirs(config["log_dir"], exist_ok=True)
log_path = os.path.join(config["log_dir"], config["log_file"])

# Configure logger
logger.remove() # Remove default logger
logger.add(
    log_path,
    level=config["log_level"],
    rotation=config["rotation"],
    retention=config["retention"],
    format=config["format"],
    enqueue=True, # Makes logging thread-safe
    colorize=True
)

logger.add(
    lambda msg: print(msg, end=""), # Print to terminal
    level=config["log_level"],
    format=config["format"],
    colorize=True
)