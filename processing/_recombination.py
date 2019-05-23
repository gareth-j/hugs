""" Handles the recombination of dataframes stored in the object store
    into the data requested by the user

"""
def get_sections(bucket, uuid_list):
    """ Get the Datasources containing the data from the object 
        store for recombination of data

        WIP

        Args:
            uuid_list (list): List of keys for data in the object store
        Returns:
            list: List of Datasource objects
    """
    from modules._datasource import Datasource
    from objectstore.hugs_objstore import get_object as _get_object_json

    # TODO - the same 3 dataframes are being returned each time - fix this
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



def combine_sections(dataframes):
    """ Combines separate dataframes into a single dataframe for
        processing to NetCDF for output

        TODO - An order for recombination of sections

        Args:
            dataframes (list): List of dataframes for recombination
        Returns:
            Pandas.Dataframe: Combined dataframes
    """
    import pandas as _pd

    # Check that the the first dataframe is a timeframe
    # if dataframes[0]
    # Get the first column for timeframe comparison
    timeframe = dataframes[0].iloc[:, :1]
    
    for d in dataframes:
        if len(d.index) != len(timeframe.index):
            raise ValueError("Mismatch in timeframe and dataframes index length")
        # Drop the time column
        d.drop(columns="Datetime", axis="columns", inplace=True)
        timeframe = _pd.concat([timeframe, d], axis=1)

    return timeframe

def convert_to_netcdf(dataframe):
    """ Converts the passed dataframe to netcdf, performs checks
        and returns

        Args:
            dataframe (Pandas.Dataframe): Dataframe for convesion
        Returns:
            bytes: NetCDF file as a bytes array
    """
    # from netCDF4 import Dataset as _Dataset

    # Get bytes array version of Pandas dataframe

    pass

    # Dataset('inmemory.nc', diskless=True, mode='w')

    # _Dataset.to_netcdf

    

    

    



        