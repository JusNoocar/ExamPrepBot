"""
This is the file with the media classes.
"""

class Playlist:
  """
  Represents a YouTube playlist.
    
  Attrs:
      id (str): Unique playlist id
      title (str): Playlist title
      desc (str): Playlist description
      upload_date (str): Upload date
      videos (list): List of videos in playlist
      tags (dict): Tags
  """
  def __init__(self, json_data):
    """
    Initializes playlist from YouTube API response data.
        
    Args:
        json_data (dict): Raw playlist data from YouTube API
    """
    self.id = json_data["id"]
    self.title = json_data["snippet"]["title"]
    self.desc = json_data["snippet"]["description"]
    self.upload_date = json_data["snippet"]["publishedAt"]
    self.videos = []

    self.tags = make_playlist_tags(self.title)

    self.videos = []

  def add_video(self, video):
    """
    Adds a video to the playlist.
        
    Args:
        video (Video): Video object
    """
    self.videos.append(video)


class Video:
  """Represents a YouTube video with transcript.
    
  Attrs:
      id (str): Unique video id
      title (str): Video title
      desc (str): Video description
      upload_date (str): Upload date
      tags (dict): Tags
      timestamps (list): List of [timecode, description] pairs
      transcript (Transcript): Processed transcript data
      playlist (Playlist): Parent playlist reference
  """
  def __init__(self, json_data, playlist):
    """
    Initializes video from YouTube API response data.
        
    Args:
        json_data (dict): Raw video data from YouTube API
        playlist (Playlist): Parent playlist instance
    """
    self.id = json_data["contentDetails"]["videoId"]
    self.title = json_data["snippet"]["title"]
    self.desc = json_data["snippet"]["description"]
    self.upload_date = json_data["contentDetails"]["videoPublishedAt"]

    self.tags, self.timestamps = make_video_tags(self.desc)
    self.transcript = None
    if json_data["snippet"]["transcript"] != None:
        self.transcript = Transcript(json_data["snippet"]["transcript"])

    self.playlist = playlist
    self.playlist.add_video(self)


class Transcript:
  """
  Handles video transcript processing and timestamp lookup.
    
  Attrs:
      data (list): Transcript chunks
      text (list): Extracted text from transcript chunks
      length (int): Total word count in transcript
      chunks_count (int): Number of transcript chunks
      chunks_start_pos (list): Cumulative word positions for chunks
  """
  
  def __init__(self, json_data):
    """
    Initializes transcript from JSON data.
        
      Args:
          json_data (list): List of transcript chunks with text and start times
    """
    self.data = json_data
    self.text = [chunk["text"] for chunk in self.data]
    self.length = sum([len(chunk.split(' ')) for chunk in self.text])
    self.chunks_count = len(self.data)
    self.chunks_start_pos = [0]
    for chunk in self.data:
      self.chunks_start_pos.append(self.chunks_start_pos[-1] + len(chunk["text"]))
    self.chunks_start_pos.pop()
  

def make_playlist_tags(title):
  """
  Extracts tags from playlist title.
    
  Args:
      title (str): Playlist title
        
  Returns:
      dict: Processed tags: subject, course, season, year, and lecturer
  """
  tags = dict()
  title = title.replace('  ', ' ')
  if '—' in title:
    name, lecturer = title.split(') — ')
  elif '-' in title:
    name, lecturer = title.split(') - ')
  else:
    name = title.split(')')[0]
    lecturer = ''
  tags['lecturer'] = lecturer.replace('. ', '.')
  tags['subject'], playlist_period = name.split(' (')
  if ',' in playlist_period:
    if (playlist_period.split(', ')[0][0]).isdigit():
      tags['course'] = playlist_period.split(', ')[0][0]
      tags['season'], tags['year'] = playlist_period.split(', ')[1].split(' ')
    else:
      tags['course'] = playlist_period.split(', ')[1][0]
      tags['season'], tags['year'] = playlist_period.split(', ')[0].split(' ')
  else:
    tags['course'] = ''

    splitter = playlist_period.split(' ')
    if len(splitter) == 2:
        tags['season'], tags['year'] = splitter
    elif len(splitter) == 4:
      if (splitter[0][0]).isdigit():
        tags['course'] = splitter[0][0]
        tags['season'], tags['year'] = splitter[2], splitter[3]
      else:
        tags['course'] = splitter[2][0]
        tags['season'], tags['year'] = splitter[0], splitter[1]


  return tags


def make_video_tags(description):
  """
  Extracts tags and timestamps from video description.
    
  Args:
      description (str): Video description
        
  Returns:
      tuple: (tags_dict, timestamps_list) containing tags
              and timestamp data
  """
  timestamps = []
  lecturer = ''
  lecture_date = ''
  tags = dict()
  info = description.split('\n\n')
  for bit in info:
    if (len(bit) > 5 and bit[:5] == "00:00") or ("Таймкоды" in bit and len(bit.split('\n')) > 1):
      bit_copy = bit.replace("Таймкоды:", "Таймкоды")
      bit_copycopy = bit_copy.split("Таймкоды\n")[-1]
      if all("-" in line for line in bit_copycopy.split('\n')):
        timestamps = [line.split(' - ') for line in bit_copycopy.split('\n')]
      else:
        timestamps = [[line.split(' ')[0], ' '.join(line.split(' ')[1:])] for line in bit_copycopy.split('\n')]
    if "Дата лекции" in bit:
      bit_copy = bit.replace(':\n', ': ')
      bit_copycopy = bit_copy.split("Дата лекции")[-1]
      if ":" in bit_copycopy:
        lecture_date = bit_copycopy.split('\n')[0].split(': ')[1]
      else:
        lecture_date = bit_copycopy.split('\n')[1]
    elif "Дата семинара" in bit:
      bit_copy = bit.replace(':\n', ': ')
      bit_copycopy = bit_copy.split("Дата семинара")[-1]
      if ":" in bit_copycopy:
        lecture_date = bit_copycopy.split('\n')[0].split(': ')[1]
      else:
        lecture_date = bit_copycopy.split('\n')[1]
    elif "Дата допсема" in bit:
      bit_copy = bit.replace(':\n', ': ')
      bit_copycopy = bit_copy.split("Дата допсема")[-1]
      if ":" in bit_copycopy:
        lecture_date = bit_copycopy.split('\n')[0].split(': ')[1]
      else:
        lecture_date = bit_copycopy.split('\n')[1]
    if "Лектор" in bit:
      bit_copy = bit.split("Лектор")[-1]
      lecturer = bit_copy.split("\n")[0].split(': ')[-1]
    elif "Семинарист" in bit:
      bit_copy = bit.split("Семинарист")[-1]
      lecturer = bit_copy.split("\n")[0].split(': ')[-1]
  tags["lecturer"] = lecturer
  tags["lecture_date"] = lecture_date
  tags["year"] = lecture_date.split(".")[-1]
  if len(tags["year"]) == 2:
    tags["year"] = "20" + tags["year"]

  return tags, timestamps