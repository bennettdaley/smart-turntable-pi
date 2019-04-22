import requests
import time
import serial
from serial import Serial

ser = serial.Serial('/dev/ttyACM0', 115200)
time.sleep(2)
def playing_pass_track_to_arduino(track_data):
    track_data["playing_status"] = "playing"
    ser.write(b'1')
    return track_data

def paused_pass_track_to_arduino(track_data):
    track_data["playing_status"] = "paused"
    ser.write(b'0')
    return track_data

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


if __name__ == "__main__":
    main()