import io
import os
import json

import googleapiclient.discovery
import google_auth_oauthlib.flow
import googleapiclient.errors

from googleapiclient.http import MediaIoBaseDownload

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
import pickle


scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def authentification():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
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
    request = youtube.playlists().list(
        part="id,snippet",
        channelId=channel_id,
        maxResults=max_results,
    )
    playlists_list = request.execute()["items"]

    return playlists_list

def get_one_playlist(youtube, playlist_id):
    request = youtube.playlists().list(
        part="id,snippet",
        id=playlist_id
    )
    playlist = request.execute()["items"]

    return playlist

def get_playlist_items(youtube, playlist_id):
    
    request = youtube.playlistItems().list(
        part="contentDetails,snippet",
        playlistId=playlist_id,
        maxResults=50,
    )
    videos_list = request.execute()["items"]

    return videos_list

def get_video(youtube, video_id):
    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    video_data = request.execute()["items"][0]
    return video_data

def get_transcript(ytt_api, video_id):
    
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
    if os.path.exists(f"database/{playlist['id']}"):
        return
    
    os.mkdir(f"database/{playlist['id']}")
    dir = f"database/{playlist['id']}/desc.json"
    with open(dir, "w") as file:
        json.dump(playlist, file)

def add_to_folder(playlist_id, video):
    video_id = video["contentDetails"]["videoId"]
    filename = f"{video_id}.json"
    dir = f"database/{playlist_id}/{filename}"

    if os.path.exists(dir):
        return
    
    with open(dir, "w") as file:
        json.dump(video, file)

    
   
def update(youtube, ytt_api):
    channel_id = "UCdxesVp6Fs7wLpnp1XKkvZg"
    playlists = get_playlists(youtube, channel_id, 20)

    for playlist in playlists:

      #playlist_id = "PL4_hYwCyhAvaUQ6oGA7sjUcf2VXSo1Txy"
      playlist_id = playlist["id"]
      #playlist = get_one_playlist(youtube, playlist_id)[0]
      print("Плейлист:", playlist["snippet"]["title"])
      print("Плейлист:", playlist["snippet"]["description"])
      print("-----------------------------------------------")
      # title = "Алгоритмы и структуры данных / основной поток (1 курс, весна 2025) - Степанов И. Д."
      # big_video_id = "Cy7M4WnFFUY"

      make_folder(playlist)

      playlist_items = get_playlist_items(youtube, playlist_id)

      for video in playlist_items:
          #video = get_video(item["id"])
          print(video["snippet"]["title"])
          #print(video["snippet"]["description"])
          video_id = video["contentDetails"]["videoId"]
          #print(f"id={video_id}")
          
          check_dir = f"database/{playlist_id}/{video_id}.json"
          if not os.path.exists(check_dir):
              video["snippet"]["transcript"] = get_transcript(ytt_api, video_id)
              add_to_folder(playlist_id, video)
      print("================================")

def pickle_get_object(filename):
    with open(filename, 'rb') as file:
        obj = pickle.load(file)
    return obj
    
def main():
    youtube, ytt_api = authentification()
    update(youtube, ytt_api)

if __name__ == "__main__":
    main()