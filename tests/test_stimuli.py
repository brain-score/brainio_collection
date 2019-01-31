import os

import numpy as np
import scipy.misc

import brainio_collection


def test_get_stimulus_set():
    stimulus_set = brainio_collection.get_stimulus_set("dicarlo.hvm")
    assert "image_id" in stimulus_set.columns
    assert stimulus_set.shape == (5760, 17)
    for image_id in stimulus_set['image_id']:
        image_path = stimulus_set.get_image(image_id)
        assert os.path.exists(image_path)


def test_loadname_dicarlo_hvm():
    assert brainio_collection.get_stimulus_set(name="dicarlo.hvm") is not None


class TestLoadImage:
    def test_dicarlohvm(self):
        stimulus_set = brainio_collection.get_stimulus_set(name="dicarlo.hvm")
        paths = stimulus_set.image_paths.values()
        for path in paths:
            image = scipy.misc.imread(path)
            assert isinstance(image, np.ndarray)
            assert image.size > 0
