import requests
import time

def playing_pass_track_to_arduino(track_data):
    track_data["playing_status"] = "playing"
    return track_data

def paused_pass_track_to_arduino(track_data):
    track_data["playing_status"] = "paused"
    return track_data

def main():
    while(True):
        time.sleep(5)
        playing_status = requests.get('https://smart-turntable-webapp.herokuapp.com/api/play_status')
        print(playing_status.json())
        if playing_status.json()["play_status"] == "playing":
            track_data = requests.get('https://smart-turntable-webapp.herokuapp.com/api/current_track')
            print(track_data.json()["track_title"])
            playing_pass_track_to_arduino(track_data.json())
        elif playing_status.json()["play_status"] == "paused":
            track_data = requests.get('https://smart-turntable-webapp.herokuapp.com/api/current_track')
            print(track_data.json()["track_title"])
            paused_pass_track_to_arduino(track_data.json())


if __name__ == "__main__":
    main()