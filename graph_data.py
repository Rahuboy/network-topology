import os
import json
import argparse
from collections import OrderedDict

def filelist(root):
    with open(root, "r") as f:
        urls = f.readlines()
        for i, _ in enumerate(urls):
            urls[i] = urls[i].strip()
    return urls

def main(args):
    # Path of json files
    json_files = os.listdir(args.data)
    # Files
    fl = filelist(args.sites)

    # Nodes and Links
    nodes_prem = set()
    nodes, links = [], [] 
    # Make directory if it doesn't exist
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    nodes_file = open(os.path.join(args.output, "nodes.json"), "w")
    links_file = open(os.path.join(args.output, "links.json"), "w")

    # Iterate through files in path
    nodes_prem.add((("AS Number", 0), ("Organization", "Host"), ("Group", "source")))
    for json_file in json_files:
        if json_file[:-5] not in fl:
            continue
        # temp_nodes, temp_lat = ['0'], [0]
        od = OrderedDict()
        od['0'] = 0
        
        f = open(os.path.join(args.data, json_file), "r")
        stuff = json.loads(f.read())
        # if json file is empty, skip
        if len(stuff) == 0:
            continue
        for idx, j in enumerate(stuff):
            nodes_prem.add((("AS Number", int(j["AS Number"])), ("Organization", j["Organization"]), ("Group", "router")))
            if j["AS Number"] in od:
                od[j["AS Number"]] += j["Latency"]
            else:
                od[j["AS Number"]] = j["Latency"]

        # update last set item to be a destination
        nodes_prem.remove((("AS Number", int(j["AS Number"])), ("Organization", j["Organization"]), ("Group", "router")))
        nodes_prem.add((("AS Number", int(j["AS Number"])), ("Organization", j["Organization"]), ("Group", "destination")))
        node_keys = list(od.keys())
        for i in range(len(node_keys) - 1):
            links.append({"AS_Src":int(node_keys[i]), "AS_Dst":int(node_keys[i+1]), "Latency":od[node_keys[i+1]], "Path":json_file[:-5]})

        f.close()

    # Add to list
    for i in nodes_prem:
        nodes.append(dict((x,y) for x,y in i))

    json.dump(nodes, nodes_file, indent=4)
    json.dump(links, links_file, indent=4)
    nodes_file.close()
    links_file.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate graph data")
    parser.add_argument("-s", "--sites", help="txt file with sites", default="sites.txt")
    parser.add_argument("-d", "--data", help="Path to data folder", default="data3/json")
    parser.add_argument("-o", "--output", help="Path to output folder", default="data3/graph_json")
    args = parser.parse_args()
    main(args)