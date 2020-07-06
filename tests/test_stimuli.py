import os

import imageio
import numpy as np
import pytest

import brainio_collection


def test_get_stimulus_set():
    stimulus_set = brainio_collection.get_stimulus_set("dicarlo.hvm-public")
    assert "image_id" in stimulus_set.columns
    assert stimulus_set.shape == (3200, 17)
    assert stimulus_set.name == 'dicarlo.hvm-public'
    for image_id in stimulus_set['image_id']:
        image_path = stimulus_set.get_image(image_id)
        assert os.path.exists(image_path)


def test_loadname_dicarlo_hvm():
    assert brainio_collection.get_stimulus_set(name="dicarlo.hvm-public") is not None


class TestLoadImage:
    def test_dicarlohvm(self):
        stimulus_set = brainio_collection.get_stimulus_set(name="dicarlo.hvm-public")
        paths = stimulus_set.image_paths.values()
        for path in paths:
            image = imageio.imread(path)
            assert isinstance(image, np.ndarray)
            assert image.size > 0


@pytest.mark.parametrize('stimulus_set', (
        'dicarlo.hvm',
        'dicarlo.hvm-public',
        'dicarlo.hvm-private',
        'gallant.David2004',
        'tolias.Cadena2017',
        'movshon.FreemanZiemba2013',
        'movshon.FreemanZiemba2013-public',
        'movshon.FreemanZiemba2013-private',
        'dicarlo.objectome.public',
        'dicarlo.objectome.private',
        'dicarlo.Kar2018cocogray',
        'klab.Zhang2018.search_obj_array',
        'dicarlo.Rajalingham2020orthographic_IT',
        'dicarlo.Sanghavi2020',
))
def test_list_stimulus_set(stimulus_set):
    l = brainio_collection.list_stimulus_sets()
    assert stimulus_set in l


@pytest.mark.private_access
def test_klab_Zhang2018search():
    stimulus_set = brainio_collection.get_stimulus_set('klab.Zhang2018.search_obj_array')
    # There are 300 presentation images in the assembly but 606 in the StimulusSet (explanation from @shashikg follows).
    # For each of the visual search task out of total 300, you need two images (one - the target image,
    # second - the search space image) plus there are 6 different mask images to mask objects
    # present at 6 different locations in a specified search image.
    # Therefore, a total of 300 * 2 + 6 images are there in the stimulus set.
    assert len(stimulus_set) == 606
    assert len(set(stimulus_set['image_id'])) == 606
