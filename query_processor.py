from video_searcher import request

def main():
    tags = []
    response = request(tags)
    print([video.title for video in response])
    print(response[1].transcript)

if __name__ == "__main__":
    main()