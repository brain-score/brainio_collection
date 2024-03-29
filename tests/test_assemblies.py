import numpy as np
import os
import pytest
import xarray as xr
from PIL import Image
from pathlib import Path
from pytest import approx

import brainio_collection
from brainio_base import assemblies
from brainio_base.assemblies import DataAssembly
from brainio_collection import fetch


@pytest.mark.parametrize('assembly', (
        'dicarlo.MajajHong2015',
        'dicarlo.MajajHong2015.private',
        'dicarlo.MajajHong2015.public',
        'dicarlo.MajajHong2015.temporal',
        'dicarlo.MajajHong2015.temporal.private',
        'dicarlo.MajajHong2015.temporal.public',
        'dicarlo.MajajHong2015.temporal-10ms',
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
        'aru.Kuzovkin2018',
        'dicarlo.Rajalingham2020',
        'dicarlo.SanghaviMurty2020',
        'dicarlo.SanghaviJozwik2020',
        'dicarlo.Sanghavi2020',
        'dicarlo.SanghaviMurty2020THINGS1',
        'dicarlo.SanghaviMurty2020THINGS2',
        'aru.Kuzovkin2018',
        'dicarlo.Seibert2019',
        'aru.Cichy2019',
        'dicarlo.Rust2012.single',
        'dicarlo.Rust2012.array',
        'dicarlo.BashivanKar2019.naturalistic',
        'dicarlo.BashivanKar2019.synthetic',
        'movshon.Cavanaugh2002a',
        'devalois.DeValois1982a',
        'devalois.DeValois1982b',
        'movshon.FreemanZiemba2013_V1_properties',
        'shapley.Ringach2002',
        'schiller.Schiller1976c',
))
def test_list_assembly(assembly):
    l = brainio_collection.list_assemblies()
    assert assembly in l


@pytest.mark.parametrize('assembly_identifier', [
    pytest.param('gallant.David2004', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.MajajHong2015', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.MajajHong2015.public', marks=[]),
    pytest.param('dicarlo.MajajHong2015.private', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.MajajHong2015.temporal', marks=[pytest.mark.private_access, pytest.mark.memory_intense]),
    pytest.param('dicarlo.MajajHong2015.temporal.public', marks=[pytest.mark.memory_intense]),
    pytest.param('dicarlo.MajajHong2015.temporal.private',
                 marks=[pytest.mark.private_access, pytest.mark.memory_intense]),
    # pytest.param('dicarlo.MajajHong2015.temporal-10ms', marks=[pytest.mark.private_access, pytest.mark.memory_intense]),
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
    pytest.param('aru.Kuzovkin2018', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.Rajalingham2020', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.SanghaviMurty2020', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.SanghaviJozwik2020', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.Sanghavi2020', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.SanghaviMurty2020THINGS1', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.SanghaviMurty2020THINGS2', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.Seibert2019', marks=[pytest.mark.private_access]),
    pytest.param('aru.Cichy2019', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.Rust2012.single', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.Rust2012.array', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.BashivanKar2019.naturalistic', marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.BashivanKar2019.synthetic', marks=[pytest.mark.private_access]),
])
def test_existence(assembly_identifier):
    assert brainio_collection.get_assembly(assembly_identifier) is not None


def test_nr_assembly_ctor():
    assy_hvm = brainio_collection.get_assembly(identifier="dicarlo.MajajHong2015.public")
    assert isinstance(assy_hvm, DataAssembly)


def test_load():
    assy_hvm = brainio_collection.get_assembly(identifier="dicarlo.MajajHong2015.public")
    assert assy_hvm.shape == (256, 148480, 1)
    print(assy_hvm)


def test_repr():
    assy_hvm = brainio_collection.get_assembly(identifier="dicarlo.MajajHong2015.public")
    repr_hvm = repr(assy_hvm)
    assert "neuroid" in repr_hvm
    assert "presentation" in repr_hvm
    assert "256" in repr_hvm
    assert "148480" in repr_hvm
    assert "animal" in repr_hvm
    print(repr_hvm)


def test_getitem():
    assy_hvm = brainio_collection.get_assembly(identifier="dicarlo.MajajHong2015.public")
    single = assy_hvm[0, 0, 0]
    assert type(single) is type(assy_hvm)


def test_lookup():
    assy = brainio_collection.lookup.lookup_assembly("dicarlo.MajajHong2015.public")
    assert assy['identifier'] == "dicarlo.MajajHong2015.public"
    assert assy['location_type'] == "S3"
    hvm_s3_url = "https://brainio.dicarlo.s3.amazonaws.com/assy_dicarlo_MajajHong2015_public.nc"
    assert assy['location'] == hvm_s3_url


def test_lookup_bad_name():
    with pytest.raises(brainio_collection.lookup.AssemblyLookupError):
        brainio_collection.lookup.lookup_assembly("BadName")


def test_fetch():
    local_path = fetch.fetch_file(
        location_type='S3',
        location='https://brainio.dicarlo.s3.amazonaws.com/assy_dicarlo_MajajHong2015_public.nc',
        sha1='13d28ca0ce88ee550b54db3004374ae19096e9b9')
    assert os.path.exists(local_path)


def test_wrap():
    assy_hvm = brainio_collection.get_assembly(identifier="dicarlo.MajajHong2015.public")
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
    assy_hvm = brainio_collection.get_assembly(identifier="dicarlo.MajajHong2015.public")
    hvm_it_v3 = assy_hvm.sel(variation=3).sel(region="IT")
    hvm_it_v3.load()
    hvm_it_v3_obj = hvm_it_v3.multi_groupby(["category_name", "object_name"]).mean(dim="presentation")
    assert "category_name" in hvm_it_v3_obj.indexes["presentation"].names
    assert "object_name" in hvm_it_v3_obj.indexes["presentation"].names


def test_stimulus_set_from_assembly():
    assy_hvm = brainio_collection.get_assembly(identifier="dicarlo.MajajHong2015.public")
    stimulus_set = assy_hvm.attrs["stimulus_set"]
    assert stimulus_set.shape[0] == np.unique(assy_hvm["image_id"]).shape[0]
    for image_id in stimulus_set['image_id']:
        image_path = stimulus_set.get_image(image_id)
        assert os.path.exists(image_path)


@pytest.mark.private_access
def test_klab_Zhang2018search():
    assembly = brainio_collection.get_assembly('klab.Zhang2018search_obj_array')
    assert set(assembly.dims) == {'presentation', 'fixation', 'position'}
    assert len(assembly['presentation']) == 4500
    assert len(set(assembly['image_id'].values)) == 300
    assert len(set(assembly['subjects'].values)) == 15
    assert len(assembly['fixation']) == 8
    assert len(assembly['position']) == 2
    assert assembly.stimulus_set is not None


class TestFreemanZiemba:
    @pytest.mark.parametrize('identifier', [
        pytest.param('movshon.FreemanZiemba2013.public', marks=[]),
        pytest.param('movshon.FreemanZiemba2013.private', marks=[pytest.mark.private_access]),
    ])
    def test_v1_v2_alignment(self, identifier):
        assembly = brainio_collection.get_assembly(identifier)
        v1 = assembly[{'neuroid': [region == 'V1' for region in assembly['region'].values]}]
        v2 = assembly[{'neuroid': [region == 'V2' for region in assembly['region'].values]}]
        assert len(v1['presentation']) == len(v2['presentation'])
        assert set(v1['image_id'].values) == set(v2['image_id'].values)

    @pytest.mark.parametrize('identifier', [
        pytest.param('movshon.FreemanZiemba2013.public', marks=[]),
        pytest.param('movshon.FreemanZiemba2013.private', marks=[pytest.mark.private_access]),
    ])
    def test_num_neurons(self, identifier):
        assembly = brainio_collection.get_assembly(identifier)
        assert len(assembly['neuroid']) == 205
        v1 = assembly[{'neuroid': [region == 'V1' for region in assembly['region'].values]}]
        assert len(v1['neuroid']) == 102
        v2 = assembly[{'neuroid': [region == 'V2' for region in assembly['region'].values]}]
        assert len(v2['neuroid']) == 103

    @pytest.mark.parametrize('identifier', [
        pytest.param('movshon.FreemanZiemba2013.public', marks=[]),
        pytest.param('movshon.FreemanZiemba2013.private', marks=[pytest.mark.private_access]),
    ])
    def test_nonzero(self, identifier):
        assembly = brainio_collection.get_assembly(identifier)
        nonzero = np.count_nonzero(assembly)
        assert nonzero > 0

    @pytest.mark.parametrize('identifier, image_id, expected_amount_gray, ratio_gray', [
        pytest.param('movshon.FreemanZiemba2013.public', '21041db1f26c142812a66277c2957fb3e2070916',
                     31756, .3101171875, marks=[]),
        pytest.param('movshon.FreemanZiemba2013.private', 'bfd26c127f8ba028cc95cdc95f00c45c8884b365',
                     31585, .308447265625, marks=[pytest.mark.private_access]),
    ])
    def test_aperture(self, identifier, image_id, expected_amount_gray, ratio_gray):
        """ test a random image for the correct amount of gray pixels """
        assembly = brainio_collection.get_assembly(identifier)
        stimulus_set = assembly.stimulus_set
        image_path = Path(stimulus_set.get_image(image_id))
        assert image_path.is_file()
        # count number of gray pixels in image
        image = Image.open(image_path)
        image = np.array(image)
        amount_gray = 0
        for index in np.ndindex(image.shape[:2]):
            color = image[index]
            gray = [128, 128, 128]
            if (color == gray).all():
                amount_gray += 1
        assert amount_gray / image.size == approx(ratio_gray, abs=.0001)
        assert amount_gray == expected_amount_gray


def test_inplace():
    d = xr.DataArray(0, None, None, None, None, None, False)
    with pytest.raises(TypeError) as te:
        d = d.reset_index(None, inplace=True)
    assert "inplace" in str(te.value)


class TestSeibert:
    @pytest.mark.private_access
    def test_dims(self):
        assembly = brainio_collection.get_assembly('dicarlo.Seibert2019')
        # neuroid: 258 presentation: 286080 time_bin: 1
        assert assembly.dims == ("neuroid", "presentation", "time_bin")
        assert len(assembly['neuroid']) == 258
        assert len(assembly['presentation']) == 286080
        assert len(assembly['time_bin']) == 1

    @pytest.mark.private_access
    def test_coords(self):
        assembly = brainio_collection.get_assembly('dicarlo.Seibert2019')
        assert len(set(assembly['image_id'].values)) == 5760
        assert len(set(assembly['neuroid_id'].values)) == 258
        assert len(set(assembly['animal'].values)) == 3
        assert len(set(assembly['region'].values)) == 2
        assert len(set(assembly['variation'].values)) == 3

    @pytest.mark.private_access
    def test_content(self):
        assembly = brainio_collection.get_assembly('dicarlo.Seibert2019')
        assert np.count_nonzero(np.isnan(assembly)) == 19118720
        assert assembly.stimulus_set_identifier == "dicarlo.hvm"
        hvm = assembly.stimulus_set
        assert hvm.shape == (5760, 18)


class TestRustSingle:
    @pytest.mark.private_access
    def test_dims(self):
        assembly = brainio_collection.get_assembly('dicarlo.Rust2012.single')
        # (neuroid: 285, presentation: 1500, time_bin: 1)
        assert assembly.dims == ("neuroid", "presentation", "time_bin")
        assert len(assembly['neuroid']) == 285
        assert len(assembly['presentation']) == 1500
        assert len(assembly['time_bin']) == 1

    @pytest.mark.private_access
    def test_coords(self):
        assembly = brainio_collection.get_assembly('dicarlo.Rust2012.single')
        assert len(set(assembly['image_id'].values)) == 300
        assert len(set(assembly['neuroid_id'].values)) == 285
        assert len(set(assembly['region'].values)) == 2


class TestRustArray:
    @pytest.mark.private_access
    def test_dims(self):
        assembly = brainio_collection.get_assembly('dicarlo.Rust2012.array')
        # (neuroid: 296, presentation: 53700, time_bin: 6)
        assert assembly.dims == ("neuroid", "presentation", "time_bin")
        assert len(assembly['neuroid']) == 296
        assert len(assembly['presentation']) == 53700
        assert len(assembly['time_bin']) == 6

    @pytest.mark.private_access
    def test_coords(self):
        assembly = brainio_collection.get_assembly('dicarlo.Rust2012.array')
        assert len(set(assembly['image_id'].values)) == 300
        assert len(set(assembly['neuroid_id'].values)) == 296
        assert len(set(assembly['animal'].values)) == 2
        assert len(set(assembly['region'].values)) == 2


@pytest.mark.parametrize('assembly,shape,nans', [
    pytest.param('dicarlo.BashivanKar2019.naturalistic', (24320, 233, 1), 309760, marks=[pytest.mark.private_access]),
    pytest.param('dicarlo.BashivanKar2019.synthetic', (21360, 233, 1), 4319940, marks=[pytest.mark.private_access]),
])
def test_BashivanKar2019(assembly, shape, nans):
    assy = brainio_collection.get_assembly(assembly)
    assert assy.shape == shape
    assert np.count_nonzero(np.isnan(assy)) == nans


@pytest.mark.private_access
class TestMarques2020V1Properties:
    @pytest.mark.parametrize('identifier,num_neuroids,properties,stimulus_set_identifier', [
        ('movshon.Cavanaugh2002a', 190, [
            'surround_suppression_index', 'strongly_suppressed', 'grating_summation_field', 'surround_diameter',
            'surround_grating_summation_field_ratio'],
         'dicarlo.Marques2020_size'),
        ('devalois.DeValois1982a', 385, [
            'preferred_orientation'],
         'dicarlo.Marques2020_orientation'),
        ('devalois.DeValois1982b', 363, [
            'peak_spatial_frequency'],
         'dicarlo.Marques2020_spatial_frequency'),
        ('movshon.FreemanZiemba2013_V1_properties', 102, [
            'absolute_texture_modulation_index', 'family_variance', 'max_noise', 'max_texture', 'noise_selectivity',
            'noise_sparseness', 'sample_variance', 'texture_modulation_index', 'texture_selectivity',
            'texture_sparseness', 'variance_ratio'],
         'movshon.FreemanZiemba2013_properties'),
        ('shapley.Ringach2002', 304, [
            'bandwidth', 'baseline', 'circular_variance', 'circular_variance_bandwidth_ratio', 'max_ac', 'max_dc',
            'min_dc', 'modulation_ratio', 'orientation_selective', 'orthogonal_preferred_ratio',
            'orthogonal_preferred_ratio_bandwidth_ratio', 'orthogonal_preferred_ratio_circular_variance_difference'],
         'dicarlo.Marques2020_orientation'),
        ('schiller.Schiller1976c', 87, [
            'spatial_frequency_selective', 'spatial_frequency_bandwidth'],
         'dicarlo.Marques2020_spatial_frequency'),
    ])
    def test_assembly(self, identifier, num_neuroids, properties, stimulus_set_identifier):
        assembly = brainio_collection.get_assembly(identifier)
        assert set(assembly.dims) == {'neuroid', 'neuronal_property'}
        assert len(assembly['neuroid']) == num_neuroids
        assert set(assembly['neuronal_property'].values) == set(properties)
        assert assembly.stimulus_set is not None
        assert assembly.stimulus_set.identifier == stimulus_set_identifier
