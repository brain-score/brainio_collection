import logging
import os

import peewee

from .fetch import get_fetcher

_logger = logging.getLogger(__name__)
_db_unique_name = "lookup_db"
_db_location = "https://brainio-collection.s3.amazonaws.com/lookup.db"
_fetcher = get_fetcher("S3", _db_location, _db_unique_name)

lookupdb_path = _fetcher.fetch()
_logger.debug(f"Loading database from {lookupdb_path}")
pwdb = peewee.SqliteDatabase(lookupdb_path)
