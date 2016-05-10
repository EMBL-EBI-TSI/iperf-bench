#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Launch IPerf client with a set of predefined parameters
# Can be used with cron to continuously query a server.
# Author: Dario Vianello (dario@ebi.ac.uk)
#
# Please remember to set the correct timezone on the server running this script.
# To add the cron job to the server use:
# (crontab -l ; echo "*/5 * * * * ~/iperf_client.py") | crontab -
# to add the crontab job to the server. Runs every 5 minutes.
# Keep in mind that if you're not using the default python env, you should come
# up with something like
# (crontab -l ; echo "*/5 * * * * /usr/local/bin/python2.7 ~/iperf_client.py") | crontab -
# to make it work.
###
import subprocess
import logging
import sys
import time
import os.path

IPERF_EXECUTABLE = "iperf3"
TEST_DURATION = 60  # In seconds
NUMBER_STREAMS = 30
IPERF_SERVER = "CHANGE_TO_IP"
JSON_OUTPUT = True
RESULTS_DIR = "iperf_results"
FILES_PREFIX = "CHANGE_TO_SUFFIX"
IPER_EXTRA_ARGS = []


def assemble_args(duration, streams, json, logfile, server, reverse=False, extra_args=[]):
    """ Assemble the right set of args to call iperf starting from vars """
    args = []
    args.extend(['-t', '{}'.format(duration)])
    args.extend(['-P', '{}'.format(streams)])
    if reverse:
        args.append('--reverse')
    if json:
        args.append('--json')
    args.extend(['--logfile', '{}'.format(logfile)])
    if extra_args:
        args.extend(extra_args)
    args.extend(['-c', '{}'.format(server)])
    return args


def launch_iperf(executable, args):
    """ Launch IPerf according to a set of given args"""
    iperf_command = [executable] + args
    iperf_retcode = subprocess.call(iperf_command)
    if iperf_retcode:
        logging.warning(
            "Something went wrong with the last Iperf test. Trying again...")
        iperf_retcode = subprocess.call(iperf_command)
        if iperf_retcode:
            logging.critical("IPerf failed twice. Bad news!")
            return False

    logging.info("IPerf command succeeded.")
    return True


# Check we're at least on Python 2.7
req_version = (2, 7)
cur_version = sys.version_info
if cur_version < req_version:
    logging.critical("This script requires at least Python 2.7!")
    sys.exit(1)

# Create directory to store results and logs
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

# Get unique timestamp to group everything together
timestamp = time.strftime("%Y%m%d_%H%M%S")

# Configure logging
log_file = FILES_PREFIX + timestamp + "_iperf_mon.log"
log_path = os.path.join(RESULTS_DIR, log_file)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filename=log_path)


# In this case, we need to execute two IPerf tests one after the other,
# sending data from from the server and the client, one at the time.
success_flag = 1
logging.info('Starting...')
logging.info('Launching first test, firing from client to server')
results_path = os.path.join(
    RESULTS_DIR, FILES_PREFIX + timestamp + "_client.json")
args = assemble_args(TEST_DURATION, NUMBER_STREAMS, True, results_path,
                     IPERF_SERVER, extra_args=IPER_EXTRA_ARGS)
if not launch_iperf(IPERF_EXECUTABLE, args):
    logging.critical("Client to server test failed (retcode != 0).")
    success_flag = 0
else:
    logging.info("Client to server test successfull.")

logging.info("Launching second test, firing from server to client")
results_path = os.path.join(
    RESULTS_DIR, FILES_PREFIX + timestamp + "_server.json")
args = assemble_args(TEST_DURATION, NUMBER_STREAMS, True, results_path,
                     IPERF_SERVER, reverse=True, extra_args=IPER_EXTRA_ARGS)
if not launch_iperf(IPERF_EXECUTABLE, args):
    logging.critical("Server to client test failed (retcode != 0).")
    success_flag = 0
else:
    logging.info("Server to client test successfull.")

if success_flag:
    logging.info("Test completed!")
else:
    logging.critical("Test completed with failures!")
