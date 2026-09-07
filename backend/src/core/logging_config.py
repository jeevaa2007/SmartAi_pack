import logging
import os
import sys
from loguru import logger
from src.core.config import settings

class InterceptHandler(logging.Handler):
    """
    Default handler to intercept standard Python logging and redirect it to Loguru.
    """
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup_logging():
    """
    Initializes Loguru logging framework. Configures separate log files with dedicated
    filters for Systems, Database queries, AI inference metrics, Audits, and general Errors.
    """
    logger.remove()

    log_dir = settings.LOG_DIR
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Base logging format including request correlation id tracking
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "req_id={extra[request_id]} | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Add default context variable for request_id to avoid key errors
    logger.configure(extra={"request_id": "system"})

    # 1. Output to standard out (Console)
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True
    )

    # 2. System Logs (Core boot, config validation)
    logger.add(
        os.path.join(log_dir, "sys.log"),
        format=log_format,
        level="INFO",
        filter=lambda record: record["name"].startswith("src.core") or record["name"] == "src.main",
        rotation=settings.LOG_ROTATION_SIZE,
        retention="14 days"
    )

    # 3. Database Execution Logs
    logger.add(
        os.path.join(log_dir, "db.log"),
        format=log_format,
        level="DEBUG",
        filter=lambda record: "sqlalchemy" in record["name"] or "database" in record["name"],
        rotation="10MB",
        retention="7 days"
    )

    # 4. AI & Inference Diagnostic Logs
    logger.add(
        os.path.join(log_dir, "ai.log"),
        format=log_format,
        level="DEBUG",
        filter=lambda record: "ai" in record["name"] or "cv_engine" in record["name"],
        rotation="50MB",
        retention="14 days"
    )

    # 5. Error Logs (Captures errors and critical warnings across all packages)
    logger.add(
        os.path.join(log_dir, "error.log"),
        format=log_format,
        level="WARNING",
        rotation=settings.LOG_ROTATION_SIZE,
        retention="30 days"
    )

    # 6. Audit & Supervisor Log (Bypasses, authentication validations)
    logger.add(
        os.path.join(log_dir, "audit.log"),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | audit_tag | {message}",
        level="INFO",
        filter=lambda record: "audit" in record["extra"] or "security" in record["name"],
        rotation="10MB",
        retention="90 days"
    )

    # Apply Intercept Handler to standard library loggers
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Redirect specifically uvicorn access and SQLAlchemy loggers
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.engine"):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False
        
    logger.info("Application logging successfully initialized and split.")
