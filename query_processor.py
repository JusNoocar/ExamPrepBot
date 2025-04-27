"""
This is the main file for processing the queries.
"""

from video_searcher import global_search
from text_processor import transcript_search, timestamp_search
from tests import make_tests
import time
   
cnt_tests = 0
def run_test(test: list):
    """
    Runs a single test case.

    Args:
        test (list): A list, each element is a list of two elements - playlist tags and query.
    """
    global cnt_tests
    playlist_tags, query = test
    print(f'===============TEST {cnt_tests}============')
    print("=============================================")
    print("Запрос:", query)
    print("Теги:", playlist_tags)
    print()

    start_time = time.time()
    video_tags = {}
    response = global_search(playlist_tags, video_tags)

    print("Поиск подходящих видео по тегам:")
    print("==========================================")
    for i in range(len(response)):
      print(f"{i + 1} / {len(response)}")
      print(response[i].tags)
      print(response[i].playlist.tags)
      print(response[i].timestamps)
      print()
      print(response[i].title)
      # print()
      # print(response[i].desc)
      print("----------------------------------------")
    print()
    # print([video.desc for video in response])
    #print(response[1].transcript.text)
    if len(response) != 0:
        timestamp_search(query, response, 0.75)
        transcript_search(query, response, 0.75)
    else:
        print('По запросу ничего не найдено')

    end_time = time.time()
    mins = int(end_time - start_time) // 60
    secs = int(end_time - start_time) % 60
    print(f"Finished in {mins} minutes,  {secs} seconds")

def main():
    """
    Executes all test cases.
    """
    global cnt_tests
    for test in [make_tests()[0]]:
       cnt_tests += 1
       run_test(test)
   

if __name__ == "__main__":
    main()