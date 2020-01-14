from HUGS.Modules import BaseModule

__all__ = ["ICOS"]

### To use this template replace:
# - ICOS with new data name in all upper case e.g. CRDS
# - template with new data name in all lower case e.g. crds
# - CHANGEME with a new fixed uuid (at the moment)

class ICOS(BaseModule):
    """ Interface for processing ICOS data
        
    """
    _root = "ICOS"
    _uuid = "3b8e169b-ea1a-4744-9b63-12a8eedd2281"

    def __init__(self):
        from Acquire.ObjectStore import get_datetime_now
        
        self._creation_datetime = get_datetime_now()
        self._stored = False
        # self._datasources = []
        # Keyed by name - allows retrieval of UUID from name
        self._datasource_names = {}
        # Keyed by UUID - allows retrieval of name by UUID
        self._datasource_uuids = {}
        # Hashes of previously uploaded files
        self._file_hashes = {}
        # Holds parameters used for writing attributes to Datasets
        self._template_params = {}
        # Sampling period of ICOS data in seconds
        self._sampling_period = "NA"

    def to_data(self):
        """ Return a JSON-serialisable dictionary of object
            for storage in object store

            Returns:
                dict: Dictionary version of object
        """
        from Acquire.ObjectStore import datetime_to_string

        data = {}
        data["creation_datetime"] = datetime_to_string(self._creation_datetime)
        data["stored"] = self._stored
        data["datasource_uuids"] = self._datasource_uuids
        data["datasource_names"] = self._datasource_names
        data["file_hashes"] = self._file_hashes

        return data

    def save(self, bucket=None):
        """ Save the object to the object store

            Args:
                bucket (dict, default=None): Bucket for data
            Returns:
                None
        """
        from Acquire.ObjectStore import ObjectStore, string_to_encoded
        from HUGS.ObjectStore import get_bucket

        if bucket is None:
            bucket = get_bucket()

        key = f"{ICOS._root}/uuid/{ICOS._uuid}"

        self._stored = True
        ObjectStore.set_object_from_json(bucket=bucket, key=key, data=self.to_data())

    @staticmethod
    def read_folder(folder_path, extension=".dat", recursive=True):
        """ Read all data matching filter in folder

            Args:
                folder_path (str): Path of folder
                extension (str, default=".dat"): File extension for data files in folder
                recursive (bool, default=True)
            Returns:
                None
        """
        from glob import glob
        from os import path

        datasource_uuids = {}

        # This finds data files in sub-folders
        folder_path = path.join(folder_path, f"./*.{extension}")
        # This finds files in the current folder, get recursive
        # folder_path = _path.join(folder_path, "*.dat")
        filepaths = glob(folder_path, recursive=recursive)

        if not filepaths:
            raise FileNotFoundError("No data files found")

        for fp in filepaths:
            datasource_uuids[fp] = ICOS.read_file(data_filepath=fp)
        
        return datasource_uuids
             
    @staticmethod
    def read_file(data_filepath, source_name, site=None, source_id=None, overwrite=False):
        """ Reads ICOS data files and returns the UUIDS of the Datasources
            the processed data has been assigned to

            Args:
                filepath (str or Path): Path of file to load
            Returns:
                list: UUIDs of Datasources data has been assigned to
        """
        from HUGS.Processing import assign_data, lookup_gas_datasources
        from HUGS.Util import hash_file
        from pathlib import Path
        import os

        template = ICOS.load()

        # Check if the file has been uploaded already
        file_hash = hash_file(filepath=data_filepath)
        if file_hash in template._file_hashes and not overwrite:
            raise ValueError(f"This file has been uploaded previously with the filename : {template._file_hashes[file_hash]}")
        
        data_filepath = Path(data_filepath)
        filename = data_filepath.name

        if not source_name:
            source_name = filename.stem

        if not site:
            site = source_name.split(".")[0]

        # This should return xarray Datasets
        gas_data = template.read_data(data_filepath=data_filepath, site=site)

        # Assign attributes to the xarray Datasets here data here makes it a lot easier to test
        gas_data = template.assign_attributes(data=gas_data, site=site)

        # Check if we've got data from these sources before
        lookup_results = lookup_gas_datasources(lookup_dict=template._datasource_names, gas_data=gas_data, 
                                                source_name=source_name, source_id=source_id)

        # Assign the data to the correct datasources
        datasource_uuids = assign_data(gas_data=gas_data, lookup_results=lookup_results, overwrite=overwrite)

        # Add the Datasources to the list of datasources associated with this object
        template.add_datasources(datasource_uuids)

        # Store the hash as the key for easy searching, store the filename as well for
        # ease of checking by user
        template._file_hashes[file_hash] = filename

        template.save()

        return datasource_uuids

    def read_data(self, data_filepath, species, site=None):
        """ Separates the gases stored in the dataframe in 
            separate dataframes and returns a dictionary of gases
            with an assigned UUID as gas:UUID and a list of the processed
            dataframes

            # TODO - update this to process multiple species here?

            Args:
                data_filepath (pathlib.Path): Path of datafile
                species (str): Species to process
            Returns:
                dict: Dictionary containing attributes, data and metadata keys
        """
        from pandas import RangeIndex, concat, read_csv, datetime, NaT, Timestamp
        from HUGS.Processing import get_attributes, read_metadata
        from HUGS.Util import read_header

        # metadata = read_metadata(filepath=data_filepath, data=data, data_type="ICOS")
        header = read_header(filepath=data_filepath)
        n_skip = len(header)-1

        def parse_date(date):
            try:
                return pd_datetime.strptime(date, "%Y %m %d %H %M")
            except ValueError:
                return NaT

        datetime_columns = {"time": ["Year", "Month", "Day", "Hour", "Minute"]}
        use_cols = ["Day", "Month", "Year", "Hour", "Minute", str(species.lower()), "SamplingHeight", "Stdev", "NbPoints"]
        
        dtypes = {"Day": np.int,
                  "Month": np.int,
                  "Year": np.int,
                  "Hour": np.int,
                  "Minute": np.int,
                  species.lower(): np.float,
                  "Stdev": np.float,
                  "SamplingHeight": np.float,
                  "NbPoints": np.int}

        data = read_csv(data_filepath, skiprows=n_skip, parse_dates=datetime_columns, index_col="time", 
                        usecols=use_cols, dtype=dtypes, na_values="-999.99")

        data = data[data[species.lower()] >= 0.0]

        # Drop duplicate indices
        data = data.loc[~data.index.duplicated(keep='first')]

        # Check if the index is sorted
        if not data.index.is_monotonic_increasing:
            data.sort_index()

        # Rename columns
        rename_dict = {species.lower(): species.upper(),
                        "Stdev": species.upper() + " variability",
                        "NbPoints": species.upper() + " number_of_observations"}

        data = data.rename(columns=rename_dict)



