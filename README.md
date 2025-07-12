## Overview

This repo contains a study about the bufferbloat phenomenon done for the Masters class in Computer Networks at Federal University of Rio de Janeiro (UFRJ) in the first semester of 2025.


## Dependencies

- [vagrant](https://www.vagrantup.com/downloads) for VM configuration. I chose to run vagrant together with [virtualbox](https://www.virtualbox.org/wiki/Downloads), if there is a mismatch between your linux kernel version and the boxes available on VirtualBox you may need to install the dkms version.

## How to run

- From the root of this repo run `git clone https://github.com/skywardpixel/mininet-vagrant`.
- `cd mininet-vagrant && vagrant up` to boot up and setup the VM we'll be working with.
- `vagrant plugin install vagrant-scp` to install scp

Now we need to copy the script files to the VM and run it:

- `vagrant scp ../bufferbloat :/home/vagrant/bufferbloat`
- `vagrant ssh` to attach to the VM

Once attached we need to setup the VM system dependencies:

- `$sudo apt install wireshark -y`
- `$nohup sudo wireshark > wireshark.log &` to start wireshark in the background
- `$cd bufferbloat`

