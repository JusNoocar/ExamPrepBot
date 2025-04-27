"""
This is the code for searching over the database and finding videos.
"""

import io
import os
import json
from media import Video, Playlist

def matching_playlist_dirs(tags={}):
  """
  Finds playlist folder names matching specified playlist tags.
    
  Args:
      tags (dict, optional): Dictionary of playlist tag keys and expected values.
    
  Returns:
      list: List of folder names in the "./database" directory whose playlists
            contain all provided tag keys with matching values.
  """
  result = []
  playlist_folders = os.listdir("./database")
  for folder in playlist_folders:
    desc_dir = f"database/{folder}/desc.json"

    with open(desc_dir, "r") as file:
      playlist = Playlist(json.load(file))
    # if "tags" not in playlist:
    #   continue
    if all((key in playlist.tags and tags[key] == playlist.tags[key]) for key in tags):
      result.append(folder)
  
  return result

def matching_videos(folder, tags={}):
  """
  Finds videos in a playlist folder matching specified video tags.
    
  Args:
      folder (str): Name of the playlist folder inside "./database".
      tags (dict, optional): Dictionary of video tag keys and expected values.
    
  Returns:
      list: List of Video objects within the specified playlist folder whose tags 
            contain all given keys with matching values.
  """
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
  """
  Performs a global search across playlists and videos filtering by tags.
    
  Args:
      playlist_tags (dict, optional): tags to filter playlists
      video_tags (dict, optional): tags to filter videos
    
  Returns:
      list: Combined list of Video objects matching 
            the tag filters.
  """
  result = []
  for playlist_folder in matching_playlist_dirs(playlist_tags):
    result.extend(matching_videos(playlist_folder, video_tags))

  return result