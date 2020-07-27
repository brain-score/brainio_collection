import hashlib
import logging
import os
import zipfile
from pathlib import Path

import boto3
from tqdm import tqdm

from brainio_base.stimuli import StimulusSet
from brainio_collection import lookup
from brainio_collection.lookup import TYPE_ASSEMBLY, TYPE_STIMULUS_SET

_logger = logging.getLogger(__name__)


def sha1_hash(path, buffer_size=64 * 2 ** 10):
    sha1 = hashlib.sha1()
    with open(path, "rb") as f:
        buffer = f.read(buffer_size)
        while len(buffer) > 0:
            sha1.update(buffer)
            buffer = f.read(buffer_size)
    return sha1.hexdigest()


def create_image_zip(proto_stimulus_set, target_zip_path):
    _logger.debug(f"Zipping stimulus set to {target_zip_path}")
    assert isinstance(proto_stimulus_set, StimulusSet), f"Expected StimulusSet object, got {proto_stimulus_set}"
    os.makedirs(os.path.dirname(target_zip_path), exist_ok=True)
    with zipfile.ZipFile(target_zip_path, 'w') as target_zip:
        for image in proto_stimulus_set.itertuples():
            arcname = image.image_path_within_store if hasattr(image, 'image_path_within_store') \
                else image.image_file_name
            target_zip.write(proto_stimulus_set.get_image(image.image_id), arcname=arcname)
    sha1 = sha1_hash(target_zip_path)
    return sha1


def upload_to_s3(source_file_path, bucket_name, target_s3_key):
    _logger.debug(f"Uploading {source_file_path} to {bucket_name}/{target_s3_key}")

    file_size = os.path.getsize(source_file_path)
    with tqdm(total=file_size, unit='B', unit_scale=True, desc="upload to s3") as progress_bar:
        def progress_hook(bytes_amount):
            if bytes_amount > 0:  # at the end, this sometimes passes a negative byte amount which tqdm can't handle
                progress_bar.update(bytes_amount)

        client = boto3.client('s3')
        client.upload_file(str(source_file_path), bucket_name, target_s3_key, Callback=progress_hook)


def extract_specific(proto_stimulus_set):
    general = ['image_current_local_file_path', 'image_id', 'image_path_within_store']
    stimulus_set_specific_attributes = []
    for name in list(proto_stimulus_set):
        if name not in general:
            stimulus_set_specific_attributes.append(name)
    return stimulus_set_specific_attributes


def create_image_csv(proto_stimulus_set, target_path):
    _logger.debug(f"Writing csv to {target_path}")
    specific_columns = extract_specific(proto_stimulus_set)
    specific_stimulus_set = proto_stimulus_set[specific_columns]
    specific_stimulus_set.to_csv(target_path, index=False)
    sha1 = sha1_hash(target_path)
    return sha1


def package_stimulus_set(proto_stimulus_set, stimulus_set_name, bucket_name="brainio-contrib"):
    """
    Package a set of images along with their metadata for the BrainIO system.
    :param proto_stimulus_set: A StimulusSet containing one row for each image,
        and the columns {'image_id', 'image_file_name', ['image_path_within_store' (optional to structure zip directory layout)]}
        and columns for all stimulus-set-specific metadata
    :param stimulus_set_name: A dot-separated string starting with a lab identifier.
    :param bucket_name: 'brainio-dicarlo' for DiCarlo Lab stimulus sets, 'brainio-contrib' for
    external stimulus sets.
    """
    # naming
    image_store_unique_name = "image_" + stimulus_set_name.replace(".", "_")
    # - csv
    csv_file_name = image_store_unique_name + ".csv"
    target_csv_path = Path(__file__).parent / csv_file_name
    # - zip
    zip_file_name = image_store_unique_name + ".zip"
    target_zip_path = Path(__file__).parent / zip_file_name
    # create csv and zip files
    csv_sha1 = create_image_csv(proto_stimulus_set, str(target_csv_path))
    image_zip_sha1 = create_image_zip(proto_stimulus_set, str(target_zip_path))
    # upload both to S3
    upload_to_s3(str(target_csv_path), bucket_name, target_s3_key=csv_file_name)
    upload_to_s3(str(target_zip_path), bucket_name, target_s3_key=zip_file_name)
    # link to csv and zip from same identifier. The csv however is the only one of the two rows with a class.
    lookup.append(object_identifier=stimulus_set_name, object_class='StimulusSet',
                  lookup_type=TYPE_STIMULUS_SET,
                  bucket_name=bucket_name, sha1=csv_sha1, s3_key=csv_file_name,
                  stimulus_set_name=None)
    lookup.append(object_identifier=stimulus_set_name, object_class=None,
                  lookup_type=TYPE_STIMULUS_SET,
                  bucket_name=bucket_name, sha1=image_zip_sha1, s3_key=zip_file_name,
                  stimulus_set_name=None)
    _logger.debug(f"stimulus set {stimulus_set_name} packaged")


def write_netcdf(assembly, target_netcdf_file):
    _logger.debug(f"Writing assembly to {target_netcdf_file}")
    for index in assembly.indexes.keys():
        assembly.reset_index(index, inplace=True)
    assembly.to_netcdf(target_netcdf_file)
    sha1 = sha1_hash(target_netcdf_file)
    return sha1


def verify_assembly(assembly):
    assert 'stimulus_set_name' in assembly.attrs, "Assembly needs to specify a 'stimulus_set_name' identifier " \
                                                  "in its `.attrs` to point to its corresponding StimulusSet"


def package_data_assembly(proto_data_assembly, data_assembly_name, stimulus_set_name,
                          assembly_class="NeuronRecordingAssembly", bucket_name="brainio-contrib"):
    """
    Package a set of data along with its metadata for the BrainIO system.
    :param proto_data_assembly: An xarray DataArray containing experimental measurements and all related metadata.
        * The dimensions of the DataArray (except for behavior) must be
            * neuroid
            * presentation
            * time_bin
        * The neuroid dimension must have a neuroid_id coordinate and should have coordinates for as much neural metadata as possible (e.g. region, subregion, animal, row in array, column in array, etc.)
        * The presentation dimension must have an image_id coordinate and should have coordinates for presentation-level metadata such as repetition and image_id.  The presentation dimension should not have coordinates for image-specific metadata, these will be drawn from the StimulusSet based on image_id.
        * The time_bin dimension should have coordinates time_bin_start and time_bin_end.
    :param data_assembly_name: A dot-separated string starting with a lab identifier.
        * For requests: <lab identifier>.<b for behavioral|n for neuroidal>.<m for monkey|h for human>.<proposer e.g. 'Margalit'>.<pull request number>
        * For published: <lab identifier>.<first author e.g. 'Rajalingham' or 'MajajHong' for shared first-author><YYYY year of publication>
    :param stimulus_set_name: The unique name of an existing StimulusSet in the BrainIO system.
    :param assembly_class: The name of a DataAssembly subclass.
    :param bucket_name: 'brainio-dicarlo' for DiCarlo Lab assemblies, 'brainio-contrib' for external assemblies.
    """
    verify_assembly(proto_data_assembly)

    assembly_store_unique_name = "assy_" + data_assembly_name.replace(".", "_")
    netcdf_file_name = assembly_store_unique_name + ".nc"
    target_netcdf_path = Path(__file__).parent / netcdf_file_name
    s3_key = netcdf_file_name

    netcdf_kf_sha1 = write_netcdf(proto_data_assembly, target_netcdf_path)
    upload_to_s3(target_netcdf_path, bucket_name, s3_key)
    lookup.append(object_identifier=data_assembly_name, stimulus_set_name=stimulus_set_name,
                  lookup_type=TYPE_ASSEMBLY,
                  bucket_name=bucket_name, sha1=netcdf_kf_sha1,
                  s3_key=s3_key, object_class=assembly_class)
    _logger.debug(f"assembly {data_assembly_name} packaged")
