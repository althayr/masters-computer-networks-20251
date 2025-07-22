#!/bin/bash

# Note: Mininet must be run as root.  So invoke this shell script
# using sudo.

# Default Experiment time is 90s
time=30
bwhost=1000
bwnet=1.5
# TODO: If you want the RTT to be 20ms what should the delay on each
# link be?  Set this value correctly.
# RTT = 2 x transmission delay => transmission delay = 10ms
delay=0.01
cong='bbr'
dir=./

iperf_port=5001

for qsize in 20 100; do
    dir=bb-q$qsize

    # TODO: Run bufferbloat.py here...
    echo "running bufferbloat script"
    python3 bufferbloat.py \
        --bw-host $bwhost \
        --bw-net $bwnet \
        --delay $delay \
        --time $time \
        --maxq $qsize \
        --cong $cong \
        --dir $dir
    

    # TODO: Ensure the input file names match the ones you use in
    # bufferbloat.py script.  Also ensure the plot file names match
    # the required naming convention when submitting your tarball.
    echo "plotting queue and ping logs"
    python3 plot_queue.py -f $dir/q.txt -o $cong-buffer-q$qsize.png
    python3 plot_ping.py -f $dir/ping.txt -o $cong-rtt-q$qsize.png
    mn -c
done
