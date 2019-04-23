import requests
import time
import serial
from serial import Serial

ser = serial.Serial('/dev/ttyACM0', 115200)
time.sleep(2)
def playing_pass_track_to_arduino(track_data):
    track_data["playing_status"] = "playing"
    print('Track Number: ', track_data["number"])
    print('Track ID: ', track_data["id"])
    print('Starting Location: ', track_data["start"])
    print('Ending Location: ', track_data["end"])
    track_str = str(track_data["start"])
    ser.write(bytes(track_str, encoding='ASCII'))
    return track_data

def paused_pass_track_to_arduino(track_data):
    track_data["playing_status"] = "paused"
    print('Track Number: ', track_data["number"])
    print('Track ID: ', track_data["id"])
    print('Starting Location: ', track_data["start"])
    print('Ending Location: ', track_data["end"])
    #ser.write(b'0')
    ser.write(b'-666')
    return track_data

def scanning(track_ids):
    #do we need to write something to serial output when scanning for new tracks?
    #call image processing and get new locations for each track id
    num_tracks = len(track_ids)
    new_start = 100
    new_end = 200
    for track_id in track_ids:
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