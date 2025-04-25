from video_searcher import global_search

def main():
    playlist_tags = {"lecturer":"Степанов И. Д.", "course":"1"}
    playlist_tags = {}
    video_tags = {}
    response = global_search(playlist_tags, video_tags)

    for i in range(min(7, len(response))):
      print(response[i].tags)
      print(response[i].playlist.tags)
      print(response[i].timestamps)
      print(response[i].title)
      print(response[i].desc)
      print("-----------------")
    # print([video.desc for video in response])
    #print(response[1].transcript.text)

if __name__ == "__main__":
    main()