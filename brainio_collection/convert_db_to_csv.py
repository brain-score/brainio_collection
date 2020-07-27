import logging
import sys

import brainio_collection
from brainio_collection import assemblies, stimuli
from brainio_collection.packaging import package_stimulus_set, package_data_assembly


def repackage_stimulus_sets():
    for identifier in stimuli.list_stimulus_sets():
        stimulus_set = brainio_collection.get_stimulus_set(identifier)
        package_stimulus_set(stimulus_set, stimulus_set_name=stimulus_set.name, bucket_name='brainio-temp')


def repackage_assemblies():
    for identifier in assemblies.list_assemblies():
        assembly = brainio_collection.get_assembly(identifier)
        package_data_assembly(assembly, data_assembly_name=assembly.name, stimulus_set_name=assembly.stimulus_set_name,
                              assembly_class=str(type(assembly)), bucket_name='brainio-temp')


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    for ignore_logger in ['peewee', 's3transfer', 'botocore', 'boto3', 'urllib3', 'PIL']:
        logging.getLogger(ignore_logger).setLevel(logging.INFO)

    repackage_stimulus_sets()
    repackage_assemblies()
