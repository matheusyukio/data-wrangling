#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
"""
Find out how many unique users
have contributed to the map in this particular area!

The function process_map should return a set of unique user IDs ("uid")
"""

def get_user(element):
    return

def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if element.tag == "node":
            user = element.attrib['user']
            if user in users:
                pass
            else:
                users.add(user)

    return users


def test():

    users = process_map('new-york-usa-sample.osm')
    pprint.pprint(users)
    assert len(users) == 6



if __name__ == "__main__":
    test()
