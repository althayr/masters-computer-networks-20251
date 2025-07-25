## Overview

This repo contains a study about the bufferbloat phenomenon done for the Masters class in Computer Networks at Federal University of Rio de Janeiro (UFRJ) in the first semester of 2025.


## Dependencies

- [vagrant](https://www.vagrantup.com/downloads) for VM configuration. I chose to run vagrant together with [virtualbox](https://www.virtualbox.org/wiki/Downloads), if there is a mismatch between your linux kernel version and the boxes available on VirtualBox you may need to install the dkms version.

## How to run

- From the root of this repo run `git clone https://github.com/skywardpixel/mininet-vagrant`.
- `cd mininet-vagrant && vagrant up` to boot up and setup the VM we'll be working with.
- `vagrant plugin install vagrant-scp` to install scp.

Now we need to copy the script files to the VM and run it:

- `vagrant scp ../bufferbloat :/home/vagrant/bufferbloat`.
- `vagrant ssh` to attach to the VM.

Once attached we need to setup the VM system dependencies:

- `$sudo apt install wireshark -y` to install wireshark.
- `$nohup sudo wireshark > wireshark.log &` to start wireshark in the background.
- `$sudo apt install python3-pip -y && sudo python3 -m pip install mininet matplotlib` to install python3 and it's dependencies in the VM. 

Running the experiments

- `$cd bufferbloat && sudo bash run.sh`

Logout from the ssh connection and copy the logged files to host machine

- `vagrant scp ../bufferbloat :/home/vagrant`

TCP Reno experiments

```bash
rm -rf bb-q20-reno bb-q100-reno && \
vagrant scp :~/bufferbloat/bb-q20 ./bb-q20-reno
vagrant scp :~/bufferbloat/bb-q100 ./bb-q100-reno
vagrant scp :~/bufferbloat/reno-buffer-q20.png ./reno-buffer-q20.png
vagrant scp :~/bufferbloat/reno-buffer-q100.png ./reno-buffer-q100.png
vagrant scp :~/bufferbloat/reno-rtt-q20.png ./reno-rtt-q20.png
vagrant scp :~/bufferbloat/reno-rtt-q100.png ./reno-rtt-q100.png
```

TCP BBR experiments

```bash
rm -rf bb-q20-bbr bb-q100-bbr && \
vagrant scp :~/bufferbloat/bb-q20 ./bb-q20-bbr
vagrant scp :~/bufferbloat/bb-q100 ./bb-q100-bbr
vagrant scp :~/bufferbloat/bbr-buffer-q20.png ./bbr-buffer-q20.png
vagrant scp :~/bufferbloat/bbr-buffer-q100.png ./bbr-buffer-q100.png
vagrant scp :~/bufferbloat/bbr-rtt-q20.png ./bbr-rtt-q20.png
vagrant scp :~/bufferbloat/bbr-rtt-q100.png ./bbr-rtt-q100.png
```
