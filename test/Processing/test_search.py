import datetime
import os
import pytest
# import matplotlib.pyplot as plt

from HUGS.Modules import CRDS, GC, Footprint
from HUGS.Modules import Datasource
from HUGS.ObjectStore import get_local_bucket, get_object_names
from HUGS.Processing import in_daterange, key_to_daterange
from HUGS.Processing import recombine_sections, search
from HUGS.Util import get_datetime, load_object, get_datetime_epoch, get_datetime_now
                            

from Acquire.ObjectStore import datetime_to_string
from Acquire.ObjectStore import datetime_to_datetime

# Create the CRDS object
# @pytest.fixture(autouse=True)
# def create_crds():
#     # prepare something ahead 
#     crds = CRDS.create()
#     crds.save()


@pytest.fixture(scope="session")
def gc_obj():
    bucket = get_local_bucket(empty=True)
    data_file = "capegrim-medusa.18.C"
    prec_file = "capegrim-medusa.18.precisions.C"
    dir_path = os.path.dirname(__file__)
    test_data = "../data/proc_test_data/GC"
    data_filepath = os.path.join(dir_path, test_data, data_file)
    prec_filepath = os.path.join(dir_path, test_data, prec_file)

    GC.read_file(data_filepath=data_filepath, precision_filepath=prec_filepath, site="capegrim", source_name="capegrim-medusa.18", instrument_name="medusa")

@pytest.fixture(scope="session")
def crds_obj():
    filename = "bsd.picarro.1minute.248m.dat"
    dir_path = os.path.dirname(__file__)
    test_data = "../data/proc_test_data/CRDS"
    filepath = os.path.join(dir_path, test_data, filename)

    return CRDS.read_file(filepath, source_name="bsd.picarro.1minute.248m")

@pytest.fixture(scope="session")
def crds_read():
    bucket = get_local_bucket(empty=True)
    test_data = "../data/search_data"
    folder_path = os.path.join(os.path.dirname(__file__), test_data)
    CRDS.read_folder(folder_path=folder_path)

# @pytest.fixture(scope="session")
# def footprint_read():
#     test_data = "../data"
#     filename = "WAO-20magl_EUROPE_201306_downsampled.nc"
#     filepath = os.path.join(os.path.dirname(__file__), filename)
#     metadata = {"name": "WAO-20magl_EUROPE"}
#     Footprint.read_file(filepath=filepath, metadata=metadata)

def test_search_GC():
    search_terms = []
    locations = []
    data_type = "GC"
    start = None
    end = None

    bucket = get_local_bucket(empty=True)
    data_file = "capegrim-medusa.18.C"
    prec_file = "capegrim-medusa.18.precisions.C"
    dir_path = os.path.dirname(__file__)
    test_data = "../data/proc_test_data/GC"
    data_filepath = os.path.join(dir_path, test_data, data_file)
    prec_filepath = os.path.join(dir_path, test_data, prec_file)

    datasources = GC.read_file(data_filepath=data_filepath, precision_filepath=prec_filepath, site="capegrim", source_name="capegrim-medusa.18", instrument_name="medusa")

    results = search(search_terms=search_terms, locations=locations, data_type=data_type, require_all=False, 
                        start_datetime=start, end_datetime=end)

    assert results["capegrim_nf3"][0].split("/")[-1] == '2018-01-01T02:24:00_2018-01-31T23:33:00'

    assert "capegrim_nf3" in results
    assert "capegrim_cf4" in results
    assert "capegrim_pfc-116" in results
    assert "capegrim_pfc-218" in results
    assert "capegrim_pfc-318" in results
    assert "capegrim_c4f10" in results
    assert "capegrim_c6f14" in results
    assert "capegrim_sf6" in results
    assert "capegrim_so2f2" in results

    assert len(datasources) == 56

# def test_load_object(crds_obj):
#     bucket = get_local_bucket()
#     crds_obj.save(bucket)
#     uuid = crds_obj.uuid()
#     class_name = "crds"
#     obj = load_object(class_name=class_name)

#     assert isinstance(obj, CRDS)
#     assert obj.uuid() == crds_obj.uuid()


def test_location_search(crds_read):
    search_terms = ["co2", "ch4"]
    locations = ["bsd", "hfd", "tac"]

    data_type = "CRDS"
    start = None  # get_datetime(year=2016, month=1, day=1)
    end = None  # get_datetime(year=2017, month=1, day=1)

    results = search(search_terms=search_terms, locations=locations, data_type=data_type, require_all=False, 
                    start_datetime=start, end_datetime=end)

    assert "bsd_co2" in results
    assert "hfd_co2" in results
    assert "tac_co2" in results
    assert "bsd_ch4" in results
    assert "hfd_ch4" in results
    assert "tac_ch4" in results

    assert len(results["bsd_co2"]) == 6
    assert len(results["hfd_co2"]) == 7
    assert len(results["tac_co2"]) == 8
    assert len(results["bsd_ch4"]) == 6
    assert len(results["hfd_ch4"]) == 7
    assert len(results["tac_ch4"]) == 8

def test_search_no_search_terms(crds_read):
    data_type = "CRDS"
    search_terms = []
    locations = ["bsd"]

    results = search(search_terms=search_terms, locations=locations, data_type=data_type, require_all=False, 
                    start_datetime=None, end_datetime=None)

    assert len(results["bsd_ch4"]) == 6
    assert len(results["bsd_co2"]) == 6
    assert len(results["bsd_co"]) == 6

def test_search_no_locations(crds_read):
    data_type = "CRDS"
    search_terms = ["ch4"]
    locations = []

    results = search(search_terms=search_terms, locations=locations, data_type=data_type, require_all=False, 
                    start_datetime=None, end_datetime=None)

    assert len(results["bsd_ch4"]) == 6
    assert len(results["hfd_ch4"]) == 7
    assert len(results["tac_ch4"]) == 8

def test_search_datetimes():
    data_type = "CRDS"
    search_terms = ["co2"]
    locations = ["bsd"]

    start = get_datetime(year=2016, month=1, day=1)
    end = get_datetime(year=2017, month=1, day=1)

    results = search(search_terms=search_terms, locations=locations, data_type=data_type, require_all=False, 
                    start_datetime=start, end_datetime=end)

    assert results["bsd_co2"][0].split("/")[-1] == "2016-01-19T17:17:30_2016-12-31T23:52:30"

def test_search_require_all():
    data_type = "CRDS"
    search_terms = ["co2", "picarro", "108m"]
    locations = ["bsd"]

    start = get_datetime(year=2016, month=1, day=1)
    end = get_datetime(year=2017, month=1, day=1)

    results = search(search_terms=search_terms, locations=locations, data_type=data_type, require_all=True, 
                    start_datetime=start, end_datetime=end)

    assert len(results["bsd_108m_co2_picarro"]) == 3

def test_search_footprints():
    test_data = "../data"
    filename = "WAO-20magl_EUROPE_201306_downsampled.nc"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    metadata = {"name": "WAO-20magl_EUROPE"}
    Footprint.read_file(filepath=filepath, metadata=metadata)

    data_type = "footprint"
    search_terms = []
    locations = []

    start = get_datetime_epoch()
    end = get_datetime_now()

    results = search(search_terms=search_terms, locations=locations, data_type=data_type, 
                                                start_datetime=start, end_datetime=end)

    print(results)

    assert False













