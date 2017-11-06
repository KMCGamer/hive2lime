#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Written by Kyle Carhart.

Description: Takes cases that have been resolved in The Hive within a specified
    interval and imports them to LimeSurvey as new responses. Users then go to
    the survey, input the case number and complete the survey.
"""
from ConfigParser import SafeConfigParser
from datetime import datetime
import logging
import time
import os
import urllib3
from hive2lime.hive import Hive
from hive2lime.lime import Lime
from hive2lime.mailclient import MailClient

def main():
    PARSER.read('./config/misc.ini')

    interval = PARSER.getint("script", "interval")
    current_milli_time = int(round(time.time() * 1000))
    interval_time_ago = current_milli_time - interval # time ago from the interval

    hive = Hive(debug=DEBUG)

    query = {
        "_and":[
            {
                "_string": "(status:\"Resolved\") AND endDate:[ {} TO * ]".format(0)
            }
        ]
    }

    # grab all the cases from hive that have been completed interval_time_ago
    cases = hive.search(query, "all", ["+caseId"])

    if cases:
        case_numbers = []
        for case in cases:
            case_numbers.append(str(case["caseId"]))
        if DEBUG:
            logging.debug("%s cases resolved: %s", len(cases), ", ".join(case_numbers))
    else:
        if DEBUG:
            logging.debug("No cases resolved today.")
            logging.info("Exiting successfully.")
        exit()

    PARSER.read('./config/lime.ini')
    tokens = {}
    for name, value in PARSER.items("tokens"):
        tokens[name] = value

    lime = Lime(debug=DEBUG)

    for case in cases:
        response = lime.create_json(case, tokens.get(case["updatedBy"], ""))
        srid = lime.add_response(response)
        lime.save_response(case["caseId"], srid)

    mailclient = MailClient(debug=DEBUG)
    mailclient.multisend(cases, tokens)
    lime.release_session()

if __name__ == "__main__":
    # change working environment so relative paths work. "./XXX/X.ini"
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    # get rid of annoying insecure warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Check if debugging is on.
    PARSER = SafeConfigParser()
    PARSER.read('./config/misc.ini')
    DEBUG = PARSER.getboolean("script", "debug")

    # configure the debugger to write logs.
    if DEBUG:
        logging.getLogger("urllib3").setLevel(logging.WARNING)

        DEBUG_STATE = str(datetime.fromtimestamp(int(round(time.time()))).strftime('%Y-%m-%d')) + '.txt'
        logging.basicConfig(
            filename="./log/{}".format(DEBUG_STATE),
            format='%(levelname)s:%(message)s',
            level=logging.DEBUG,
            filemode='w')
        logging.info("Starting.")

    try:
        main()
        if DEBUG:
            logging.info("Exiting successfully.")
    except (ValueError, TypeError, Exception) as e:
        if DEBUG:
            logging.error(e.message)
            logging.info("Exiting with error.")
