import io
import os

import googleapiclient.discovery
import google_auth_oauthlib.flow
import googleapiclient.errors

from googleapiclient.http import MediaIoBaseDownload

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
import pickle


scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def downloads():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "creds_local.json"

    # Get credentials and create an API client

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server(port=0)
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    
    request = youtube.captions().list(
        part="id",
        videoId="Cy7M4WnFFUY"
    )
    available_captions = request.execute()

    print(available_captions)

    
    ytt_api = YouTubeTranscriptApi(
      proxy_config=WebshareProxyConfig(
        proxy_username="mlenlbet",
        proxy_password="xk1ah2zznopb",
      )
    )

    channel_id = "UCdxesVp6Fs7wLpnp1XKkvZg"
    playlist_id = "PL4_hYwCyhAvaUQ6oGA7sjUcf2VXSo1Txy"
    title = "Алгоритмы и структуры данных / основной поток (1 курс, весна 2025) - Степанов И. Д.",
    video_id = "Cy7M4WnFFUY"

    request = youtube.playlistItems().list(
        part="contentDetails,id,snippet",
        playlistId="PL4_hYwCyhAvaUQ6oGA7sjUcf2VXSo1Txy"
    )
    response = request.execute()["items"]

    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    video_description = request.execute()["items"][0]["snippet"]["description"]
    print(video_description)
    print("===================")

    fetched_transcript = ytt_api.fetch(video_id, languages=['ru'])
    for snippet in fetched_transcript:
      print(snippet.text)

    transcript_data = fetched_transcript.to_raw_data()

    with open("Subtitles", 'wb') as subfile:
       pickle.dump(transcript_data, subfile)

def get_subtitles(video_id):
    with open("Subtitles", 'rb') as subfile:
       transcript_data = pickle.load(subfile)
    print(transcript_data)
    
def main():
    # downloads()
    get_subtitles("some_id")

if __name__ == "__main__":
    main()