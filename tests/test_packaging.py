import pytest
from pathlib import Path
from brainio_base.assemblies import DataAssembly
from brainio_collection.packaging import write_netcdf

def test_write_netcdf():
    assy = DataAssembly([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18]],
                        coords={'up': ("a", ['alpha', 'alpha', 'beta', 'beta', 'beta', 'beta']),
                                'down': ("a", [1, 1, 1, 1, 2, 2]),
                                'sideways': ('b', ['x', 'y', 'z'])},
                        dims=['a', 'b'])
    netcdf_path = Path("test.nc")
    netcdf_sha1 = write_netcdf(assy, str(netcdf_path))
    assert netcdf_path.exists()
