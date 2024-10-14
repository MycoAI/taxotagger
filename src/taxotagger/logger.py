import logging
from rich.console import Console
from rich.logging import RichHandler


def setup_logging(
    level: str = "INFO",
    file: str = "",
    to_console: bool = True,
) -> None:
    """Setup logging configuration for the ancestor logger "taxotagger".

    Args:
        level: The log level, use the logging module's log level constants.
            Valid levels are: `NOTSET`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
        file: The file to write the log to.
            If the file is an empty string (by default), the log will not be written to a file.
            If the file does not exist, it will be created.
            The log will be written to the file in append mode.
        to_console: Whether to log to the console.
    """
    # Get the ancestor logger "taxotagger"
    logger = logging.getLogger("taxotagger")
    logger.setLevel(level)
    logger.handlers.clear()

    # File handler
    if file:
        logger.addHandler(
            RichHandler(
                # force line wrapping at 200 characters, otherwise it will wrap at the console width
                console=Console(file=open(file, "a"), width=200),
                omit_repeated_times=False,
                rich_tracebacks=True,
                tracebacks_show_locals=True,
                log_time_format="[%Y-%m-%d %X]",
                markup=True,
            )
        )

    # Console handler
    if to_console:
        logger.addHandler(
            RichHandler(
                omit_repeated_times=False,
                rich_tracebacks=True,
                tracebacks_show_locals=True,
                log_time_format="[%Y-%m-%d %X]",
                markup=True,
            )
        )
