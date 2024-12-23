strlist=""
for var in "$@"
do
    mkdir $var
    cp sites.txt $var/sites.txt
    python gen_data.py -o $var/output/ -f $var/sites.txt
    python parse_data.py -f $var/output -o $var/json
    python graph_data.py -d $var/json -o $var/graph_json -s $var/sites.txt
    strlist+=" $var/graph_json"
done

# string of $var/graph_json (space separated)
python graph_gen.py -d $strlist -o graphs