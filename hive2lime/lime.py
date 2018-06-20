from ConfigParser import SafeConfigParser
from datetime import datetime
import json
import logging
import hashlib
import time
import requests
import pymysql
import base64


class Lime:

    def __init__(self, debug=False):
        parser = SafeConfigParser()
        parser.read('./config/lime.ini')

        self.url = parser.get("misc", "url")
        self.sid = parser.get("misc", "sid")
        self.debug = debug

        self.sessionkey = self.create_session(parser.get("admin_panel", "user"),
                                              parser.get("admin_panel", "password"))
        self.sql = {"user": parser.get('mysql', 'user'),
                    "password": parser.get('mysql', 'password'),
                    "db": parser.get('mysql', 'database')}

    def create_session(self, user, password):
        """ Creates a limesurvey api session from a username and password.

        Args:
            lime_api (dict): contains information like user, pass, surveyid, etc.

        Returns:
            A string containing a valid session key.

        Raises:
            ValueError: if the response comes back unsuccessful.
        """
        url = self.url + "/admin/remotecontrol"
        headers = {
            "content-type": "application/json",
            "connection": "Keep-Alive"
        }
        data = {
            "id": 1,
            "method": "get_session_key",
            "params": {
                "username": user,
                "password": password
            },
        }

        data = json.dumps(data)
        request = requests.post(url, data=data, headers=headers, verify=False)

        if request.status_code == 200:
            if self.debug:
                logging.debug("Lime session created.")
            return request.json()["result"]
        else:
            raise ValueError(
                "create_session: Response was: {}.".format(request.status_code))

    def release_session(self):
        """ Ends the api session by releasing the session_key.

        Args:
            lime_api (dict): contains information like user, pass, surveyid, etc.

        Returns:
            The string of the result. If the string is "OK", the method was successful.

        Raises:
            ValueError: if the response comes back unsuccessful.
        """
        url = self.url + "/admin/remotecontrol"
        headers = {
            "content-type": "application/json",
            "connection": "Keep-Alive"
        }
        data = {
            "method": "release_session_key",
            "params": [self.sessionkey],
            "id": 1
        }
        data = json.dumps(data)

        request = requests.post(url, data=data, headers=headers, verify=False)

        if request.status_code == 200 and request.json()["result"] == "OK":
            if self.debug:
                logging.debug("Lime session released.")
        else:
            raise ValueError(
                "release_session: Response was: {}.".format(request.status_code))

    def add_response(self, response_data):
        """ Adds a response to the specified survey_id with data from response_data.

        Args:
            lime_api (dict): contains information like user, pass, surveyid, etc.
            response_data (dict): a dictionary where the keys are mysql table names
            and the values are their corresponding values for the case.

        Returns:
            srid (int): if the response addition is successful, the function will
            return the "survey response id" of the newly created survey response.

        Raises:
            ValueError: if the response was not 200.
            TypeError: if the return value of the request was not an srid (int).

        """

        url = self.url + "/admin/remotecontrol"
        headers = {
            "content-type": "application/json",
            "connection": "Keep-Alive"
        }
        data = json.dumps({
            "method": "add_response",
            "params": [self.sessionkey, self.sid, response_data],
            "id": 1
        })

        request = requests.post(url, data=data, headers=headers, verify=False)

        if request.status_code == 200:
            srid = request.json()['result']
            if self.debug:
                logging.debug("Lime response added. SRID: %s", srid)
            return srid  # returns the srid of the new response
        else:
            raise ValueError(
                "add_response: response was: {}.".format(request.status_code))

    @staticmethod
    def create_json(case, token):
        return {
            # token that represents who the case belongs to
            # "token": self.tokens.get(case["updatedBy"], ""),
            "token": token,
            # Survey response submission date.
            "submitdate": "",
            # Hive reference id.
            "386328X14X651": case['caseId'],
            # When did you start your investigation?
            "386328X14X646": datetime.fromtimestamp(int(case['startDate'] / 1000)).strftime('%Y-%m-%d'),
            # Time to compromise to discovery
            "386328X15X916other": case['metrics'].get('Dwell Time', ""),
            # Time from open to close
            "386328X15X905": case['metrics'].get("Close Time", ""),
            # Time worked.
            "386328X15X904": case['metrics'].get('Time Worked', "")
        }

    def save_response(self, caseid, srid):
        """ Manually enter response data into lime_saved_control in mysql.

        In order to make a response accessible after being created, data must be
        entered into survey_x (from lime_add_response()) but also
        into lime_saved_control.This makes it so that you can resume a survey
        response by giving a "saved name" and password.

        Args:
            case (dict): case information returned from hive_search().
            lime_api (dict): contains information like user, pass, surveyid, etc.
            survey_response_id (int): the id of the actual survey response to
                connect the saved response to.

        """
        connection = pymysql.connect(host='localhost',
                                     user=self.sql['user'],
                                     password=self.sql['password'],
                                     db=self.sql['db'])

        identifier = caseid
        access_code = hashlib.sha256(str.encode(str(identifier))).hexdigest()
        email = ""
        ip = ""
        saved_thisstep = 1
        status = "S"
        saved_date = datetime.fromtimestamp(
            int(round(time.time()))).strftime('%Y-%m-%d %H:%M:%S')
        refurl = ""

        try:
            with connection.cursor() as cursor:
                query = "INSERT INTO `lime_saved_control` (`sid`,`srid`,`identifier`,`access_code`,`email`,`ip`,`saved_thisstep`,`status`,`saved_date`,`refurl`) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
                    self.sid, srid, identifier, access_code, email, ip, saved_thisstep, status, saved_date, refurl)
                cursor.execute(query)
                connection.commit()
            if self.debug:
                logging.debug(
                    "Mysql database entry completed for srid: %s", srid)
        finally:
            connection.close()

    def export_responses(self):
        url = self.url + "/admin/remotecontrol"

        headers = {
            "content-type": "application/json",
            "connection": "Keep-Alive"
        }

        data = json.dumps({
            "method": "export_responses",
            "params": [self.sessionkey,
                       self.sid,
                       'json',
                       'en',
                       'incomplete',
                       'code',
                       'short',
                       '', '',
                       ['token', '386328X14X651']],
            "id": 1
        })

        request = requests.post(url, data=data, headers=headers, verify=False)

        if request.status_code == 200:
            return json.loads(base64.decodestring(json.loads(request.text)['result']))['responses']
        else:
            raise ValueError(
                "export_responses: response was: {}.".format(request.status_code))
