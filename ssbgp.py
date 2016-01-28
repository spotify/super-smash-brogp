#!/usr/bin/env python

# Copyright 2016 Spotify AB. All rights reserved.
#
# The contents of this file are licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import os
import time
import yaml
import argparse

from random import sample, randint, shuffle

path = os.path.dirname(os.path.realpath(__file__))


def build_help():
    parser = argparse.ArgumentParser(description="Sends and retrieves BGP prefixes for fun.")
    parser.add_argument(dest='peer', action='store', help="Peer's IP address.")
    parser.add_argument(dest='local_as', action='store', help="Our own AS.")
    parser.add_argument(dest='conf', action='store', help="Path to configuration file.")
    args = parser.parse_args()

    return args


def read_config(config_file):
    with open('{}/{}'.format(path, config_file), 'r') as f:
        return yaml.load(f)


def read_prefixes(prefixes_file):
    prefixes = set()

    with open('{}/{}'.format(path, prefixes_file)) as f:
        for line in f.readlines():
            line = line.strip()

            prefixes.add(line)

    return prefixes


def build_as_paths(total, min_as_path, max_as_path):
    as_paths = dict()
    available_as_paths = range(1, 64999)

    for i in range(0, total):
        shuffle(available_as_paths)
        as_paths[i] = available_as_paths[:randint(min_as_path, max_as_path)]

    return as_paths


def announce_prefixes(local_as, prefixes, peer, min_num_prefixes, max_num_prefixes, max_total, announced_prefixes,
                      available_as_paths, num_as_paths, next_hop):
    i = 0

    possible_prefixes = prefixes - announced_prefixes

    num = min(randint(min_num_prefixes, max_num_prefixes), max_total - len(announced_prefixes))
    if len(possible_prefixes) < num:
        num = len(possible_prefixes)

    prefixes_to_announce = set(sample(possible_prefixes, num))
    prefixes_to_announce -= announced_prefixes

    for prefix in prefixes_to_announce:
        as_path = [str(i) for i in available_as_paths[randint(0, num_as_paths - 1)]]
        print 'neighbor {} announce route {} next-hop {} as-path [ {} {} ]'.format(peer, prefix, next_hop, local_as,
                                                                                   ' '.join(as_path))

    return announced_prefixes | prefixes_to_announce


def remove_prefixes(peer, announced_prefixes, remove_prefixes):
    num = len(announced_prefixes) * remove_prefixes / 100

    prefixes_to_withdraw = set(sample(announced_prefixes, num))

    for prefix in prefixes_to_withdraw:
        print 'neighbor {} withdraw route {} next-hop self'.format(peer, prefix)

    return announced_prefixes - prefixes_to_withdraw


def main():
    args = build_help()
    conf = read_config(args.conf)
    prefixes = read_prefixes(conf['PREFIXES_FILE'])

    time.sleep(10)

    announced_prefixes = set()

    available_as_paths = build_as_paths(conf['NUM_DIFFERENT_AS_PATHS'], conf['MIN_AS_LENGTH'], conf['MAX_AS_LENGTH'])

    #Initial warmup according to INITIAL_WARMUP
    announced_prefixes = announce_prefixes(
        args.local_as, prefixes, args.peer, conf['INITIAL_WARMUP'], conf['INITIAL_WARMUP'], conf['MAX_TOTAL'],
        announced_prefixes, available_as_paths, conf['NUM_DIFFERENT_AS_PATHS'], conf['NEXT_HOP'])
    time.sleep(conf['INITIAL_WAIT'])

    while True:
        announced_prefixes = announce_prefixes(args.local_as, prefixes, args.peer, conf['MIN_PREFIXES'],
                                               conf['MAX_PREFIXES'], conf['MAX_TOTAL'], announced_prefixes,
                                               available_as_paths, conf['NUM_DIFFERENT_AS_PATHS'], conf['NEXT_HOP'])

        announced_prefixes = remove_prefixes(args.peer, announced_prefixes, conf['REMOVE_PREFIXES'])
        time.sleep(conf['WAITING_TIME'])


if __name__ == "__main__":
    main()
