""" Generic search functions that can be used to find data in
    the object store

"""
from enum import Enum

__all__ = [
    "get_data",
    "in_daterange",
    "key_to_daterange",
    "daterange_to_string",
    "daterange_to_string",
    "search",
    "lookup_gasDatasources",
    "lookup_footprintDatasources",
]


class RootPaths(Enum):
    DATA = "data"
    DATASOURCE = "datasource"
    INSTRUMENT = "instrument"
    SITE = "site"
    NETWORK = "network"


class DataType(Enum):
    CRDS = "CRDS"
    GC = "GC"
    FOOTPRINT = "FOOTPRINT"
    NOAA = "NOAA"
    EUROCOM = "EUROCOM"
    ThamesBarrier = "THAMESBARRIER"
    ICOS = "ICOS"


def search(
    species,
    locations,
    data_type,
    inlet=None,
    instrument=None,
    require_all=False,
    start_datetime=None,
    end_datetime=None,
):
    """ Search for gas data (optionally within a daterange)

        Args:
            species (str or list): Terms to search for in Datasources
            locations (str or list): Where to search for the terms in species
            inlet (str, default=None): Inlet height such as 100m
            instrument (str, default=None): Instrument name such as picarro
            require_all (bool, default=False): Require all search terms to be satisfied
            start_datetime (datetime, default=None): Start datetime for search
            If None a start datetime of UNIX epoch (1970-01-01) is set
            end_datetime (datetime, default=None): End datetime for search
            If None an end datetime of the current datetime is set
        Returns:
            dict: List of keys of Datasources matching the search parameters
    """
    from Acquire.ObjectStore import datetime_to_datetime
    from HUGS.ObjectStore import get_object_names
    from HUGS.ObjectStore import get_bucket
    from HUGS.Modules import Datasource
    from HUGS.Util import get_datetime_epoch
    from HUGS.Util import get_datetime_now
    from HUGS.Util import load_object

    from collections import defaultdict as defaultdict

    if not isinstance(species, list):
        species = [species]

    if not isinstance(locations, list):
        locations = [locations]

    if start_datetime is None:
        start_datetime = get_datetime_epoch()
    if end_datetime is None:
        end_datetime = get_datetime_now()

    # TODO - for now the latest dates people can access is the end of 2017
    # max_datetime = datetime_to_datetime(datetime(2017, 12, 31))
    # if end_datetime > max_datetime:
    #     end_datetime = max_datetime

    # Ensure passed datetimes are timezone aware
    start_datetime = datetime_to_datetime(start_datetime)
    end_datetime = datetime_to_datetime(end_datetime)

    bucket = get_bucket()

    # TODO - method to load different types in here for search
    # Maybe just an if else for now?
    # Get the objects that contain the Datasources
    # object_list = get_object_names(bucket=bucket, prefix=search_prefix)
    # object_uuid = object_list[0].split("/")[-1]

    # if len(object_list) == 0:
    #     raise ValueError("No " + data_type.name + " object found.")
    # if len(object_list) > 1:
    #     raise ValueError("More than one " + data_type.name + " object found.")

    # Load the required data object and get the datasource UUIDs required for metadata search
    data_type = DataType[data_type.upper()].name
    data_obj = load_object(class_name=data_type)
    datasource_uuids = data_obj.datasources()

    # TODO - implement lookup tables?
    # Shallow load the Datasources
    datasources = [Datasource.load(uuid=uuid, shallow=True) for uuid in datasource_uuids]

    # If inlet or instrument aren't passed we want to find the Datasource with the highest rank for
    # the passed daterange

    # If all search terms are required just use a single composite key of all search terms
    if require_all:
        single_key = "_".join(sorted(species))

    # First we find the Datasources from locations we want to narrow down our search
    location_sources = defaultdict(list)
    # If we have locations to search
    if locations is not None:
        for location in locations:
            for datasource in datasources:
                if datasource.search_metadata(location):
                    location_sources[location].append(datasource)
    # If we have an empty list of locations, search everywhere
    # TODO - this feels clunky
    else:
        for datasource in datasources:
            location_sources[datasource.site()].append(datasource)
    
    results = defaultdict(list)

    # If we have a specific inlet and instrument set just find that specific data and return it
    if inlet is not None and instrument is not None:
        matching = [d for d in location_sources if d.search_metadata(search_terms=[inlet, instrument], find_all=True)]

        in_date = []
        # Now we can just return this
        key = f"{site}_{species}_{instrument}_{inlet}"
        # Find the keys that match the correct data
        results[key] = 



        

    # elif data_type == "FOOTPRINT":
    #     footprints = []
    #     search_fn = datasource.search_metadata
    #     footprints = []
    #     for datasource in datasources:
    #         if datasource.search_metadata(data_type.lower()):
    # Return the metadata for each datasource with the results?
    # Display the additional metadata with each item
    # How to then differentiate between the
    # Take the values of the metadata keys and add them to the returned key to allow differentiation
    # between returned keys? This feels clunky but should be OK for now
    # Will get too long with lots of metadata

    # Instead of adding the values to the key retur the metadata dict?
    # Then we can parse that in the UI
    # OR just update the UI for selcetion of the type of data before searching and then
    # it creates a dictionary of search terms that can be parsed more easily by this function?
    # For now we can differentiate between inlets at least

    # Next we search these keys for the search terms we require
    # keys = defaultdict(dict)
    

    if data_type != "FOOTPRINT":
        if species is not None:
            for search_term in species:
                for location in location_sources:
                    for datasource in location_sources[location]:
                        if datasource.search_metadata(search_term):
                            # Get the latest version string from the Datasource
                            version_str = datasource.latest_version()
                            uuid = datasource.uuid()
                            
                            # Get all the keys that are prefixed with this string
                            prefix = f"data/uuid/{uuid}/{version_str}"
                            data_list = get_object_names(bucket=bucket, prefix=prefix)

                            # Get the keys to data in the correct daterange
                            in_date = [d for d in data_list if in_daterange(d, start_datetime, end_datetime)]

                            # Add the values of the metadata dictionary to the key for differentiation
                            key_addition = "_".join(
                                [
                                    v
                                    for k, v in datasource.metadata().items()
                                    if k == "inlet" or k == "height"
                                ]
                            )

                            if require_all:
                                search_key = f"{location}_{single_key}_{key_addition}"
                                remaining_terms = [
                                    datasource.search_metadata(term)
                                    for term in species
                                    if term != search_term
                                ]

                                if all(remaining_terms):
                                    results = append_keys(
                                        results=results,
                                        search_key=search_key,
                                        keys=in_date,
                                    )
                                    # Add the metadata from the Datasource to the results
                                    results[search_key]["metadata"] = datasource.metadata()
                                    # results[search_key].extend(in_date)
                            else:
                                search_key = f"{location}_{search_term}_{key_addition}"
                                results = append_keys(
                                    results=results, search_key=search_key, keys=in_date
                                )
                                results[search_key]["metadata"] = datasource.metadata()
                                # results[search_key].extend(in_date)
        # If we don't have any search terms, return everything that's in the correct daterange
        else:
            for location in location_sources:
                for datasource in location_sources[location]:
                    prefix = "data/uuid/%s" % datasource.uuid()
                    data_list = get_object_names(bucket=bucket, prefix=prefix)
                    in_date = [
                        d
                        for d in data_list
                        if in_daterange(d, start_datetime, end_datetime)
                    ]

                    key_addition = "_".join(
                        [
                            v
                            for k, v in datasource.metadata().items()
                            if k == "inlet" or k == "height"
                        ]
                    )

                    # TODO - currently adding in the species here, is this OK?
                    # key_addition = "_".join(datasource.metadata().values())
                    search_key = f"{location}_{datasource.species()}_{key_addition}"
                    results = append_keys(
                        results=results, search_key=search_key, keys=in_date
                    )
                    results[search_key]["metadata"] = datasource.metadata()
                    # results[search_key].extend(in_date)
    else:
        # For now get all footprints
        for datasource in datasources:
            if datasource.data_type() == "footprint":
                search_key = single_key
                prefix = "data/uuid/%s" % datasource.uuid()
                data_list = get_object_names(bucket=bucket, prefix=prefix)
                results = append_keys(
                    results=results, search_key=search_key, keys=data_list
                )
                results[search_key]["metadata"] = datasource.metadata()
                # results["footprints"].extend(data_list)
    # else:
    #     raise NotImplementedError("Only time series and footprint data can be searched for currently")

    # Here we can add the daterange key to the search results
    # TODO - can this just be taken more easily from the Datasource?
    for key in results:
        start, end = strip_dates_keys(keys=results[key]["keys"])
        results[key]["start_date"] = start
        results[key]["end_date"] = end

    return results


def strip_dates_keys(keys):
    """ Strips the date from a key, could this data just be read from JSON instead?
        Read dates covered from the Datasource?

        TODO - check if this is necessary - Datasource instead?

        Args:
            keys (list): List of keys containing data
            data/uuid/<uuid>/2014-01-30T10:52:30_2014-01-30T14:20:30'
        Returns:
            tuple (str,str): Start, end dates
    """
    if not isinstance(keys, list):
        keys = [keys]

    keys = sorted(keys)
    start_key = keys[0]
    end_key = keys[-1]
    # Get the first and last dates from the keys in the search results
    start_date = start_key.split("/")[-1].split("_")[0].replace("T", " ")
    end_date = end_key.split("/")[-1].split("_")[-1].replace("T", " ")

    return start_date, end_date


def append_keys(results, search_key, keys):
    """ defaultdict(list) behaviour for keys record

        If search_key exists in results the keys list is appended
        to the list stored at that key. Otherwise a new list containing
        the keys is created and stored at that key.

        Args:
            results (dict): Results dictionary
            search_key (str): Key to use to access results
            keys (list): List of object store keys to access
        Returns:
            dict: Results dictionary
    """
    if search_key in results:
        results[search_key]["keys"].extend(keys)
    else:
        results[search_key] = {"keys": keys}

    return results


def lookup_gasDatasources(lookup_dict, gas_data, source_name, source_id):
    """ Check if the passed data exists in the lookup dict

        Args:
            lookup_dict (dict): Dictionary to search for exisiting Datasources
            gas_data (list): Gas data to process
            source_name (str): Name of course
            source_id (str, default=None): UUID of source. Not currently implemented.
        Returns:
            dict: source_name: Datasource UUID (key: value)
    """
    # If we already have data from these datasources then return that UUID
    # otherwise return False
    if source_id is not None:
        raise NotImplementedError()

    results = {}
    for species in gas_data:
        datasource_name = source_name + "_" + species
        results[species] = {}
        results[species]["uuid"] = lookup_dict.get(datasource_name, False)
        results[species]["name"] = datasource_name

    return results


def lookup_footprintDatasources(lookup_dict, source_name, source_id=None):
    """ Check if we've had data from this Datasource before

        TODO - This seems like a waste - combine this with lookup_gasDatasources ?

        Args:
            lookup_dict (dict): Dictionary to search for exisiting Datasources
            source_name (str): Name of course
            source_id (str, default=None): UUID of source. Not currently implemented.
        Returns:
            dict: source_name: Datasource UUID (key: value)
    """
    if source_id is not None:
        raise NotImplementedError()

    results = {source_name: {}}
    results[source_name]["uuid"] = lookup_dict.get(source_name, False)

    return results


def get_data(key_list):
    """ Gets data from the Datasources found by the search function

        Bypass loading the Datasource? Get both then we have metadata?

    """
    from HUGS.Modules import Datasource as Datasource

    # Get the data
    # This will return a list of lists of data
    # Maybe want to do some preprocessing on this data before it comes raw out of the object store?
    # We only want the data in the correct daterange
    return [Datasource.load(key=key)._data for key in key_list]


def in_daterange(key, start_search, end_search):
    """ Does this key contain data in the daterange we want?

        Args:
            key (str): Key for data
            daterange (tuple (datetime, datetime)): Daterange as start and end datetime objects
        Return:
            bool: True if key within daterange
    """
    from Acquire.ObjectStore import string_to_datetime

    end_key = key.split("/")[-1]
    dates = end_key.split("_")

    if len(dates) > 2:
        raise ValueError("Invalid date string")

    start = string_to_datetime(dates[0])
    end = string_to_datetime(dates[1])

    if start_key >= start_search and end_key <= end_search:
        return True
    else:
        return False

def daterange_to_string(start, end):
    """ Creates a string from the start and end datetime
    objects. Used for production of the key
    to store segmented data in the object store.

    Args:
        start (datetime): Start datetime
        end (datetime): End datetime
    Returns:
        str: Daterange formatted as start_end
        YYYYMMDD_YYYYMMDD
        Example: 20190101_20190201
    """

    start_fmt = start.strftime("%Y%m%d")
    end_fmt = end.strftime("%Y%m%d")

    return start_fmt + "_" + end_fmt


# def get_objects(bucket, root_path, datetime_begin, datetime_end):
#     """ Get all values stored in the object store

#         Args:
#             bucket (dict): Bucket holding data
#             root_path (str): Select from the enum RootPaths
#             For DataSources: datasource
#             For Instruments: instrument etc
#             datetime_begin (datetime): Start of datetime range
#             datetime_end (datetime): End of datetime range
#         Returns:
#             list: A list of Pandas.Dataframes

#     """
#     from Acquire.ObjectStore import ObjectStore as _ObjectStore
#     from Acquire.ObjectStore import datetime_to_datetime as datetime_to_datetime
#     from objectstore._hugs_objstore import get_dataframe as _get_dataframe
#     from pandas import date_range as _pd_daterange

#     datetime_begin = datetime_to_datetime(datetime_begin)
#     datetime_end = datetime_to_datetime(datetime_end)

#     daterange = _pd_daterange(datetime_begin, datetime_end)

#     freq = "YS"
#     resolution = "%Y"
#     if start_datetime.month != 0 and end_datetime.month != 0:
#         resolution += "%m"
#         freq = "MS"
#     if start_datetime.day != 0 and end_datetime.day != 0:
#         resolution += "%d"
#         freq = "D"
#     if start_datetime.hour != 0 and end_datetime.hour != 0:
#         resolution += "%h"
#         freq = "H"

#     keys = []

#     path = RootPaths[root_path.upper()]

#     for date in daterange:
#         date_string = date.strftime(resolution)
#         prefix = "%s/%s/%s" % (path, uuid, date_string)

#         # datakeys =


#     # Find the keys that are valid
#     for year in range(year_begin, year_end+1):
#         prefix = "%s/%s/%s" % (path, self._uuid, year)

#         datakeys = _ObjectStore.get_all_object_names(bucket=bucket, prefix=prefix)

#         # Check the end date of the data
#         for datakey in datakeys:
#             _, end = string_to_daterange(datakey.split("_")[-1])

#             if end.year < year_end:
#                 keys.append(datakey)

#     # List to store dataframes
#     values = []

#     for key in keys:
#         values.append(_get_dataframe(bucket=bucket, key=key))

#     return values
