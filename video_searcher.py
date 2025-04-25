import io
import os
import json
from media import Video, Playlist

def matching_playlist_dirs(tags={}):
  result = []
  playlist_folders = os.listdir("./database")
  for folder in playlist_folders:
    # if folder[0] != "P":
    #   continue # костыль для проверки (потом убрать)
    desc_dir = f"database/{folder}/desc.json"

    with open(desc_dir, "r") as file:
      playlist = Playlist(json.load(file))
    # if "tags" not in playlist:
    #   continue
    print(playlist.tags)
    print(tags)
    print()
    if all((key in playlist.tags and tags[key] == playlist.tags[key]) for key in tags):
      result.append(folder)
  
  return result

def matching_videos(folder, tags={}):

  playlist_dir = f"database/{folder}/desc.json"
  with open(playlist_dir, "r") as file:
    playlist = Playlist(json.load(file))

  result = []

  video_files = os.listdir(f"./database/{folder}")

  video_files.remove("desc.json")
  for video_file in video_files:
    dir = f"database/{folder}/{video_file}"
    with open(dir, "r") as file:
      video = Video(json.load(file), playlist)
    # if "tags" not in video:
    #   continue
    if all(key in video.tags and tags[key] == video.tags[key] for key in tags):
      result.append(video)
  
  return result

def global_search(playlist_tags={}, video_tags={}):
  result = []
  for playlist_folder in matching_playlist_dirs(playlist_tags):
    result.extend(matching_videos(playlist_folder, video_tags))

  return result