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
        if identifier.startswith('movshon'):
            stimulus_set['image_path_within_store'] = stimulus_set['image_file_name']
        # re-assign bucket
        stimulus_set_model = stimuli.StimulusSetModel.get(stimuli.StimulusSetModel.name == identifier)
        location = stimulus_set_model.stimulus_set_image_maps[0].image.image_image_store_maps[0].image_store.location
        bucket = 'brainio-dicarlo' if 'brainio-dicarlo' in location else 'brainio-contrib'
        bucket = bucket.replace('-', '.')
        # package
        package_stimulus_set(stimulus_set, stimulus_set_identifier=stimulus_set.name, bucket_name=bucket)


def _strip_presentation_coords(assembly):
    presentation_columns = [coord for coord, dim, values in walk_coords(assembly['presentation'])]
    stimulus_set_columns = assembly.stimulus_set.columns
    redundant_coords = set(presentation_columns).intersection(set(stimulus_set_columns)) - {'image_id'}
    assembly = DataArray(assembly)
    assembly = assembly.reset_index('presentation')
    assembly = assembly.drop(redundant_coords)
    return assembly


def repackage_assemblies():
    for identifier in assemblies.list_assemblies():
        print(f"Repackaging {identifier}")
        assembly = brainio_collection.get_assembly(identifier)
        stimulus_set_identifier = assembly.stimulus_set_name
        # fix individual assemblies
        assembly_class = assembly.__class__.__name__
        if identifier == 'dicarlo.Kar2019':  # change OST assembly
            assembly_class = 'DataAssembly'  # it's not actually a NeuronRecordingAssembly because it contains OSTs
        if identifier == 'klab.Zhang2018search_obj_array':
            assembly_class = 'BehavioralAssembly'  # was incorrectly packaged as NeuronRecordingAssembly but is behavior
        if identifier.startswith('dicarlo.Majaj2015'):
            assembly.name = assembly.name.replace('Majaj2015', 'MajajHong2015')  # joint first authors
        # strip
        assembly = _strip_presentation_coords(assembly)
        del assembly.attrs['stimulus_set']
        del assembly.attrs['stimulus_set_name']
        # re-assign bucket
        assembly_model = assemblies.lookup_assembly(identifier)
        store = assembly_model.assembly_store_maps[0]
        location = store.assembly_store_model.location
        bucket = 'brainio-dicarlo' if 'brainio-dicarlo' in location else 'brainio-contrib'
        bucket = bucket.replace('-', '.')
        # package
        package_data_assembly(assembly, assembly_identifier=assembly.name,
                              stimulus_set_identifier=stimulus_set_identifier,
                              assembly_class=assembly_class, bucket_name=bucket)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    for ignore_logger in ['peewee', 's3transfer', 'botocore', 'boto3', 'urllib3', 'PIL']:
        logging.getLogger(ignore_logger).setLevel(logging.INFO)

    repackage_stimulus_sets()
    repackage_assemblies()
