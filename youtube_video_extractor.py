"""
This code extracts videos from Youtube and stores them in the database.
"""

import io
import os
import json

import googleapiclient.discovery
import google_auth_oauthlib.flow
import googleapiclient.errors

from googleapiclient.http import MediaIoBaseDownload

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig


scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def authentification():
    """
    Performs OAuth2 authentication and initializes YouTube and transcript API.
    
    Returns:
        tuple: (youtube, ytt_api)
            youtube: Google API client for YouTube v3.
            ytt_api: YouTubeTranscriptApi client.
    """
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "creds_local.json"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server(port=0)
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
  
    ytt_api = YouTubeTranscriptApi(
      proxy_config=WebshareProxyConfig(
        proxy_username="mlenlbet",
        proxy_password="xk1ah2zznopb",
      )
    )
    return youtube, ytt_api

def get_playlists(youtube, channel_id, max_results):
    """
    Gets a list of playlists for a given YouTube channel.
    
    Args:
        youtube: YouTube API client.
        channel_id (str): YouTube channel ide.
        max_results (int): Maximum number of playlists to get.
    
    Returns:
        list: List of playlist dicts.
    """
    request = youtube.playlists().list(
        part="id,snippet",
        channelId=channel_id,
        maxResults=max_results,
    )
    playlists_list = request.execute()["items"]

    return playlists_list

def get_one_playlist(youtube, playlist_id):
    """
    Gets data of a specific playlist.
    
    Args:
        youtube: YouTube API client.
        playlist_id (str): Playlist id.
    
    Returns:
        list: List containing playlist dict.
    """
    request = youtube.playlists().list(
        part="id,snippet",
        id=playlist_id
    )
    playlist = request.execute()["items"]

    return playlist

def get_playlist_items(youtube, playlist_id):
    """
    Retrieves videos from a playlist.
    
    Args:
        youtube: YouTube API client.
        playlist_id (str): Playlist id.
    
    Returns:
        list: List of videos dicts.
    """
    request = youtube.playlistItems().list(
        part="contentDetails,snippet",
        playlistId=playlist_id,
        maxResults=50,
    )
    videos_list = request.execute()["items"]

    return videos_list

def get_video(youtube, video_id):
    """
    Fetches data for a specific video.
    
    Args:
        youtube: YouTube API client.
        video_id (str): Video id.
    
    Returns:
        dict: Video dict.
    """
    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    video_data = request.execute()["items"][0]
    return video_data

def get_transcript(ytt_api, video_id):
    """
    Fetches transcript for a video using YouTubeTranscriptApi.
    
    Args:
        ytt_api: YouTubeTranscriptApi client.
        video_id (str): Video id.
    
    Returns:
        list or None: Transcript data list if it's possible to download subtitles, else None.
    """
    try:
      fetched_transcript = ytt_api.fetch(video_id, languages=['ru'])
    except Exception:
      print(f"https://www.youtube.com/watch?v={video_id}", " - transcript unavailable!")
      return None
    # for snippet in fetched_transcript:
    #   print(snippet.text)

    transcript_data = fetched_transcript.to_raw_data()

    return transcript_data

def dumper(obj, filename):
    with open(filename, 'wb') as file:
        pickle.dump(obj, file)


def make_folder(playlist):
    """
    Creates a folder for a playlist and saves its description JSON.
    
    Args:
        playlist (dict): Playlist dict from YouTube API.
    """
    if os.path.exists(f"database/{playlist['id']}"):
        return
    
    os.mkdir(f"database/{playlist['id']}")
    dir = f"database/{playlist['id']}/desc.json"
    with open(dir, "w") as file:
        json.dump(playlist, file)

def add_to_folder(playlist_id, video):
    """
    Adds video JSON file to the playlist folder.
    
    Args:
        playlist_id (str): Playlist id.
        video (dict): Video dict.
    """
    video_id = video["contentDetails"]["videoId"]
    filename = f"{video_id}.json"
    dir = f"database/{playlist_id}/{filename}"

    if os.path.exists(dir):
        return
    
    with open(dir, "w") as file:
        json.dump(video, file)

    
   
def update(youtube, ytt_api):
    """
    Fetches latest playlists and videos for the specified channel, storing them in the database directory.
    For each playlist, creates a folder and downloads data and transcripts for videos.
    
    Args:
        youtube: YouTube API client.
        ytt_api: YouTubeTranscriptApi client.
    """
    channel_id = "UCdxesVp6Fs7wLpnp1XKkvZg"
    playlists = get_playlists(youtube, channel_id, 20)

    for playlist in playlists:
      playlist_id = playlist["id"]
      print("Плейлист:", playlist["snippet"]["title"])
      print("Плейлист:", playlist["snippet"]["description"])
      print("-----------------------------------------------")

      make_folder(playlist)

      playlist_items = get_playlist_items(youtube, playlist_id)

      for video in playlist_items:
          print(video["snippet"]["title"])
          video_id = video["contentDetails"]["videoId"]
          
          check_dir = f"database/{playlist_id}/{video_id}.json"
          if not os.path.exists(check_dir):
              video["snippet"]["transcript"] = get_transcript(ytt_api, video_id)
              add_to_folder(playlist_id, video)
      print("================================")
    
def main():
    """Main function to authenticate and update the database."""
    youtube, ytt_api = authentification()
    update(youtube, ytt_api)

if __name__ == "__main__":
    main()