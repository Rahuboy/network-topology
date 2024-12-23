from pyvis.network import Network
from glob import glob 
import json
import os
import random
import math
import argparse
import matplotlib.pyplot as plt
import numpy as np

# Default WIDTH
WIDTH = 5

# HexColors
def rgb2hex(c):
    r,g,b=c
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

def hex2rgb(t):
    return tuple(int(t[i:i+2], 16) for i in (0, 2, 4))

# colder colors -> lower latency
latencytocolor = {
  float('-inf'): (31, 81, 255),
  0: (31, 81, 255),
  25: (0, 150, 255),
  50: (137, 207, 240),
  75: (173, 216, 230),
  100: (240, 255, 255),
  125: (255, 255, 255),
  150: hex2rgb("FFCBCB"),
  175: hex2rgb("FC7676"),
  200: hex2rgb("d9381e"),
  225: hex2rgb("c21807"),
  250: hex2rgb("ff2400"),
}

def main(args):
    # Define Network
    net = Network(directed=True, bgcolor='#222222', font_color='white', height="1200px")
    net.options.groups = {
            "router": {                 
                "shape": 'icon',
                "icon": {
                    "face": 'FontAwesome',
                    "code": '\uf233',
                    "size": 50,
                    "color": 'white'
                }
            },
            "source": {
                "shape": 'icon',
                "icon": {
                    "face": 'FontAwesome',
                    "code": '\uf109',
                    "size": 50,
                    "color": 'white'
                }
            },
            "destination": {
                "shape": 'icon',
                "icon": {
                    "face": 'FontAwesome',
                    "code": '\uf0ac',
                    "size": 50,
                    "color": 'white'
                }
            }
        }

    # Make output folder if it doesn't exist
    if not os.path.exists(args.output):
        os.makedirs(args.output)
   
    # Src Number
    src_num = -1
    links = {}
    in_deg = {} # key: in
    out_deg = {} # key: out
    node_details = {}
    for folder in args.data:
        # Nodes
        f_node = open(os.path.join(folder, "nodes.json"), "r")
        nodes_dic = json.load(f_node)
        nodes_list = [x["AS Number"] if x["AS Number"] else src_num for x in nodes_dic]
        nodes_group = [x["Group"] for x in nodes_dic]
        nodes_labels = [str(x["AS Number"]) if x["AS Number"] else folder[5:][:-11] for x in nodes_dic]
        nodes_titles = [x["Organization"] if x["AS Number"] else folder[5:][:-11] for x in nodes_dic]
        for node in nodes_dic:
            id = str(node["AS Number"]) if node["AS Number"] else folder[5:][:-11]
            node_details[id] = node["Organization"][:5]+"..."+node["Organization"][-4:]  if node["AS Number"] else folder[5:][:-11]
        for i in range(len(nodes_list)):
            net.add_node(nodes_list[i], label=nodes_labels[i], size=10, shape="icon", group=nodes_group[i], title=nodes_titles[i])
        f_node.close()

        # Links
        f_link = open(os.path.join(folder, "links.json"), "r")
        links_dic = json.load(f_link)
        for link in links_dic:
            l_src = node_details[str(link["AS_Src"]) if link["AS_Src"] else folder[5:][:-11]]
            l_dst = node_details[str(link["AS_Dst"])]
            if(l_dst in in_deg.keys()):
                in_deg[l_dst] += 1
            else:
                in_deg[l_dst] = 1
            if(l_src in out_deg.keys()):
                out_deg[l_src] += 1
            else:
                out_deg[l_src] = 1
            if link["Path"] not in links.keys():
                links[link["Path"]] = [(link["AS_Src"] if link["AS_Src"] else src_num, link["AS_Dst"], link["Latency"])]
            else:
                links[link["Path"]].append((link["AS_Src"] if link["AS_Src"] else src_num, link["AS_Dst"], link["Latency"]))
        f_link.close()
        src_num -= 1

    # Degrees (Histogram)
    stage_delete = []
    for node in in_deg:
        if(node not in out_deg):
            stage_delete.append(node)
    for node in stage_delete:
        del in_deg[node]

    plt.figure(figsize=(20, 12))
    plt.bar(list(in_deg.keys()), in_deg.values(), color='g')
    plt.xlabel('Organizations')
    plt.ylabel('In-Degree')
    plt.title('In-Degree of Network Nodes')
    plt.yticks(np.arange(0, max(in_deg.values())+5, 1))
    plt.xticks(rotation=80)
    plt.savefig(os.path.join(args.output, 'in-degree.png'))
    
    for k, x in links.items():
            if not args.latency:
                c = (random.randint(60, 255), random.randint(60, 255), random.randint(60, 255))
            for y in x:
                src, dst, lat = y
                if args.latency:
                    for key in sorted(latencytocolor.keys())[::-1]:
                        if lat > key:
                            c = latencytocolor[key]
                            break
                net.add_edge(src, dst, color=rgb2hex(c), width=WIDTH, title="Path: "+k+", Latency: "+str(max(0, int(lat))))

    # Show
    # net.show_buttons(filter_=['physics'])
    net.set_edge_smooth('dynamic')
    net.repulsion(node_distance=250)

    print(net.html)
    net.show(os.path.join(args.output, "graph.html"), notebook=False)

    # replace https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css
    with open(os.path.join(args.output, "graph.html"), 'r') as file :
        filedata = file.read()
    # Replace the target string
    filedata = filedata.replace('</head>', '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" type="text/css"/>\n</head>')

    # Write the file out again
    with open(os.path.join(args.output, "graph.html"), 'w') as file:
        file.write(filedata)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate graph data")
    parser.add_argument("-d", "--data", nargs='+', help="Path to data folders", default="data3/graph_json")
    parser.add_argument("-o", "--output", help="Path to output folder", default="./data3")
    parser.add_argument("--latency", action="store_true", help="Use latency color scheme")
    args = parser.parse_args()

    main(args)