import logging
import requests
from ConfigParser import SafeConfigParser

class Hive:

    def __init__(self, debug=False):
        parser = SafeConfigParser()
        parser.read('./config/hive.ini')

        self.url = parser.get("hive", "url")
        self.auth = requests.auth.HTTPBasicAuth(username=parser.get("hive", "user"),
                                                password=parser.get("hive", "password"))
        self.debug = debug

    def search(self, query, scope="all", sort=[]):
        """ Sends a query to thehive to retrieve matching cases.

        Args:
            query (dict): the query you want to perform which will be sent as JSON.
            scope (array): the range for how many values you want (ex: "1-10").
            sort (array): how you would like the results sorted (ex: ["+caseId"]).

        Returns:
            A dict of cases that match the query.

        Raises:
            ValueError: if the response comes back unsuccessful.

        """

        req = self.url + "/api/case/_search"
        params = {
            "range": scope,
            "sort": sort
        }
        data = {
            "query": query
        }
        request = requests.post(req, json=data, auth=self.auth, params=params, verify=False)

        if request.status_code == 200:
            if self.debug:
                logging.debug("Query sent to TheHive.")
            return Hive.__filter_cases(request.json())
        else:
            raise ValueError("Reponse status code: {}".format(request.status_code))

    @staticmethod
    def __filter_cases(cases):
        # filter out any cases created by the api
        cases = [case for case in cases if case["createdBy"] != "api"]
        # filter out any cases that have the tag "class:ediscovery"
        cases = [case for case in cases if "class:ediscovery" not in case["tags"]]
        # filter out false positives
        cases = [case for case in cases if case["resolutionStatus"] != "FalsePositive"]
        # filter out nonir
        cases = [case for case in cases if "nonir" not in case["tags"]]
        return cases
