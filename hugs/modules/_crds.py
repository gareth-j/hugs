# from _paths import RootPaths

class CRDS:
    """ Holds CRDS data within a set of Datasources

        Instances of CRDS should be created using the
        CRDS.create() function
        
    """
    _crds_root = "CRDS"

    def __init__(self):
        self._metadata = None
        self._uuid = None
        self._datasources = None
        self._start_datetime = None
        self._end_datetime = None

    def is_null(self):
        """ Check if this is a null object

            Returns:
                bool: True if object is null
        """
        return self._uuid is None

    @staticmethod
    def create(metadata, datasources, start_datetime, end_datetime):
        """ This function should be used to create CRDS objects

        """
        c = CRDS()

        c._metadata = metadata
        c._datasources = datasources
        c._start_datetime = start_datetime
        c._end_datetime = end_datetime

    @staticmethod
    def read_filelist(filelist):
        """ Returns a number of CRDS objects created from files

            Args:
                filelist (list): List of filenames
            Returns:
                list: List of CRDS objects
        """
        crds_list = []
        for filename in filelist:
            crds_list.append(CRDS.read_file(filename))

        return crds_list

    @staticmethod
    def read_file(filepath):
        """ Creates a CRDS object holding data stored within Datasources

            Args:
                filepath (str): Path of file to load
            Returns:
                CRDS: CRDS object containing data from file
        """
        from Acquire.ObjectStore import create_uuid as _create_uuid
        from Acquire.ObjectStore import get_datetime_now as _get_datetime_now
        from processing._metadata import Metadata as _Metadata
        from processing._segment import get_datasources as _get_datasources

        import pandas as _pd

        data = _pd.read_csv(filepath, header=None, skiprows=1, sep=r"\s+")     

        # Data will be contained within the Datasources
        datasources = _get_datasources(data)

        filename = filepath.split("/")[-1]
        # Get a Metadata object containing the processed metadata
        # Does this need to be an object? Just a dict?
        metadata = _Metadata.create(filename, data)

        c = CRDS()
        c._uuid = _create_uuid()
        c._creation_datetime = _get_datetime_now()
        c._datasources = datasources
        c._metadata = metadata

        # Ensure the CRDS object knows the datetimes it has
        c._start_datetime = datasources[0].get_start_datetime()
        c._end_datetime = datasources[0].get_end_datetime()

        return c

    
    def to_data(self):
        from Acquire.ObjectStore import datetime_to_string as _datetime_to_string

        datasource_uuids = {d._name: d._uuid for d in self._datasources}

        d = {}
        d["UUID"] = self._uuid
        d["creation_datetime"] = _datetime_to_string(self._creation_datetime)
        d["datasources"] = datasource_uuids
        d["metadata"] = self._metadata.data()
        d["data_start_datetime"] = _datetime_to_string(self._start_datetime)
        d["data_end_datetime"] = _datetime_to_string(self._end_datetime)

        return d

    @staticmethod
    def from_data(data, bucket=None):
        """ Create a CRDS object from data

            Args:
                data (str): JSON data
            Returns:
                CRDS: CRDS object created from data
        """
        from Acquire.ObjectStore import string_to_datetime as _string_to_datetime
        from modules._datasource import Datasource
        from objectstore._hugs_objstore import get_bucket as _get_bucket

        if data is None or len(data) == 0:
            return CRDS()

        if bucket is None:
            bucket = _get_bucket()
        
        c = CRDS()
        c._uuid = data["UUID"]
        c._creation_datetime = _string_to_datetime(data["creation_datetime"])

        datasource_uuids = data["datasources"]
        c._datasources = []

        # Load the Datasources associated with this object
        for _, uuid in datasource_uuids.items():
            c._datasources.append(Datasource.load(bucket=bucket, uuid=uuid))

        c._metadata = data["metadata"]
        c._start_datetime = _string_to_datetime(data["data_start_datetime"])
        c._end_datetime = _string_to_datetime(data["data_end_datetime"])

        return c

    def save(self, bucket=None):
        """ Save the object to the object store

            Args:
                bucket (dict, default=None): Bucket for data
            Returns:
                None
        """
        if self.is_null():
            return

        from Acquire.ObjectStore import ObjectStore as _ObjectStore
        from Acquire.ObjectStore import string_to_encoded as _string_to_encoded
        from objectstore._hugs_objstore import get_bucket as _get_bucket

        if bucket is None:
            bucket = _get_bucket()

        crds_key = "%s/uuid/%s" % (CRDS._crds_root, self._uuid)
        # Get the datasources to save themselves to the object store
        for d in self._datasources:
            d.save(bucket)

        _ObjectStore.set_object_from_json(bucket=bucket, key=crds_key, data=self.to_data())

    @staticmethod
    def load(uuid, bucket=None):
        """ Load a CRDS object from the datastore using the passed
            bucket and UUID

            Args:
                bucket (dict, default=None): Bucket to store object
                uuid (str, default=None): UID of Datasource
            Returns:
                Datasource: Datasource object created from JSON
        """
        from Acquire.ObjectStore import ObjectStore as _ObjectStore
        from modules._datasource import Datasource
        from objectstore._hugs_objstore import get_bucket as _get_bucket

        if bucket is None:
            bucket = _get_bucket()

        key = "%s/uuid/%s" % (CRDS._crds_root, uuid)

        data = _ObjectStore.get_object_from_json(bucket=bucket, key=key)

        return CRDS.from_data(data=data, bucket=bucket)


    @staticmethod
    def to_datetime(date_string):
        """ Convert a string of the format 2014-01-30
            to datetime

            TODO - make this more general

            Args:
                date_string (str): String of the format 2014-01-30
            Returns:
                Datetime: Datetime of string

        """
        import datetime as _datetime
        return _datetime.datetime.strptime("2014-01-30", "%Y-%m-%d")

    
    def get_daterange(self):
        """ Returns the daterange of the data in this object

            Returns:
                tuple (datetime, datetime): Start and end datetime
        """
        return self._start_datetime, self._end_datetime 

    def get_datasources(self):
        """ Return this object's Datasource

            Returns:
                list: List of datasources
        """
        return self._datasources

    def get_metadata(self):
        """ Get the metadata relating to this CRDS object

            Returns:
                dict: Metadata as dictionary
        """
        return self._metadata.data()

    def write_file(self, filename):
        """ Collects the data stored in this object and writes it
            to file at filename

            TODO - add control of daterange being written to file from
            data in Datasources

            Args:
                filename (str): Filename to write data to
            Returns:
                None
        """
        data = [] 

        return False
        # for datasource in self._datasources:
        #     # Get datas - for now just get the data that's there
        #     # Can either get the daterange here or in the Datasource.get_data fn
        #     data.append(datasource.get_data())

        #     for datetime in d.datetimes_in_data():
        #         datetimes[datetime] = 1
        
        # datetimes = list(datetimes.keys())

        # datetimes.sort()

        # with open(filename, "w") as FILE:
        #     FILE.write(metadata)
        #     # Merge the dataframes
        #     # If no data for that datetime set as NaN
        #     # Write these combined tables to the file