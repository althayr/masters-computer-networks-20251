from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser

from monitor import monitor_qlen

import sys
import os
import math

parser = ArgumentParser(description="Bufferbloat tests")
parser.add_argument('--bw-host', '-B',
                    type=float,
                    help="Bandwidth of host links (Mb/s)",
                    default=1000)

parser.add_argument('--bw-net', '-b',
                    type=float,
                    help="Bandwidth of bottleneck (network) link (Mb/s)",
                    required=True)

parser.add_argument('--delay',
                    type=float,
                    help="Link propagation delay (ms)",
                    required=True)

parser.add_argument('--dir', '-d',
                    help="Directory to store outputs",
                    required=True)

parser.add_argument('--time', '-t',
                    help="Duration (sec) to run the experiment",
                    type=int,
                    default=10)

parser.add_argument('--maxq',
                    type=int,
                    help="Max buffer size of network interface in packets",
                    default=100)

# Linux uses CUBIC-TCP by default that doesn't have the usual sawtooth
# behaviour.  For those who are curious, invoke this script with
# --cong cubic and see what happens...
# sysctl -a | grep cong should list some interesting parameters.
parser.add_argument('--cong',
                    help="Congestion control algorithm to use",
                    default="reno")

# Expt parameters
args = parser.parse_args()

class BBTopo(Topo):
    "Simple topology for bufferbloat experiment."
    
    def __init__(self, bw_host, bw_net, delay, maxq, *args, **kwargs):
        self.bw_host = bw_host
        self.bw_net = bw_net
        self.delay = delay
        self.maxq = maxq
        super().__init__(*args, **kwargs)

    def build(self):
        # TODO: create two hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        # Here I have created a switch.  If you change its name, its
        # interface names will change from s0-eth1 to newname-eth1.
        switch = self.addSwitch('s0')

        # TODO: Add links with appropriate characteristics
        self.addLink(h1, switch, cls=TCLink, bw=self.bw_host, delay=f'{self.delay}ms')
        self.addLink(switch, h2, cls=TCLink, bw=self.bw_net, delay=f'{self.delay}ms', max_queue_size=self.maxq)

# Simple wrappers around monitoring utilities.  You are welcome to
# contribute neatly written (using classes) monitoring scripts for
# Mininet!

def start_iperf(net):
    h1 = net.get('h1')
    h2 = net.get('h2')
    print("Starting iperf server...")
    # For those who are curious about the -w 16m parameter, it ensures
    # that the TCP flow is not receiver window limited.  If it is,
    # there is a chance that the router buffer may not get filled up.
    server = h2.popen("iperf -s -w 16m")

    # TODO: Start the iperf client on h1.  Ensure that you create a
    # long lived TCP flow.
    h2_ip = '10.0.0.2'
    transmission_duration = 300
    client = h1.popen('iperf -c {} -t {}'.format(h2_ip, transmission_duration))
    return client, server

def start_qmon(iface, interval_sec=0.1, outfile="q.txt"):
    print("Starting queue monitoring")
    monitor = Process(target=monitor_qlen,
                      args=(iface, interval_sec, outfile))
    monitor.start()
    return monitor

def start_ping(net, dir):
    # TODO: Start a ping train from h1 to h2 (or h2 to h1, does it
    # matter?)  Measure RTTs every 0.1 second.  Read the ping man page
    # to see how to do this.

    # Hint: Use host.popen(cmd, shell=True).  If you pass shell=True
    # to popen, you can redirect cmd's output using shell syntax.
    # i.e. ping ... > /path/to/ping.
    h1 = net.get('h1')
    h2_ip = '10.0.0.2'
    h1.popen('ping -i 0.1 {} > {}/ping.txt'.format(h2_ip, dir),
             shell=True)

def start_webserver(net):
    print("Starting webserver")
    h1 = net.get('h1')
    proc = h1.popen("python webserver.py", shell=True)
    sleep(1)
    return [proc]

def download_webpage(net):
    h2 = net.get('h2')
    result = h2.cmd('curl -o /dev/null -s -w %{time_total} http://10.0.0.1')
    return float(result.strip())

def bufferbloat():
    if not os.path.exists(args.dir):
        os.makedirs(args.dir)
    os.system("sysctl -w net.ipv4.tcp_congestion_control=%s" % args.cong)
    topo = BBTopo(args.bw_host, args.bw_net, args.delay, args.maxq)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    # This dumps the topology and how nodes are interconnected through
    # links.
    dumpNodeConnections(net.hosts)
    # This performs a basic all pairs ping test.
    net.pingAll()

    # TODO: Start monitoring the queue sizes.  Since the switch I
    # created is "s0", I monitor one of the interfaces.  Which
    # interface?  The interface numbering starts with 1 and increases.
    # Depending on the order you add links to your network, this
    # number may be 1 or 2.  Ensure you use the correct number.
    qmon = start_qmon(iface='s0-eth2',
                      outfile='%s/q.txt' % (args.dir))

    # TODO: Start iperf, webservers, etc.
    start_iperf(net)
    start_webserver(net)
    start_ping(net, args.dir)
    

    # TODO: measure the time it takes to complete webpage transfer
    # from h1 to h2 (say) 3 times.  Hint: check what the following
    # command does: curl -o /dev/null -s -w %{time_total} google.com
    # Now use the curl command to fetch webpage from the webserver you
    # spawned on host h1 (not from google!)
    # Hint: Verify the url by running your curl command without the
    # flags. The html webpage should be returned as the response.

    # Hint: have a separate function to do this and you may find the
    # loop below useful.
    fetch_times = []
    start_time = time()
    while True:
        # do the measurement (say) 3 times.
        try:
            fetch_time = download_webpage(net)
            fetch_times.append(fetch_time)
            print(f"Webpage fetch time: {fetch_time:.3f}s")
        except:
            print("Failed to fetch webpage")
        
        sleep(5)
        now = time()
        delta = now - start_time
        if delta > args.time:
            break
        print("%.1fs left..." % (args.time - delta))

    # TODO: compute average (and standard deviation) of the fetch
    # times.  You don't need to plot them.  Just note it in your
    if fetch_times:
        avg_time = sum(fetch_times) / len(fetch_times)
        if len(fetch_times) > 1:
            variance = sum((t - avg_time) ** 2 for t in fetch_times) / (len(fetch_times) - 1)
            std_dev = variance ** 0.5
        else:
            std_dev = 0
        print(f"Webpage fetch statistics: avg={avg_time:.3f}s, std={std_dev:.3f}s, samples={len(fetch_times)}")
    else:
        print("No successful webpage fetches")
    # README and explain.

    # Hint: The command below invokes a CLI which you can use to
    # debug.  It allows you to run arbitrary commands inside your
    # emulated hosts h1 and h2.
    # CLI(net)

    qmon.terminate()
    net.stop()
    # Ensure that all processes you create within Mininet are killed.
    # Sometimes they require manual killing.
    Popen("pgrep -f webserver.py | xargs kill -9", shell=True).wait()

if __name__ == "__main__":
    bufferbloat()
