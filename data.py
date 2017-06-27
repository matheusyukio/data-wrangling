#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
"""
Wrangle the data and transform the shape of the data
into the model to MongoDB. 
Output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


def shape_element(element):
    node = {}
    address = {}
    created = {}
    pos = [None, None]
    
    #print 'element'
    #print element
    if element.tag == "node" or element.tag == "way" :
        node["type"] = element.tag
        
        # iterate element attrib
        #Add attributes
        for key in element.attrib:
            if key in CREATED:
                if 'created' not in node:
                    node["created"] = {}
                created["version"] = element.attrib["version"]
                created["changeset"] = element.attrib["changeset"]
                created["timestamp"] = element.attrib["timestamp"]
                created["user"] = element.attrib["user"]
                created["uid"] = element.attrib["uid"]
                node["created"] = created
                
            elif key in ["lat","lon"]:
                if "pos" not in node:
                    node["pos"] = [None, None]
                    
                if key == "lon":
                    pos[0] = float(element.attrib[key])
                else:
                    pos[1] = float(element.attrib[key])
            else:
                node[key] = element.attrib[key]
        
        # iterate child
        for child in element:
            # iterate "tag" tag
            if child.tag == "tag":
                if not problemchars.search(child.attrib["k"]):
                    # single colon
                    if lower_colon.search(child.attrib["k"]):
                        if child.attrib["k"].find("addr") == 0:
                            if "address" not in node:
                                node["address"] = {}
                            sub_attr = child.attrib["k"].split(':', 1)
                            node["address"][sub_attr[1]] = child.attrib["v"]
                        else:
                            node[child.attrib["k"]] = child.attrib["v"]
                    # no colon
                    elif child.attrib["k"].find(':') == -1:
                        node[child.attrib["k"]] = child.attrib["v"]
            # iterate "nd" tag
            if child.tag == "nd":
                if "node_refs" not in node:
                    node["node_refs"] = []
                
                node["node_refs"].append(child.attrib["ref"])
        
        if pos:
            node["pos"] = pos
        #if address:
        #    node["address"] = address
        #if created:
        #    node['created'] = created
        #if node_refs:
        #    node['node_refs'] = node_refs

            print node
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map('example.osm', True)
    #pprint.pprint(data)
    
    correct_first_elem = {
        "id": "261114295", 
        "visible": "true", 
        "type": "node", 
        "pos": [41.9730791, -87.6866303], 
        "created": {
            "changeset": "11129782", 
            "user": "bbmiller", 
            "version": "7", 
            "uid": "451048", 
            "timestamp": "2012-03-28T18:31:23Z"
        }
    }
    assert data[0] == correct_first_elem
    assert data[-1]["address"] == {
                                    "street": "West Lexington St.", 
                                    "housenumber": "1412"
                                      }
    assert data[-1]["node_refs"] == [ "2199822281", "2199822390",  "2199822392", "2199822369", 
                                    "2199822370", "2199822284", "2199822281"]

if __name__ == "__main__":
    test()