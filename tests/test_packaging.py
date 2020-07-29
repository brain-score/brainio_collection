import os
import zipfile

import datetime
import pandas as pd
import pytest
from pathlib import Path

from brainio_base.stimuli import StimulusSet

import brainio_collection
from brainio_collection.lookup import sha1_hash
from brainio_collection.packaging import package_stimulus_set, create_image_zip


def now():
    return datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")


def prep_proto_stim():
    image_dir = Path(__file__).parent / "images"
    csv_path = image_dir / "test_images.csv"
    proto = pd.read_csv(csv_path)
    proto["image_id"] = [f"{iid}.{now()}" for iid in proto["image_id"]]
    proto[f"test_{now()}"] = [f"{iid}.{now()}" for iid in proto["image_id"]]
    proto = StimulusSet(proto)
    proto.image_paths = {row.image_id: image_dir / row.image_current_relative_file_path for row in proto.itertuples()}
    return proto


def test_create_image_zip():
    target_zip_path = Path(__file__).parent / "test_images.zip"
    proto = prep_proto_stim()
    sha1, _ = create_image_zip(proto, target_zip_path)
    with zipfile.ZipFile(target_zip_path, "r") as target_zip:
        infolist = target_zip.infolist()
        assert len(infolist) == 25
        for zi in infolist:
            print(zi.filename)
            print(len(zi.filename))
            assert zi.filename.endswith(".png")
            assert not zi.is_dir()
            assert len(zi.filename) == 44


@pytest.mark.private_access
def test_package_stimulus_set():
    proto = prep_proto_stim()
    stim_set_name = "dicarlo.test." + now()
    test_bucket = "brainio-temp"
    package_stimulus_set(proto, stimulus_set_identifier=stim_set_name, bucket_name=test_bucket)
    stim_set_fetched = brainio_collection.get_stimulus_set(stim_set_name)
    assert len(proto) == len(stim_set_fetched)
    for image in proto.itertuples():
        orig = proto.get_image(image.image_id)
        fetched = stim_set_fetched.get_image(image.image_id)
        assert os.path.basename(orig) == os.path.basename(fetched)
        sha1_orig = sha1_hash(orig)
        sha1_fetched = sha1_hash(fetched)
        assert sha1_orig == sha1_fetched
