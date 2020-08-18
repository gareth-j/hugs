__all__ = ["RankSources"]

import copy
from Acquire.Client import Wallet


class RankSources:
    """
    This class is used to select the primary datasources for species from different sites
    """
    def __init__(self, service_url=None):
        wallet = Wallet()

        if service_url is None:
            service_url = "https://hugs.acquire-aaai.com/t"

        self._service = wallet.get_service(service_url=f"{service_url}/hugs")

        self._before_ranking = {}

    def get_sources(self, site, species, data_type):
        """ Get the datasources for this site and species to allow a ranking to be set

            Args:
                site (str): Three letter site code
                species (str): Species name
                data_type (str): Must be valid datatype i.e. CRDS, GC
                See all valid datasources in the DataTypes class
            Returns:
                dict: Dictionary of datasource metadata
        """
        from HUGS.Util import valid_site

        if self._service is None:
            raise PermissionError("Cannot use a null service")

        if len(site) != 3 or not valid_site(site):
            # raise InvalidSiteError(f"{site} is not a valid site code")
            raise ValueError(f"{site} is not a valid site code")

        args = {"site": site, "species": species, "data_type": data_type}

        response = self._service.call_function(function="get_sources", args=args)

        self._before_ranking = copy.deepcopy(response)

        self._key_uuids = {key: response[key]["uuid"] for key in response}

        return response

    def rank_simply(self, key, start_date, end_date, data_type):
        """ Simply y

            Args:
                key (str): Key such as co_bsd_248m
                start_date (str): Start date
                end_date ()
            Returns:
                None
        """
        pass

    def rank_sources(self, updated_rankings, data_type):
        """ Assign the precendence of sources for each.
            This function expects a dictionary of the form

            This function expects a dictionary of the form

            {'site_string': {'rank': [daterange_str, ...], 'daterange': 'start_end', 'uuid': uuid}, 

            Args:
                updated_ranking (dict): Dictionary of ranking
            Returns:
                None
        """
        if updated_rankings == self._before_ranking:
            return

        args = {"ranking": updated_rankings, "data_type": data_type}

        self._service.call_function(function="rank_sources", args=args)

    def create_daterange(self, start, end):
        """ Create a JSON serialisable daterange string for use in ranking dict

            Args:
                start (datetime): Start of daterange
                end (datetime): End of daterange
            Returns:
                str: Serialisable daterange string
        """
        from Acquire.ObjectStore import datetime_to_string
        from pandas import Timestamp

        if isinstance(start, str) and isinstance(end, str):
            start = Timestamp(start).to_pydatetime()
            end = Timestamp(end).to_pydatetime()

        return "".join([datetime_to_string(start), "_", datetime_to_string(end)])
