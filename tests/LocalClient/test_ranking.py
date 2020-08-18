import os
import pytest
from HUGS.LocalClient import RankSources
from HUGS.Modules import CRDS
from HUGS.ObjectStore import get_local_bucket


# Ensure we have something to rank
@pytest.fixture(scope="session", autouse=True)
def crds():
    get_local_bucket(empty=True)
    dir_path = os.path.dirname(__file__)
    test_data = "../data/proc_test_data/CRDS"
    filename = "hfd.picarro.1minute.100m.min.dat"
    filepath = os.path.join(dir_path, test_data, filename)

    CRDS.read_file(data_filepath=filepath, source_name="hfd_picarro_100m", site="hfd")


def test_ranking(crds):
    r = RankSources()

    results = r.get_sources(site="hfd", species="co2", data_type="CRDS")

    hundred_uuid = results["co2_hfd_100m_picarro"]["uuid"]

    del results["co2_hfd_100m_picarro"]["uuid"]

    expected_results = {'co2_hfd_100m_picarro': {'rank': 0, 'data_range': '2013-12-04T14:02:30_2019-05-21T15:46:30'}}

    assert results == expected_results

    rank_daterange = r.create_daterange(start="2013-12-04", end="2016-05-05")

    updated = {'co2_hfd_100m_picarro': {'rank': {1: [rank_daterange]}, 'data_range': '2013-12-04T14:02:30_2019-05-21T15:46:30', 
                        "uuid": hundred_uuid}}

    r.rank_sources(updated_rankings=updated, data_type="CRDS")

    results = r.get_sources(site="hfd", species="co2", data_type="CRDS")

    del results["co2_hfd_100m_picarro"]["uuid"]

    assert results == {'co2_hfd_100m_picarro': {'rank': {'1': ['2013-12-04T00:00:00_2016-05-05T00:00:00']}, 
                        'data_range': '2013-12-04T14:02:30_2019-05-21T15:46:30'}}