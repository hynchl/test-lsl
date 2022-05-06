######################################################################################
# LSLGazepoint.py - LSL interface
# Written in 2019 by Gazepoint www.gazept.com
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along with this
# software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
######################################################################################

# This Python script uses the Open Gaze API to communicate with the Gazepoint Control
# application. Eye gaze data is read via the Open Gaze API, and then streamed to LSL.

from random import sample
import socket
import time
import re
import pylsl as lsl
import time
import numpy as np

# Commands to send to the Open Gaze API
requests = ['<SET ID="ENABLE_SEND_COUNTER" STATE="1"/>\r\n',
            '<SET ID="ENABLE_SEND_TIME" STATE="1"/>\r\n',
            '<SET ID="ENABLE_SEND_TIME_TICK" STATE="1"/>\r\n',
            '<SET ID="ENABLE_SEND_POG_FIX" STATE="1"/>\r\n',
            '<SET ID="ENABLE_SEND_POG_LEFT" STATE="1"/>\r\n',
            '<SET ID="ENABLE_SEND_POG_RIGHT" STATE="1"/>\r\n',
            '<SET ID="ENABLE_SEND_POG_BEST" STATE="1"/>\r\n',
            '<SET ID="ENABLE_SEND_PUPIL_LEFT" STATE="1"/>\r\n',
            '<SET ID="ENABLE_SEND_PUPIL_RIGHT" STATE="1"/>\r\n',
            '<SET ID="ENABLE_SEND_CURSOR" STATE="1"/>\r\n',
            '<SET ID="ENABLE_SEND_BLINK" STATE="1"/>\r\n',
            '<SET ID="ENABLE_SEND_DATA" STATE="1"/>\r\n']


# Socket send
def send(sock, msg):
    msgb = msg.encode()
    totalsent = 0
    while totalsent < len(msgb):
        sent = sock.send(msgb[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent


# Socket receive
def receive(sock):
    msg = ''
    numbytes = 0
    t0 = time.time()
    while True:
        chunk = sock.recv(1)

        if (len(chunk) == 0):
            break
        msg = msg + (chunk.decode())
        if (msg.endswith('\r\n')):
            # print('Received:',msg.encode())
            break

    return msg


def extract_value(item, input, output):
    m = re.search(f'(?<={item}=")\d*\.\d+|\d+(?=" {item})', input)
    if (m != None): 
        output[item] = float(m.group(0))

if __name__ == "__main__":
    print("good")

    # Connect to Gazepoint Control
    s = socket.socket()
    s.connect(('127.0.0.1', 4242))

    # Send request to start streaming data
    numreq = len(requests)
    indreq = 0
    for i in range(numreq):
        send(s, requests[i])
        msg = receive(s)

    # Determine serial number
    sn = "000000000"
    send(s, '<GET ID="SERIAL_ID" />\r\n')
    msg = receive(s)
    m = re.search('(?<=<ACK ID="SERIAL_ID" VALUE=")\d*\.\d+|\d+(?=" />)', msg)
    if (m != None):
        sn = m.group(0)
    # Initialize LSL entry
    info_gaze = lsl.StreamInfo('GazepointEyeTracker', 'gaze', 36, 150, 'float32', 'gazepoint' + sn)

    # Set meta-data for LSL entry
    info_gaze.desc().append_child_value("manufacturer", "Gazepoint")
    channels = info_gaze.desc().append_child("channels")


    # time
    channels.append_child("channel").append_child_value("label", "CNT").append_child_value("unit", "integer").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "EPOCHTIME").append_child_value("unit", "seconds").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "TIME").append_child_value("unit", "seconds").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "TIMETICK").append_child_value("unit", "nanoseconds").append_child_value("type", "gaze")
    
    # fixation
    channels.append_child("channel").append_child_value("label", "FPOGX").append_child_value("unit", "percent").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "FPOGY").append_child_value("unit", "percent").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "FPOGS").append_child_value("unit", "seconds").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "FPOGD").append_child_value("unit", "seconds").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "FPOGID").append_child_value("unit", "integer").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "FPOGV").append_child_value("unit", "boolean").append_child_value("type", "gaze")
    
    # gaze
    channels.append_child("channel").append_child_value("label", "LPOGX").append_child_value("unit", "percent").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "LPOGY").append_child_value("unit", "percent").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "LPOGV").append_child_value("unit", "boolean").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "RPOGX").append_child_value("unit", "percent").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "RPOGY").append_child_value("unit", "percent").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "RPOGV").append_child_value("unit", "boolean").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "BPOGX").append_child_value("unit", "percent").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "BPOGY").append_child_value("unit", "percent").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "BPOGV").append_child_value("unit", "boolean").append_child_value("type", "gaze")

    # pupil
    channels.append_child("channel").append_child_value("label", "LPCX").append_child_value("unit", "percent").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "LPCY").append_child_value("unit", "percent").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "LPD").append_child_value("unit", "pixels").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "LPS").append_child_value("unit", "scalar").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "LPV").append_child_value("unit", "boolean").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "RPCX").append_child_value("unit", "percent").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "RPCY").append_child_value("unit", "percent").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "RPD").append_child_value("unit", "pixels").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "RPS").append_child_value("unit", "scalar").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "RPV").append_child_value("unit", "boolean").append_child_value("type", "gaze")

    #bkid
    channels.append_child("channel").append_child_value("label", "BKID").append_child_value("unit", "integer").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "BKDUR").append_child_value("unit", "seconds").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "BKPMIN").append_child_value("unit", "integer").append_child_value("type", "gaze")
    
    #cursor
    channels.append_child("channel").append_child_value("label", "CX").append_child_value("unit", "pixels").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "CY").append_child_value("unit", "pixels").append_child_value("type", "gaze")
    channels.append_child("channel").append_child_value("label", "CS").append_child_value("unit", "integer").append_child_value("type", "gaze")

    #etc
    channels.append_child("channel").append_child_value("label", "USER").append_child_value("unit", "seconds").append_child_value("type", "gaze")
    

    # Make an LSL outlet
    outlet_gaze = lsl.StreamOutlet(info_gaze)

    # Continuously stream data and push each data sample to the LSL
    while True:

        # Reset data values to 0
        rec = {
        "CNT":np.nan,
        "EPOCHTIME":time.time(),
        "TIME":np.nan,
        "TIME_TICK":np.nan,
        "FPOGX":np.nan,
        "FPOGY":np.nan,
        "FPOGS":np.nan,
        "FPOGD":np.nan,
        "FPOGID":np.nan,
        "FPOGV":np.nan,
        "LPOGX":np.nan,
        "LPOGY":np.nan,
        "LPOGV":np.nan,
        "RPOGX":np.nan,
        "RPOGY":np.nan,
        "RPOGV":np.nan,
        "BPOGX":np.nan,
        "BPOGY":np.nan,
        "BPOGV":np.nan,
        "LPCX":np.nan,
        "LPCY":np.nan,
        "LPD":np.nan,
        "LPS":np.nan,
        "LPV":np.nan,
        "RPCX":np.nan,
        "RPCY":np.nan,
        "RPD":np.nan,
        "RPS":np.nan,
        "RPV":np.nan,
        "BKID":np.nan,
        "BKDUR":np.nan,
        "BKPMIN":np.nan,
        "CX":np.nan,
        "CY":np.nan,
        "CS":np.nan,
        "USER":0}
        
        # Read data
        msg = receive(s)
        # Data looks like: '<FPOGX="0.26676" FPOGY="0.99285" ... FPOGV="1"/>\r\n'

        # Parse data string to extract values
        for key in list(rec.keys()):
            if key == "EPOCHTIME": continue
            extract_value(key, msg, rec)

        # Push data to LSL
        samplegaze = rec.values()
        outlet_gaze.push_sample(samplegaze)


    s.close()
