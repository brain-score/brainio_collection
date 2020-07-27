import logging
import os
from pathlib import Path

import pandas as pd
import peewee

_logger = logging.getLogger(__name__)

TYPE_ASSEMBLY = 'assembly'
TYPE_STIMULUS_SET = 'stimulus_set'

path = Path(__file__).parent / "lookup.csv"
_logger.debug(f"Loading lookup from {path}")
print(f"Loading lookup from {path}")  # print because logging usually isn't set up at this point during import
data = pd.read_csv(path)


def _is_csv_lookup(data_row):
    return data_row['lookup_type'] == TYPE_STIMULUS_SET \
           and data_row['location'].endswith('.csv') \
           and data_row['object_class'] is not None


def _is_zip_lookup(data_row):
    return data_row['lookup_type'] == TYPE_STIMULUS_SET \
           and data_row['location'].endswith('.zip') \
           and data_row['object_class'] is None


def append(object_identifier, object_class, lookup_type,
           bucket_name, sha1, s3_key, stimulus_set_name=None):
    global data
    _logger.debug(f"Adding {object_identifier} to lookup")
    object_lookup = {'identifier': object_identifier, 'stimulus_set_identifier': stimulus_set_name,
                     'object_class': object_class, 'lookup_type': lookup_type,
                     'location_type': "S3", 'location': f"https://{bucket_name}.s3.amazonaws.com/{s3_key}",
                     "sha1": sha1}
    # check duplicates
    assert object_lookup['lookup_type'] in [TYPE_ASSEMBLY, TYPE_STIMULUS_SET]
    duplicates = data[data['identifier'] == object_lookup['identifier']]
    if len(duplicates) > 0:
        if object_lookup['lookup_type'] == TYPE_ASSEMBLY:
            raise ValueError(
                f"Trying to add duplicate identifier {object_lookup['identifier']}, existing {duplicates}")
        elif object_lookup['lookup_type'] == TYPE_STIMULUS_SET:
            if len(duplicates) == 1 and duplicates.squeeze()['identifier'] == object_lookup['identifier'] and (
                    (_is_csv_lookup(duplicates.squeeze()) and _is_zip_lookup(object_lookup)) or
                    (_is_zip_lookup(duplicates.squeeze()) and _is_csv_lookup(object_lookup))):
                pass  # all good, we're just adding the second part of a stimulus set
            else:
                raise ValueError(
                    f"Trying to add duplicate identifier {object_lookup['identifier']}, existing {duplicates}")
    # append and save
    add_lookup = pd.DataFrame({key: [value] for key, value in object_lookup.items()})
    data = data.append(add_lookup)
    data.to_csv(path, index=False)


lookupdb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "lookup.db"))
_logger.debug(f"Loading database from {lookupdb_path}")
pwdb = peewee.SqliteDatabase(lookupdb_path)
