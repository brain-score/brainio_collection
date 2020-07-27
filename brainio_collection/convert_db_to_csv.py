from brainio_base.assemblies import walk_coords
from xarray import DataArray
import logging
import sys

import brainio_collection
from brainio_collection import assemblies, stimuli
from brainio_collection.packaging import package_stimulus_set, package_data_assembly


def repackage_stimulus_sets():
    for identifier in stimuli.list_stimulus_sets():
        stimulus_set = brainio_collection.get_stimulus_set(identifier)
        package_stimulus_set(stimulus_set, stimulus_set_identifier=stimulus_set.name, bucket_name='brainio-temp')


def _strip_presentation_coords(assembly):
    presentation_columns = [coord for coord, dim, values in walk_coords(assembly['presentation'])]
    redundant_coords = set(presentation_columns) - {'image_id', 'repetition', 'repetition_id'}
    assembly = DataArray(assembly)
    assembly = assembly.reset_index('presentation')
    assembly = assembly.drop(redundant_coords)
    return assembly


def repackage_assemblies():
    for identifier in assemblies.list_assemblies():
        assembly = brainio_collection.get_assembly(identifier)
        stimulus_set_identifier = assembly.stimulus_set_name
        # fix individual assemblies
        assembly_class = assembly.__class__.__name__
        if identifier == 'dicarlo.Kar2019': # special case for OST
            assembly_class = 'DataAssembly'  # it's not actually a NeuronRecordingAssembly because it contains OSTs
        # strip
        assembly = _strip_presentation_coords(assembly)
        del assembly.attrs['stimulus_set']
        del assembly.attrs['stimulus_set_name']
        # package
        package_data_assembly(assembly, assembly_identifier=assembly.name,
                              stimulus_set_identifier=stimulus_set_identifier,
                              assembly_class=assembly_class, bucket_name='brainio-temp')


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    for ignore_logger in ['peewee', 's3transfer', 'botocore', 'boto3', 'urllib3', 'PIL']:
        logging.getLogger(ignore_logger).setLevel(logging.INFO)

    repackage_stimulus_sets()
    repackage_assemblies()
