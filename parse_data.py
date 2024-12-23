import subprocess
import os
import re
import argparse
from glob import glob
import json
from tqdm import tqdm


def whois(ip_addrs_list):
    """Run whois command on the list of ip addresses to obtain netrange and organization
    To obtain ASN, use the curl command below
    Returns:
        list of outputs
    """
    op = []
    for ip in tqdm(ip_addrs_list):
        op.append(subprocess.getoutput('whois -h whois.cymru.com " -v ' + ip + '"'))
    return op


def parse_output(op_list, latency):
    """Parse the output of whois command and curl command
    Input:
        List of op
        op:
            AS      | IP               | BGP Prefix          | CC | Registry | Allocated  | AS Name
            32      | 171.67.215.200   | 171.64.0.0/14       | US | arin     | 1994-08-22 | STANFORD, US
        latency:
            float

    Returns:
        list of dictionaries
        dict = {
            "AS Number" : [],
            "Range": "",
            "Organization": ""
        }
    """
    parsed_op, valid_idxs, latencies = [], [], []
    for idx, op in enumerate(op_list):
        op = op.split("\n")[-1]
        op_dict = {}
        line = op.split("|")
        if len(line) < 2:
            continue
        op_dict["AS Number"] = line[0].strip()
        if op_dict["AS Number"] == "NA":
            continue
        op_dict["IP"] = line[1].strip()
        op_dict["Range"] = line[2].strip()
        op_dict["Organization"] = line[6].strip()
        valid_idxs.append(idx)
        parsed_op.append(op_dict)

    # find differences between consecutive valid latencies
    if len(valid_idxs) != 0:
        latencies.append(latency[valid_idxs[0]])
    for i in range(len(valid_idxs) - 1):
        latencies.append(latency[valid_idxs[i + 1]] - latency[valid_idxs[i]])
    # update the latencies in the parsed_op
    for i, idx in enumerate(valid_idxs):
        parsed_op[i]["Latency"] = latencies[i]

    return parsed_op


def main(args):
    """Reads IP addresses from the files in args.folder, 
    runs whois command on them and saves the output as json in args.output
    """
    os.makedirs(args.output, exist_ok=True)
    for file in (pbar := tqdm(glob(os.path.join(args.folder, "*.txt")))):
        pbar.set_description("Processing %s" % file)
        with open(file, "r") as f:
            op = f.read()
        op = op.split("\n")
        ip_addrs = []
        latency = []
        # continue if the file is empty
        if op[-1] == "":
            continue
        for line in op:
            ip_addrs.append(line.split()[-1][1:-1]) # remove () surrounding ip
            latency.append(float(line.split()[0]))
        # check if json already exists
        if os.path.exists(os.path.join(args.output, file.split('/')[-1][:-4] + ".json")) and not args.overwrite:
            continue
        op_list = whois(ip_addrs)
        json_dict = parse_output(op_list, latency)
        with open(os.path.join(args.output, file.split('/')[-1][:-4] + ".json"), "w") as f2: # obtain filename, remove .txt and add .json
            json.dump(json_dict, f2, indent=4)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--folder",
                        help="folder containing the data files",
                        default="./data2/output")
    parser.add_argument("-o", "--output",
                        help="folder with output files",
                        default="./data2/json")
    parser.add_argument("--overwrite",
                        help="overwrite existing files",
                        action="store_true")
    args = parser.parse_args()
    main(args)