# Continuous IPerf benchmarking
---

### IPerf testing
[IPerf](https://iperf.fr/) allows to test network bandwidth between a client and a server. However, testing networks only once usually doesn't provide enough information: links can be temporarily saturated by unexpected spikes in the traffic or undergoing maintenance. In these cases, single-shot results may not provide a clear picture of the infrastructure in place. **Continuous testing** over a fixed amount of time (where *time* is long enough, of course) is needed to derive meaningful figures and, thus, conclusions.  

This repo is composed by two separate script, which are mainly thin wrappers around IPerf.

---

### Requirements
The scripts require:
 - Python 2.7,  **no support for Python 3.**
 - Iperf, version 3.1 or higher

No external Python libraries are needed.

### Server side

On the host that needs to act as IPerf server, execute `iperf_server.py`. The script will take care of setting up logging, checking if IPerf is running, and spawning it
if necessary.

There's little to configure in this script (it's hardly doing anything interesting!), but you can find some global variables to change it's behavior, namely:

    IPERF_PID_FILE = "iperf.pid"              # Where to store IPerf pid
    IPERF_MONITOR_LOG = "iperf_monitor.log"   # Where to store the script logs
    IPERF_EXECUTABLE = "iperf3"               # IPerf Executable to use
    IPERF_ARGS = ["--pidfile", os.path.expanduser("~/" + IPERF_PID_FILE),
              "-s", "-D"]                     # Arguments to pass to IPerf

In this case, `IPERF_ARGS` is used to ask IPerf to:
  - `--pidfile` and `os.path.expanduser("~/" + IPERF_PID_FILE)`: create a pidfile at the given path
  - `-s`: act as a server
  - `-D`: enter daemon mode after lunch

Information on how to insert this script into cron can be found in the script itself. For reference, executing on a bash:
<p style="text-align: center;">`(crontab -l ; echo "*/1 * * * * ~/iperf_server.py") | crontab  - `</p>

would force cron to execute the script every minute, expecting the script to be in the user home (that's the default path for cron).


### Client side

Client side, execute `iperf_client.py`. In this case, the script will take care of spawning two IPerf tests one after the other, sending traffic from the client to the server first, and then from the server to the client.

Also in this case, global variables can be tuned to reflect different needs:

    IPERF_EXECUTABLE = "iperf3"               # IPerf executable to use
    TEST_DURATION = 60  # In seconds          # Single transfer duration (sec)
    NUMBER_STREAMS = 30                       # Number of concurrent streams
    IPERF_SERVER = "CHANGE_TO_IP"             # IP/ DNS name of the server
    JSON_OUTPUT = True                        # Output in JSON
    RESULTS_DIR = "iperf_results"             # Folder where to store results
    FILES_PREFIX = "CHANGE_TO_SUFFIX"         # Prefix for all produced files
    IPER_EXTRA_ARGS = []                      # Any additional argument to pass to
                                              # be passed to IPerf

Each result will be timestamped, to avoid filename collisions. Again, adding this script to cron is quite easy:
<p style="text-align: center;">`(crontab -l ; echo "*/5 * * * * ~/iperf_client.py") | crontab  - `</p>

With that invocation, cron will execute the test every five minutes, and the script will take care of storing the (JSON) results in the given folder. For sake of simplicity, the same timestamp will be used for both tests (client to server, server to client) even if there's roughly an offset of one minute between them. The real time of invocation can be extracted by the JSON logs directly, if needed.
