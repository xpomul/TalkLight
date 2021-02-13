#!/opt/local/bin/python

from pprint import pprint
import subprocess
import argparse
from urllib import request, parse

parser = argparse.ArgumentParser(description='Check active call and update OpenHab item')
parser.add_argument('--debug', action='store_true', help='debug putput')

args = parser.parse_args()
debug = args.debug

state_url = "http://pine.local:8080/rest/items/Anruf_Aktiv"

commands = {
    "Teams": { "cmd": "lsof -alPi -c \"Microsoft Teams Helper (Renderer)\" +c 50 -n -M | wc -l", "threshold": 8 },
    "SfB": { "cmd": "lsof -alP -c \"Skype for Business\" +c 50 -n -M -i4udp | wc -l", "threshold": 0 },
    "Skype": { "cmd": "lsof -alP -c \"Skype Helper (Renderer)\" +c 50 -n -M -i4udp | wc -l", "threshold": 5 },
    "Telephone": { "cmd": "lsof -alP -c \"Telephone\" +c 50 -n -M -i4udp | wc -l", "threshold": 2 }
}

def check_calls():   
    for app, cmdToThres in commands.items():
        cmd = cmdToThres["cmd"]
        thres = cmdToThres["threshold"]

        if debug: 
            print ("Running ", app, " check: ", cmd)
        output = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
        int_output = int(output)
        if debug: 
            print ("-> Output was ", int_output, " threshold = ", thres)

        if int_output > thres:
            return True
    
    return False

def switch_item(state):
    if debug: 
        print ("New Item State = " + state)

    encoded_state = state.encode('utf-8')
    req = request.Request(state_url, data=encoded_state, headers={'Content-Type': 'text/plain'}) 
    if debug:
        print ("Executing request:")
        pprint(vars(req))

    resp = request.urlopen(req)
    if debug:
        print ("Got response:", resp.code, resp.msg)
        
# -- main entry point

result = check_calls()

if result:
    switch_item("ON")
else:
    switch_item("OFF")

if debug:
    print ("All done.")
