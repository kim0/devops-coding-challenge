#!/usr/bin/env python3
# coding: utf-8
import requests
import datetime
import sys
import logging

if len(sys.argv) < 2:
    logging.critical("Must take URL to monitor as first argument! Usage: {0} URL".format(sys.argv[0]))
    sys.exit(2)

try:
    serverTimeRaw = requests.get(sys.argv[1]).content.decode("utf-8") 
except:
    print("Unexpected error reading time from service:", sys.exc_info()[0])
    raise

try:
    serverTime = datetime.datetime.fromisoformat(serverTimeRaw)
except:
    print("Unexpected error parsing time:", sys.exc_info()[0])
    raise

nowTime = datetime.datetime.utcnow()
secondsAbsDelta =  abs((serverTime - nowTime).total_seconds())

if secondsAbsDelta > 1:
    logging.warning("Time sync lost!")
    sys.exit(1)
else:
    logging.info("Time sync OK!") # Does not show by default. Depend only on exit status
