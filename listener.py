import requests
import time
import serial
from serial import Serial
from PIL import Image

ser = serial.Serial('/dev/ttyACM1', 115200)
time.sleep(2)
def playing_pass_track_to_arduino(track_data):
    track_data["playing_status"] = "playing"
    print('Track Number: ', track_data["number"])
    print('Track ID: ', track_data["id"])
    print('Starting Location: ', track_data["start"])
    print('Ending Location: ', track_data["end"])
    track_str = str(track_data["start"])
    #ser.write(b'800')
    ser.write(bytes(track_str, encoding='ASCII'))
    return track_data

def paused_pass_track_to_arduino(track_data):
    track_data["playing_status"] = "paused"
    print('Track Number: ', track_data["number"])
    print('Track ID: ', track_data["id"])
    print('Starting Location: ', track_data["start"])
    print('Ending Location: ', track_data["end"])
    ser.write(b'0')
    ser.write(b'-666')
    return track_data

def scanning(track_ids):
    #do we need to write something to serial output when scanning for new tracks?
    #call image processing and get new locations for each track id
    num_tracks = len(track_ids)
    new_starts = []

    im = Image.open('cam1.jpg') # Can be many different formats.
    pix = im.load()
    print (im.size)  # Get the width and hight of the image for iterating over
    w = im.size[0]
    h = im.size[1]
    band = 20
    bandw = band*2 + 1
    numOfPix = w*h
    s = 0
    highBound = int(h/2) - band
    lowBound = int(h/2) + band
    leftBound = 60
    rightBound = w-250
    mergeW = 3

    hi = 0
    lo = 255
    #grayscale
    for i in range(leftBound, rightBound+1):
        for j in range(highBound,lowBound):
            (a,b,c) = pix[i,j]
            z = (a+b+c)/3
            z = int(z)
            if(z>hi): hi = z
            elif(z<lo): lo = z
            pix[i,j] = (z,z,z)

    rat = 255/(hi-lo)

    #######################################
    ## Should try area based contrast
    ######################################

    #bump contrast
    for i in range(leftBound, rightBound+1):
        for j in range(highBound,lowBound):
            z = pix[i,j][0] - lo
            z = z*rat
            z = int(z)
            pix[i,j] = (z,z,z)

    hi = 0
    lo = 255
    #horizontal contrast
    for i in range(leftBound, rightBound):
        for j in range(highBound,lowBound):
            z = pix[i,j][0] - pix[i+1,j][0]
            if(z>255): z=255
            elif(z<0): z=0
            if(z>hi): hi = z
            elif(z<lo): lo = z
            pix[i,j] = (z,z,z)

    rat = 255/(hi-lo)
    print(lo)
    print(hi)
    print(rat)
    #bump contrast
    for i in range(leftBound, rightBound):
        for j in range(highBound,lowBound):
            z = pix[i,j][0] - lo
            z = z*rat
            z = int(z)
            pix[i,j] = (z,z,z)

    #vertical merge
    for i in range(leftBound, rightBound):
        s = 0
        count = 0
        for j in range(highBound,lowBound):
            s += pix[i,j][0]
            count += 1
        s = int(s/count * rat)
        if(s > 255): s = 255
        for j in range(highBound,lowBound):
            pix[i,j] = (s,s,s)

    tc = 1
    tl = [0,0,0]
    tl = []
    tl.append(0)
    #select
    for i in range(leftBound, rightBound):
        j = h/2
        z = pix[i,j][0]
        if(z>200):
            pix[i,j] = (255,0,0)
            if(tc == 1):
                tc += 1
                tl.append(i)
            elif(i - tl[tc-1] < 10):
                tl[tc-1] = i
            else:
                tc += 1
                tl.append(i)
                
    for i in range(len(tl)):
        tl[i] = int(tl[i]*1.2 +165+9*i)

    print(tl)
    print(tc)

    #im.save('contrast2.png')  # Save the modified pixels as .png
    print('Done')

    for i in range(num_tracks):
        new_starts.append(i)
    new_end = 12
    for track_id, new_start in zip(track_ids, new_starts):
        requests.post('https://smart-turntable-webapp.herokuapp.com/api/set_track_location', json={"track_id":track_id, "start":new_start, "end":new_end})

def main():
    previous_status = ""
    while(True):
        time.sleep(1)
        playing_status = requests.get('https://smart-turntable-webapp.herokuapp.com/api/play_status')
        print(playing_status.json())
        if(previous_status != playing_status.json()["play_status"]):
            if playing_status.json()["play_status"] == "playing":
                track_data = requests.get('https://smart-turntable-webapp.herokuapp.com/api/current_track')
                print(track_data.json())
                previous_status = playing_status.json()["play_status"]
                print(previous_status)
                playing_pass_track_to_arduino(track_data.json())
            elif playing_status.json()["play_status"] == "paused":
                track_data = requests.get('https://smart-turntable-webapp.herokuapp.com/api/current_track')
                print(track_data.json())
                previous_status = playing_status.json()["play_status"]
                print(previous_status)
                paused_pass_track_to_arduino(track_data.json())
            elif playing_status.json()["play_status"] == "scanning":
                track_ids = playing_status.json()["scan_track_ids"]
                scanning(track_ids)
                requests.post('https://smart-turntable-webapp.herokuapp.com/api/set_play_status', json={"is_playing": "paused", "set_track_data": None})

if __name__ == "__main__":
    main()