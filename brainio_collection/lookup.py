import hashlib
import logging
import os
from pathlib import Path

import numpy as np
import pandas as pd
import peewee

_logger = logging.getLogger(__name__)

TYPE_ASSEMBLY = 'assembly'
TYPE_STIMULUS_SET = 'stimulus_set'

path = Path(__file__).parent / "lookup.csv"
_logger.debug(f"Loading lookup from {path}")
print(f"Loading lookup from {path}")  # print because logging usually isn't set up at this point during import
data = pd.read_csv(path)


def lookup_assembly(identifier):
    lookup = data[(data['identifier'] == identifier) & (data['lookup_type'] == TYPE_ASSEMBLY)]
    if len(lookup) == 0:
        raise KeyError(f"assembly {identifier} not found")
    if len(lookup) > 1:
        raise ValueError(f"Internal data inconsistency: Found multiple lookup rows for identifier {identifier}")
    lookup = lookup.squeeze()
    return lookup


def lookup_stimulus_set(identifier):
    lookup = data[(data['identifier'] == identifier) & (data['lookup_type'] == TYPE_STIMULUS_SET)]
    if len(lookup) == 0:
        raise KeyError(f"stimulus_set {identifier} not found")
    if len(lookup) > 2:
        raise ValueError(
            f"Internal data inconsistency: Found more than 2 lookup rows for stimulus_set identifier {identifier}")
    csv_lookup = [lookup_row for _, lookup_row in lookup.iterrows() if _is_csv_lookup(lookup_row)]
    zip_lookup = [lookup_row for _, lookup_row in lookup.iterrows() if _is_zip_lookup(lookup_row)]
    assert len(csv_lookup) == 1 and len(zip_lookup) == 1
    csv_lookup, zip_lookup = csv_lookup[0], zip_lookup[0]
    return csv_lookup, zip_lookup


def _is_csv_lookup(data_row):
    return data_row['lookup_type'] == TYPE_STIMULUS_SET \
           and data_row['location'].endswith('.csv') \
           and data_row['class'] not in [None, np.nan]


def _is_zip_lookup(data_row):
    return data_row['lookup_type'] == TYPE_STIMULUS_SET \
           and data_row['location'].endswith('.zip') \
           and data_row['class'] in [None, np.nan]


def append(object_identifier, cls, lookup_type,
           bucket_name, sha1, s3_key, stimulus_set_identifier=None):
    global data
    _logger.debug(f"Adding {object_identifier} to lookup")
    object_lookup = {'identifier': object_identifier, 'lookup_type': lookup_type, 'class': cls,
                     'location_type': "S3", 'location': f"https://{bucket_name}.s3.amazonaws.com/{s3_key}",
                     'sha1': sha1, 'stimulus_set_identifier': stimulus_set_identifier, }
    # check duplicates
    assert object_lookup['lookup_type'] in [TYPE_ASSEMBLY, TYPE_STIMULUS_SET]
    duplicates = data[(data['identifier'] == object_lookup['identifier']) &
                      (data['lookup_type'] == object_lookup['lookup_type'])]
    if len(duplicates) > 0:
        if object_lookup['lookup_type'] == TYPE_ASSEMBLY:
            raise ValueError(f"Trying to add duplicate identifier {object_lookup['identifier']}, "
                             f"existing \n{duplicates.to_string()}")
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


def sha1_hash(path, buffer_size=64 * 2 ** 10):
    sha1 = hashlib.sha1()
    with open(path, "rb") as f:
        buffer = f.read(buffer_size)
        while len(buffer) > 0:
            sha1.update(buffer)
            buffer = f.read(buffer_size)
    return sha1.hexdigest()
