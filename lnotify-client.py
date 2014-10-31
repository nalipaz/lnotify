#!/usr/bin/env python
#  Project: lnotify
#  Description: A libnotify client/daemon that receives 
#  notifications by monitoring messages sent to  a socket.  
#  Author: Nicholas Alipaz <nicholas@alipaz.net>
#
import zmq
import argparse
import os
import pipes
import re
import sys
import json

# get command line argument (hostname)
parser = argparse.ArgumentParser(description='Connect to notification queue')
parser.add_argument('hostname', nargs=1, help='Where Weechat is running')
args = parser.parse_args()
hostname = args.hostname[0]

# start socket connection
context = zmq.Context()
socket = context.socket(zmq.SUB)
try:
    socket.connect("tcp://%s:5000" % hostname)
except:
    print "Cannot make connection to %s." % hostname
    sys.exit(1)

# subscribe to `message` queue
socket.setsockopt(zmq.SUBSCRIBE, "message")

notifiercommand = "notify-send -i {0} -a WeeChat {1} {2}"

os.system(
    notifiercommand.format(
        "weechat",
        "weechat-zmq-notifier",
        pipes.quote("Successfully started. Now listening for messages.")
    )
)

while True:
    try:
        queue, arg = socket.recv().split(" ", 1)
        data = json.loads(arg)

        os.system(
            notifiercommand.format(
                pipes.quote(data['icon']),
                pipes.quote(data['origin']),
                pipes.quote(data['message'])
            )
        )
        if data['sounds']:
            soundcommand = "({0} {1} -q &) &> /dev/null"
            if data['query_type'] == "highlight":
                 os.system(
                     soundcommand.format(
                         data['sound_cmd'],
                         pipes.quote(data['highlight_sound'])
                     )
                 )

            elif data['query_type'] == "query":
                 os.system(
                     soundcommand.format(
                         data['sound_cmd'],
                         pipes.quote(data['query_sound'])
                     )
                 )



    except (KeyboardInterrupt, SystemExit):
        sys.exit('Quitting...')
