# Network-Topology

### Directory Structure
- The raw data is present in `data/data_*`. The data used in the graphs is present in the following folders: `data/data_Bangalore`, `data/data_Hyderabad`, 
`data/data_IITB`, `data/data_IITH`, `data/data_Jodhpur`, `data/data_Poland` and `data/data_US`.
- The 4 python scripts used to generate the data and parse the graphs are: `gen_data.py`, `parse_data.py`, `graph_data.py` and `graph_gen.py`.
- The visualizations are present in the folder `visualization`. The two interactive graphs are `graph_latency.html` and `graph_normal.html`. Open them in a browser (tested on Chrome). There are two sample images of the graphs, and also a histogram with the in-degrees of the intermediate routers.
- A report of the Network Topology is present in `report.pdf`, and the destinations used are present (and can be modified) in `sites.txt`. `sites_og.txt` and `sites_og_2.txt` can be specified as flags for more websites.

### Running the code
- It is recommended to use a conda environment and install the required python packages. The code was tested on both MacOS and Linux
To run the code, use:
```./run.sh <data-folder-list>```
For example:
```./run.sh data/data_Bangalore data/data_Hyderabad data/data_US```

### Small Bugs
- You might have to zoom in and out before the icons are visible in the graphs (a two finger scroll or using the mouse's scroll-wheel should work). Note that the graph is also interactive, with the links 
behaving like springs.