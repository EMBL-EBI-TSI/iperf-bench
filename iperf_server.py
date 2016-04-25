#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Launch IPerf server in daemon mode (requires Iperf 3.1 or above).
# Can be used with cron to continuously check daemon and respawn if necessary.
# Author: Dario Vianello (dario@ebi.ac.uk)
#
# Please remember to set the correct timezone on the server running this script.
# To add the cron job to the server use:
# (crontab -l ; echo "*/1 * * * * ~/iperf_server.py") | crontab -
# Runs every minute.
###
import subprocess
import logging
import sys
import time
import os.path


IPERF_PID_FILE = "iperf.pid"
IPERF_MONITOR_LOG = "iperf_monitor.log"
IPERF_EXECUTABLE = "iperf3"
IPERF_ARGS = ["--pidfile", os.path.expanduser("~/" + IPERF_PID_FILE),
              "-s", "-D"]


def check_pid(pid):
    """ Check for the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def launch_iperf(executable, args):
    """ Launch IPerf according to a set of given args"""
    iperf_command = [executable] + args
    iperf_command = subprocess.Popen(iperf_command)
    # We can't check any return code, as python fires-and-forgets and
    # the process enters daemon mode. We would always receive a None.


def check_iperf(pidfile):
    """ Check if pidfile exists, and if the process is alive """
    if os.path.isfile(pidfile):
        pid = int(open(pidfile).readline().strip("\x00"))
        if check_pid(pid):
            return True
        else:
            return False

    # If the file does not exits, return False
    return False

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filename=IPERF_MONITOR_LOG)


# MAIN
if check_iperf(IPERF_PID_FILE):
    logging.debug("IPerf is running.")
else:
    logging.warning("IPerf is not running. Spawning...")
    launch_iperf(IPERF_EXECUTABLE, IPERF_ARGS)

    # Wait for 1 second before checking if IPerf is running
    # Helps on slow systems.
    time.sleep(1)
    if check_iperf(IPERF_PID_FILE):
        logging.info("IPerf launched successfully!")
    else:
        logging.critical("Unable to launch IPerf correctly. Exiting...")
        sys.exit(1)
