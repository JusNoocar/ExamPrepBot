from video_searcher import global_search

def main():
    playlist_tags = {"subject":'Алгоритмы и структуры данных, продвинутый поток', "course":"1", "season":"весна"}
    #playlist_tags = {}
    video_tags = {}
    response = global_search(playlist_tags, video_tags)

    for i in range(len(response)):
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