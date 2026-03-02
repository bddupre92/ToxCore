"""Base ETL class with common functionality."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseETL(ABC):
    """Base class for all ETL pipelines."""

    def __init__(self, db_url: str, cache_dir: Path | None = None) -> None:
        self.db_url = db_url
        self.cache_dir = cache_dir or Path("data/.cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def download(self) -> Path:
        """Download source data. Returns path to downloaded file."""
        ...

    @abstractmethod
    async def parse(self, source: Path) -> list[dict[str, Any]]:
        """Parse source data into records."""
        ...

    @abstractmethod
    async def load(self, records: list[dict[str, Any]]) -> int:
        """Load records into database. Returns count loaded."""
        ...

    async def run(self) -> dict[str, Any]:
        """Execute full ETL pipeline."""
        self.logger.info("Starting %s ETL pipeline", self.__class__.__name__)

        self.logger.info("Downloading...")
        source = await self.download()

        self.logger.info("Parsing...")
        records = await self.parse(source)
        self.logger.info("Parsed %d records", len(records))

        self.logger.info("Loading...")
        loaded = await self.load(records)
        self.logger.info("Loaded %d records", loaded)

        result = {
            "pipeline": self.__class__.__name__,
            "parsed": len(records),
            "loaded": loaded,
        }

        self.logger.info("Pipeline complete: %s", result)
        return result

    @abstractmethod
    def validate(self) -> dict[str, Any]:
        """Post-load validation checks."""
        ...
