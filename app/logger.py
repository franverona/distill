import logging

import structlog

from app.config import settings


def configure_logging() -> None:
    processors = [
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
        if settings.environment == "production"
        else structlog.dev.ConsoleRenderer(),
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


log = structlog.get_logger()
