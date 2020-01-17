import logging
import os

import peewee

_logger = logging.getLogger(__name__)

lookupdb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "lookup.db"))
_logger.debug(f"Loading database from {lookupdb_path}")
pwdb = peewee.SqliteDatabase(lookupdb_path)
