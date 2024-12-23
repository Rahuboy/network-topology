import subprocess
import os
import sys
import threading
import argparse

def gen_data(url, args):
    # call traceroute
    # check if file url.txt exists
    if os.path.exists(os.path.join(args.output, url + ".txt")) and not args.overwrite:
        return
    
    print("started thread for " + url)
    op = subprocess.getoutput("traceroute -I -m 50 " + url)
    # out the output to a file calles url.txt
    p_op = parse_output(op)
  
    with open(os.path.join(args.output, url + ".txt"), "w") as f:
        f.write(p_op)
    print("finished thread for " + url)

def parse_output(op):
    p_op = []
    op = op.split("\n")
    op = op[1:]
    for line in op:
        # if line has * * * then ignore
        if "* * *" in line:
            continue
        line = line.split("  ")

        # Find average latency
        latency = []
        for i in range(len(line)):
            if " ms" in line[i]:
                latency.append(float(line[i].split()[0]))

        if len(line) > 1:
            latency = sum(latency) / len(latency)
            p_op.append(str(latency) + " " + line[1])
        

    # make the output a string
    p_op = "\n".join(p_op)
    return p_op

def main(args):
    # read urls from file
    with open(args.file, "r") as f:
        urls = f.readlines()

    # create output folder if it doesn't exist
    os.makedirs(args.output, exist_ok=True)

    # generate data for each url
    for url in urls:
        url = url.strip() # remove \n
        # create a thread for each url
        t = threading.Thread(target=gen_data, args=(url, args,))
        t.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file",
                        help="file containing the urls",
                        default="./sites.txt")
    parser.add_argument("-o", "--output",
                        help="folder with output files",
                        default="./data2/output")
    parser.add_argument("--overwrite",
                        help="overwrite existing files",
                        action="store_true")
    args = parser.parse_args()
    main(args)