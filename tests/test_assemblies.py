import os

import numpy as np
import pytest
import xarray as xr

import brainio_collection
import brainio_collection.assemblies
from brainio_base import assemblies
from brainio_base.assemblies import DataAssembly
from brainio_collection import fetch


@pytest.mark.parametrize('assembly', (
        'dicarlo.Majaj2015',
        'dicarlo.Majaj2015.private',
        'dicarlo.Majaj2015.public',
        'dicarlo.Majaj2015.temporal',
        'dicarlo.Majaj2015.temporal.private',
        'dicarlo.Majaj2015.temporal.public',
        'dicarlo.Majaj2015.temporal-10ms',
        'gallant.David2004',
        'tolias.Cadena2017',
        'movshon.FreemanZiemba2013',
        'movshon.FreemanZiemba2013.private',
        'movshon.FreemanZiemba2013.public',
        'dicarlo.Rajalingham2018.public', 'dicarlo.Rajalingham2018.private',
        'dicarlo.Kar2019',
        'dicarlo.Kar2018hvm',
        'dicarlo.Kar2018cocogray',
        'klab.Zhang2018search_obj_array',
))
def test_list_assembly(assembly):
    l = brainio_collection.list_assemblies()
    assert assembly in l


@pytest.mark.parametrize('assembly_identifier', [
    pytest.param('gallant.David2004', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.Majaj2015', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.Majaj2015.public', marks=[]),
    pytest.param('dicarlo.Majaj2015.private', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.Majaj2015.temporal', marks=[pytest.mark.private_access, pytest.mark.memory_intense]),
    pytest.param('dicarlo.Majaj2015.temporal.public', marks=[pytest.mark.memory_intense]),
    pytest.param('dicarlo.Majaj2015.temporal.private', marks=[pytest.mark.private_access, pytest.mark.memory_intense]),
    # pytest.param('dicarlo.Majaj2015.temporal-10ms', marks=[pytest.mark.private_access, pytest.mark.memory_intense]),
    pytest.param('tolias.Cadena2017', marks=[pytest.mark.private_access]),
    pytest.param('movshon.FreemanZiemba2013', marks=[pytest.mark.private_access, pytest.mark.memory_intense]),
    pytest.param('movshon.FreemanZiemba2013.public', marks=[pytest.mark.memory_intense]),
    pytest.param('movshon.FreemanZiemba2013.private', marks=[pytest.mark.private_access, pytest.mark.memory_intense]),
    pytest.param('dicarlo.Rajalingham2018.public', marks=[]),
    pytest.param('dicarlo.Rajalingham2018.private', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.Kar2019', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.Kar2018hvm', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.Kar2018cocogray', marks=[pytest.mark.private_access]),
    pytest.param('klab.Zhang2018search_obj_array', marks=[pytest.mark.private_access]),
])
def test_existence(assembly_identifier):
    assert brainio_collection.get_assembly(assembly_identifier) is not None


def test_nr_assembly_ctor():
    assy_hvm = brainio_collection.get_assembly(name="dicarlo.Majaj2015.public")
    assert isinstance(assy_hvm, DataAssembly)


def test_load():
    assy_hvm = brainio_collection.get_assembly(name="dicarlo.Majaj2015.public")
    assert assy_hvm.shape == (256, 148480, 1)
    print(assy_hvm)


def test_repr():
    assy_hvm = brainio_collection.get_assembly(name="dicarlo.Majaj2015.public")
    repr_hvm = repr(assy_hvm)
    assert "neuroid" in repr_hvm
    assert "presentation" in repr_hvm
    assert "256" in repr_hvm
    assert "148480" in repr_hvm
    assert "animal" in repr_hvm
    print(repr_hvm)


def test_getitem():
    assy_hvm = brainio_collection.get_assembly(name="dicarlo.Majaj2015.public")
    single = assy_hvm[0, 0, 0]
    assert type(single) is type(assy_hvm)


def test_lookup():
    assy = brainio_collection.assemblies.lookup_assembly("dicarlo.Majaj2015.public")
    assert assy.name == "dicarlo.Majaj2015.public"
    store = assy.assembly_store_maps[0]
    assert store.role == "dicarlo.Majaj2015.public"
    assert store.assembly_store_model.location_type == "S3"
    hvm_s3_url = "https://brainio-dicarlo.s3.amazonaws.com/assy_dicarlo_Majaj2015_public.nc"
    assert store.assembly_store_model.location == hvm_s3_url


def test_lookup_bad_name():
    with pytest.raises(brainio_collection.assemblies.AssemblyLookupError) as err:
        brainio_collection.assemblies.lookup_assembly("BadName")


def test_fetch():
    assy_record = brainio_collection.assemblies.lookup_assembly("dicarlo.Majaj2015.public")
    local_paths = fetch.fetch_assembly(assy_record)
    assert len(local_paths) == 1
    print(local_paths["dicarlo.Majaj2015.public"])
    assert os.path.exists(local_paths["dicarlo.Majaj2015.public"])


def test_wrap():
    assy_hvm = brainio_collection.get_assembly(name="dicarlo.Majaj2015.public")
    hvm_v3 = assy_hvm.sel(variation=3)
    assert isinstance(hvm_v3, assemblies.NeuronRecordingAssembly)

    hvm_it_v3 = hvm_v3.sel(region="IT")
    assert isinstance(hvm_it_v3, assemblies.NeuronRecordingAssembly)

    hvm_it_v3.coords["cat_obj"] = hvm_it_v3.coords["category_name"] + hvm_it_v3.coords["object_name"]
    hvm_it_v3.load()
    hvm_it_v3_grp = hvm_it_v3.multi_groupby(["category_name", "object_name"])
    assert not isinstance(hvm_it_v3_grp, xr.core.groupby.GroupBy)
    assert isinstance(hvm_it_v3_grp, assemblies.GroupbyBridge)

    hvm_it_v3_obj = hvm_it_v3_grp.mean(dim="presentation")
    assert isinstance(hvm_it_v3_obj, assemblies.NeuronRecordingAssembly)

    hvm_it_v3_sqz = hvm_it_v3_obj.squeeze("time_bin")
    assert isinstance(hvm_it_v3_sqz, assemblies.NeuronRecordingAssembly)

    hvm_it_v3_t = hvm_it_v3_sqz.T
    assert isinstance(hvm_it_v3_t, assemblies.NeuronRecordingAssembly)


def test_multi_group():
    assy_hvm = brainio_collection.get_assembly(name="dicarlo.Majaj2015.public")
    hvm_it_v3 = assy_hvm.sel(variation=3).sel(region="IT")
    hvm_it_v3.load()
    hvm_it_v3_obj = hvm_it_v3.multi_groupby(["category_name", "object_name"]).mean(dim="presentation")
    assert "category_name" in hvm_it_v3_obj.indexes["presentation"].names
    assert "object_name" in hvm_it_v3_obj.indexes["presentation"].names


def test_stimulus_set_from_assembly():
    assy_hvm = brainio_collection.get_assembly(name="dicarlo.Majaj2015.public")
    stimulus_set = assy_hvm.attrs["stimulus_set"]
    assert stimulus_set.shape[0] == np.unique(assy_hvm["image_id"]).shape[0]
    for image_id in stimulus_set['image_id']:
        image_path = stimulus_set.get_image(image_id)
        assert os.path.exists(image_path)


@pytest.mark.private
def test_klab_Zhang2018search():
    assembly = brainio_collection.get_assembly('klab.Zhang2018search_obj_array')
    assert set(assembly.dims) == {'presentation', 'fixation', 'position'}
    assert len(assembly['presentation']) == 4500
    assert len(set(assembly['image_id'].values)) == 300
    assert len(set(assembly['subjects'].values)) == 15
    assert len(assembly['fixation']) == 8
    assert len(assembly['position']) == 2
    assert assembly.stimulus_set is not None
