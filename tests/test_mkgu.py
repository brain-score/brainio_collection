#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_mkgu
----------------------------------

Tests for `mkgu` module.
"""

import os
import pytest
import numpy as np
import mkgu
from mkgu import assemblies, fetch
from mkgu import metrics
import pandas as pd
import xarray as xr
from pytest import approx



@pytest.fixture
def response():
    """Sample pytest fixture.
    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/jjpr-mit/mkgu')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument.
    """
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_nr_assembly_ctor():
    assy_hvm = mkgu.get_assembly(name="HvMWithDiscfade")

def test_load():
    print(os.getcwd())
    it_rdm = np.load("it_rdm.p", encoding="latin1")
    print(it_rdm)
    assert it_rdm.shape == (64, 64)


def test_hvm_it_rdm():
    loaded = np.load("it_rdm.p", encoding="latin1")

    assy_hvm = mkgu.get_assembly(name="HvMWithDiscfade")
    hvm_it_v6 = assy_hvm.sel(var="V6").sel(region="IT")
    hvm_it_v6.coords["cat_obj"] = hvm_it_v6.coords["category"] + hvm_it_v6.coords["obj"]
    hvm_it_v6_obj = hvm_it_v6.groupby("cat_obj").mean(dim="presentation").squeeze("time_bin").T

    assert hvm_it_v6_obj.shape == (64, 168)

    rdm_hvm = metrics.RDM()
    bmk_hvm = metrics.Benchmark(rdm_hvm, hvm_it_v6_obj)
    rdm = bmk_hvm.calculate()

    assert rdm.shape == (64, 64)
    assert rdm == approx(loaded, abs=1e-6)


def test_lookup():
    assy = fetch.get_lookup().lookup_assembly("HvM")
    assert assy.name == "HvM"
    store = assy.stores.values()[0]
    assert store.role == "HvM"
    assert store.store.type == "S3"
    assert store.store.location == "https://s3.amazonaws.com/mkgu-dicarlolab-hvm/hvm_neuronal_features.nc"




