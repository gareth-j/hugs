""" Handles the recombination of dataframes stored in the object store
    into the data requested by the user

"""
def get_datasources(bucket, uuid_list):
    """ Get the Datasources containing the data from the object 
        store for recombination of data

        Args:
            key_list (list): List of keys for data in the object store
        Returns:
            list: List of Datasource objects
    """
    from modules._datasource import Datasource
    from objectstore._hugs_objstore import get_object as _get_object_json

    return [Datasource.load(bucket=bucket, uuid=uid) for uid in uuid_list]


# This might be unnecessary
def get_dataframes(datasources):
    """ Get the data from the Datasources and return the dataframes

        Args:
            datasources (list): List of datasources
        Returns:
            list: List of Pandas.Dataframes
    """
    x = [datasource._data for datasource in datasources]

    return False


def combine_sections(sections):
    """ Combines separate dataframes into a single dataframe for
        processing to NetCDF for output

        TODO - An order for recombination of sections

        Args:
            sections (list): List of list of dataframes for each segment 
            for recombination
        Returns:
            Pandas.Dataframe: Combined dataframes
    """
    import pandas as _pd

    combined = []
    # Combine the dataframes and create a frame of their indices
    for section in sections:
        combo = _pd.concat(section, axis="rows")
        combined.append(combo)

    complete = combined[0].iloc[:, :1]

    for d in combined:
        if len(d.index) != len(complete.index):
            raise ValueError("Mismatch in timeframe and dataframes index length")
        complete = _pd.concat([complete, d], axis="columns")

    return complete


def convert_to_netcdf(dataframe):
    """ Converts the passed dataframe to netcdf, performs checks
        and returns

        TODO - in memory return of a NetCDF file as a bytes object

        Args:
            dataframe (Pandas.Dataframe): Dataframe for convesion
        Returns:
            str: Name of file written
    """
    from Acquire.ObjectStore import get_datetime_now_to_string as _get_datetime_now_to_string
    import xarray

    filename = "crds_output_%s.nc" % _get_datetime_now_to_string()

    ds = dataframe.to_xarray().to_netcdf(filename)

    return filename

