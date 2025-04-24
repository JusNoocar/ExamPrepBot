import io
import os
import json

def matching_playlists(tags=[]):
  result = []
  playlist_folders = os.listdir()
  for folder in playlist_folders:
    if folder[0] != "P":
      continue # костыль для проверки (потом убрать)
    desc_dir = f"{folder}/desc.json"

    with open(desc_dir, "r") as file:
      playlist = json.load(file)
    # if "tags" not in playlist:
    #   continue
    if all(tag in playlist["tags"] for tag in tags):
      result.append(folder)
  
  return result

def matching_videos(folder, tags=[]):
  result = []
  video_files = os.listdir(f"./{folder}")

  video_files.remove("desc.json")
  for video_file in video_files:
    dir = f"{folder}/{video_file}"
    with open(dir, "r") as file:
      video = json.load(file)
    # if "tags" not in video:
    #   continue
    if all(tag in video["tags"] for tag in tags):
      result.append(dir)
  
  return result

def global_search(tags=[]):
  result = []
  for playlist_folder in matching_playlists(tags):
    result.extend(matching_videos(playlist_folder))

  return result

class Video:
  def __init__(self, json_data):
    self.id = json_data["contentDetails"]["videoId"]
    self.title = json_data["snippet"]["title"]
    self.desc = json_data["snippet"]["description"]
    self.upload_date = json_data["contentDetails"]["videoPublishedAt"]
    # self.tags = json_data["tags"]
    self.transcript = json_data["snippet"]["transcript"]

def request(tags=None):
    response = []
    for dir in global_search(tags):
      with open(dir, "r") as file:
        json_data = json.load(file)
      response.append(Video(json_data))
    
    return response