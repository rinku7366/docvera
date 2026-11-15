import logging
import sys

# Standard Python logging configured once here.
# Why: centralised logger means all modules use the same format and level.
# To add JSON logging for production, swap the formatter for pythonjsonlogger.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("docvera")
