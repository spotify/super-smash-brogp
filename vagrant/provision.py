#!/usr/bin/env python

import sys
import pyeapi
import httplib


def print_info_message():
    print "BOX is no longer reachable with vagrant up. Use ssh instead (check the IP in the initial conf)"
    print "Don't forget to change the network type of the first NIC of the box."


def provision_eos(port, username, password):
    connection = pyeapi.client.connect(
        transport='https',
        host='localhost',
        username='vagrant',
        password='vagrant',
        port=port
    )
    device = pyeapi.client.Node(connection)

    commands = list()
    commands.append('configure session')
    commands.append('rollback clean-config')

    with open('../eos/initial.conf', 'r') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line == '':
            continue
        if line.startswith('!'):
            continue
        commands.append(line)

    commands[-1] = 'commit'

    try:
        device.run_commands(commands)
    except httplib.BadStatusLine:
        # This actually means everything went fine
        print_info_message()


if __name__ == "__main__":
    os = sys.argv[1]
    port = sys.argv[2]
    username = sys.argv[3]
    password = sys.argv[4]

    provision_eos(port, username, password)
