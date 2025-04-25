from bisect import bisect_left

class Playlist:
  def __init__(self, json_data):
    self.id = json_data["id"]
    self.title = json_data["snippet"]["title"]
    self.desc = json_data["snippet"]["description"]
    self.upload_date = json_data["snippet"]["publishedAt"]
    self.videos = []

    def make_tags(title):
      tags = dict()
      if '—' in title:
        name, lecturer = title.split(') — ')
      else:
        name, lecturer = title.split(') - ')
      tags['lecturer'] = lecturer
      tags['subject'], playlist_period = name.split(' (')
      tags['course'] = playlist_period.split(', ')[0][0]
      tags['season'], tags['year'] = playlist_period.split(', ')[1].split(' ')

      return tags
    #self.tags = json_data["tags"]
    self.tags = make_tags(self.title)

    self.videos = []

  def add_video(self, video):
    self.videos.append(video)


class Video:
  def __init__(self, json_data, playlist):
    self.id = json_data["contentDetails"]["videoId"]
    self.title = json_data["snippet"]["title"]
    self.desc = json_data["snippet"]["description"]
    self.upload_date = json_data["contentDetails"]["videoPublishedAt"]

    def make_tags(description):
      timestamps = []
      lecturer = ''
      lecture_date = ''
      tags = dict()
      info = description.split('\n\n')
      for bit in info:
        if len(bit) > 5 and bit[:5] == "00:00" or "Таймкоды" in bit:
          bit_copy = bit.replace("Таймкоды:", "Таймкоды")
          bit_copycopy = bit_copy.split("Таймкоды\n")[-1]
          if all("-" in line for line in bit_copycopy.split('\n')):
            timestamps = [line.split(' - ') for line in bit_copycopy.split('\n')]
          else:
            timestamps = [[line.split(' ')[0], ' '.join(line.split(' ')[1:])] for line in bit_copycopy.split('\n')]
        if "дата лекции" in bit.lower():
          bit_copy = bit.replace(':\n', ': ')
          if ":" in bit_copy:
            lecture_date = bit_copy.split('\n')[0].split(': ')[1]
          else:
            lecture_date = bit_copy.split('\n')[1]
        if "Лектор" in bit:
          bit_copy = bit.split("Лектор")[1]
          lecturer = bit_copy.split(": ")[1]
      tags["lecturer"] = lecturer
      tags["lecture_date"] = lecture_date
      tags["year"] = lecture_date.split(".")[-1]
      if len(tags["year"]) == 2:
        tags["year"] = "20" + tags["year"]

      return tags, timestamps

    # self.tags = json_data["tags"]
    self.tags, self.timestamps = make_tags(self.desc)
    self.transcript = Transcript(json_data["snippet"]["transcript"])

    self.playlist = playlist
    self.playlist.add_video(self)


class Transcript:
  def __init__(self, json_data):
    self.data = json_data
    self.text = ' '.join(chunk["text"] for chunk in self.data)
    self.length = len(self.text.split(' '))
    self.chunks_count = len(self.data)
    self.chunks_start_pos = [0]
    for chunk in self.data:
       self.chunks_start_pos.append(self.chunks_start_pos[-1] + len(chunk["text"]))
    self.chunks_start_pos.pop()

  def get_timestamp(self, word_pos):
    chunk_num = bisect_left(self.chunks_start_pos, word_pos)

    return self.data[chunk_num]["start"]
  