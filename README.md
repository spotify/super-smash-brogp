# super-smash-brogp

Sends and withdraws BGP prefixes for fun.

## Purpose

The purpose of this tool is to stress test a BGP implementation. Maybe you are testing a new feature, vendor or ASIC. This tool will allow you to test if the code is stable, if convergence is fast, if the feature works, if there are memory leaks, etc.

##Installation

To install super-smash-brogp just clone the repo and install the dependancies:

    pip install -r requirements.txt

## Usage

The tool is meant to be run inside [exabgp](https://github.com/Exa-Networks/exabgp). There is not much purpose of using the tool in the CLI unless you want to see what it does.

### exabgp

Configure exabgp in any way you want. Just make sure you configure the process stanza to use ssbgp.py correctly, i.e.:

    group v4 {
        capability {
            asn4 enable;
            route-refresh enable;
            graceful-restart 60;
        }

        family {
            ipv4 unicast;
        }

        neighbor 192.168.232.0 {
            process p1_v4 {
                run ../../ssbgp.py 192.168.232.0 65001 config_files/ssbgp/v4_conf.yaml;
            }
            local-address 192.168.232.1;
            peer-as 4290030000;
            local-as 65001;
            router-id 192.168.232.1;

            graceful-restart;
            group-updates;
        }
    }

Finally start exabgp:

    exabgp /path/to/my/config/exabgp.conf

It's better if you check exabgp's documentation but at least you should be able to get started with the previous instructions.

### CLI

To run the tool in the CLI without using exabgp:

    # ./ssbgp.py -h
    usage: ssbgp.py [-h] peer local_as conf

    Sends and withdraws BGP prefixes for fun.

    positional arguments:
      peer        Peer's IP address.
      local_as    Our own AS.
      conf        Path to configuration file.

    # ./ssbgp.py 192.168.232.0 65000 config_files/ssbgp/v4_conf.yaml
    neighbor 192.168.232.0 announce route 65.124.137.0/24 next-hop self as-path [ 65001 3687 34884 59039 10321 40604 ]
    neighbor 192.168.232.0 announce route 46.1.248.0/23 next-hop self as-path [ 65001 3384 53606 8798 ]
    neighbor 192.168.232.0 announce route 93.92.213.0/24 next-hop self as-path [ 65001 26471 49757 62653 56834 61765 11971 ]
    neighbor 192.168.232.0 announce route 147.55.0.0/16 next-hop self as-path [ 65001 9430 58646 41084 28728 22795 35881 35001 36980 41257 14490 ]
    ... (several thousands of lines later)
    neighbor 192.168.232.0 withdraw route 74.91.96.0/20 next-hop self
    neighbor 192.168.232.0 withdraw route 139.14.0.0/16 next-hop self
    neighbor 192.168.232.0 withdraw route 190.225.80.0/21 next-hop self
    neighbor 192.168.232.0 withdraw route 204.137.28.0/24 next-hop self
    ... (several thousands of lines later)
    neighbor 192.168.232.0 announce route 134.146.197.0/24 next-hop self as-path [ 65001 61694 33123 57374 30016 10484 48033 30745 32085 6588 32729 ]
    neighbor 192.168.232.0 announce route 91.212.127.0/24 next-hop self as-path [ 65001 51081 38087 22779 53030 32589 42626 43528 ]
    neighbor 192.168.232.0 announce route 177.66.204.0/22 next-hop self as-path [ 65001 63813 38719 36942 27446 43241 29719 ]
    neighbor 192.168.232.0 announce route 91.213.41.0/24 next-hop self as-path [ 65001 42479 27888 23140 45226 51505 41316 38073 501 17781 19305 ]
    neighbor 192.168.232.0 announce route 1.23.167.0/24 next-hop self as-path [ 65001 23306 19037 20574 35460 6329 ]
    ... etc

### Example

Here you can see the result of running 4 ssbgp processes against a router:

    lab# show ip bgp sum
    BGP summary information for VRF default
    Router identifier 192.168.232.0, local AS number 65000
    Neighbor Status Codes: m - Under maintenance
      Neighbor         V  AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State  PfxRcd PfxAcc
      192.168.232.1    4  65001         278679     17852    0    0    5d10h Estab  223826 223826
      192.168.232.3    4  65003         279508     17852    0    0    5d10h Estab  223860 223860
      192.168.232.5    4  65005         280321     17852    0    0    5d10h Estab  223881 223881
      192.168.232.7    4  65007         273854     17852    0    0    5d10h Estab  223871 223871

## Configuration

### ssbgp

You can tweak some parameters like how many prefixes you want to add/remove on each iteration, how fast, from which file you want to read the prefixes, etc. You can find some examples in `config_files/ssbgp/`.

### exabgp

The tool leverages on exabgp, so the first thing you have to do is configure it to establish the peering sessions with your device. You have to make sure that you call the process that will start advertising and removing prefixes. You can find some examples on how to configure exabgp and call the process in `config_files/exabgp/`.
