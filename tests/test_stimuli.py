import os

import imageio
import numpy as np
import pytest

import brainio_collection


def test_get_stimulus_set():
    stimulus_set = brainio_collection.get_stimulus_set("dicarlo.hvm")
    assert "image_id" in stimulus_set.columns
    assert stimulus_set.shape == (5760, 17)
    assert stimulus_set.name == 'dicarlo.hvm'
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
            image = imageio.imread(path)
            assert isinstance(image, np.ndarray)
            assert image.size > 0


@pytest.mark.parametrize('stimulus_set', (
        'dicarlo.hvm',
        'gallant.David2004',
        'tolias.Cadena2017',
        'movshon.FreemanZiemba2013',
        'dicarlo.objectome.public',
        'dicarlo.objectome.private',
        'dicarlo.Kar2018cocogray',
        'dicarlo.Kar2018coco_color.public',
        'dicarlo.Kar2018coco_color.private',
))
def test_list_stimulus_set(stimulus_set):
    l = brainio_collection.list_stimulus_sets()
    assert stimulus_set in l
