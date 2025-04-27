"""
This is the main code for processing texts using language processing and transformers.
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer, util
import spacy
from spellchecker import SpellChecker
import requests

import os


nlp = spacy.load('ru_core_news_md')

spell = SpellChecker(language='ru')

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def yandex_spellcheck(text):
    """
    Corrects spelling in Russian text using Yandex spellchecker.

    Args:
        text (str): Input text to be spellchecked.

    Returns:
        str: Corrected text.
    """

    url = "https://speller.yandex.net/services/spellservice.json/checkText"
    params = {
        "text": text,
        "lang": "ru"
    }
    response = requests.get(url, params=params)
    corrections = response.json()
    corrected_text = text

    for error in sorted(corrections, key=lambda x: x['pos'], reverse=True):
        start = error['pos']
        end = start + error['len']
        if error['s']:
            correction = error['s'][0]
            corrected_text = corrected_text[:start] + correction + corrected_text[end:]
    return corrected_text

def clean_text(text):
    """
    Normalizes text by lowercasing and collapsing whitespace.

    Args:
        text (str): Input text.

    Returns:
        str: Cleaned text.
    """

    return ' '.join(text.lower().split())

def lemmatize(text):
    """
    Lemmatizes Russian text.

    Args:
        text (str): Input text.

    Returns:
        str: Lemmatized text.
    """

    doc = nlp(text)
    return ' '.join([token.lemma_ for token in doc])

def cache_embeddings(video_id, chunks):
    """
    Caches embeddings for text chunks if not already cached.

    Args:
        video_id (str): Unique video id.
        chunks (list): List of text chunks.
    """

    if os.path.exists(f"cache/{video_id}_embeddings.npy"):
        return

    texts = [clean_text(chunk) for chunk in chunks]
    embeddings = model.encode(texts, convert_to_tensor=False, show_progress_bar=True)
    np.save(f"cache/{video_id}_embeddings.npy", embeddings)

def load_cache(video_id):
    """
    Loads cached embeddings for a video.

    Args:
        video_id (str): Unique video id.

    Returns:
        numpy.ndarray: Loaded embeddings array.
    """

    embeddings = np.load(f"cache/{video_id}_embeddings.npy")
    return embeddings

def convert_time(time):
    """
    Converts time string 'HH:MM:SS' to seconds format.

    Args:
        time (str): Time string.

    Returns:
        int: Total seconds.
    """

    hrs, mins, secs = map(int, time.split(':'))
    return hrs * 3600 + mins * 60 + secs

def merge_timestamps(videos):
    """
    Merges embeddings and chunks from videos' timestamp data.

    Args:
        videos (list): List of videos with timestamps.

    Returns:
        tuple: (embeddings (list of numpy arrays), chunks (list of dicts))
    """

    embeddings=[]
    chunks = []
    for video in videos:
        if video.timestamps == []:
            continue
        
        texts = [clean_text(chunk[1]) for chunk in video.timestamps]
        current_embeddings = model.encode(texts, convert_to_tensor=False, show_progress_bar=True)

        embeddings.extend(current_embeddings)
        current_chunks = []
        for i in range(len(video.timestamps)):
            current_chunks.append(dict())
            current_chunks[i]["video_id"] = video.id
            current_chunks[i]["video_title"] = video.title
            current_chunks[i]["video_year"] = int(video.tags['year'])
            current_chunks[i]["text"] = video.timestamps[i][1]
            current_chunks[i]["start"] = convert_time(video.timestamps[i][0])
        chunks.extend(current_chunks)
    return embeddings, chunks

def merge_transcripts(videos):
    """
    Merges embeddings and chunks from videos' transcripts.

    Args:
        videos (list): List of videos with transcript attribute.

    Returns:
        tuple: (embeddings (list of numpy arrays), chunks (list of dicts))
    """

    embeddings=[]
    chunks = []
    for video in videos:
        if video.transcript is None:
            continue
        
        embeddings.extend(load_cache(video.id))
        current_chunks = video.transcript.data
        for i in range(len(current_chunks)):
            current_chunks[i]["video_id"] = video.id
            current_chunks[i]["video_title"] = video.title
            current_chunks[i]["video_year"] = int(video.tags['year'])
        chunks.extend(current_chunks)
    return embeddings, chunks


def semantic_search(query, embeddings, chunks, threshold=0.5, score_offset=0.2):
    """
    Performs semantic search over precomputed embeddings for a query.

    Args:
        query (str): User search query.
        embeddings (numpy.ndarray): Precomputed embeddings.
        chunks (list[dict]): Data corresponding to each embedding.
        threshold (float): Minimum similarity threshold
        score_offset (float): Offset for selecting multiple top matches

    Returns:
        list[dict] or None: Sorted list of matching chunks with scores or None if no match.
    """

    query_lemma = lemmatize(query.lower())
    query_clean = clean_text(query_lemma)

    query_emb = model.encode(query_clean, convert_to_tensor=False)
    embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    query_emb_norm = query_emb / np.linalg.norm(query_emb)
    scores = embeddings_norm @ query_emb_norm

    best_score = np.max(scores)
    if best_score < threshold:
        return None

    best_idxs = [i for i in range(len(scores)) if scores[i] >= max(threshold, best_score - score_offset)]
    if len(best_idxs) > 10:
        best_idxs = [i for i in range(len(scores)) if scores[i] >= max(threshold, best_score - score_offset / 2)]

    results = [chunks[idx] for idx in best_idxs]
    for i in range(len(results)):
        results[i]['score_percent'] = round(float(scores[best_idxs[i]])*100, 2)
    results.sort(key=lambda x: [int(x['video_year']), x['score_percent'], (-1) * int(x['start'])], reverse=True)
    #results.sort(key=lambda x: x['video_year'], reverse=True)

    return results[:min(len(results), 7)]

def make_youtube_url(video_id, timestamp):
    """
    Constructs YouTube URL with timestamp.

    Args:
        video_id (str): Video id.
        timestamp (int): Time offset in seconds.

    Returns:
        str: URL linking to video at specific time.
    """

    mins = int(timestamp) // 60
    secs = int(timestamp) % 60
    if mins == 0:
        time = str(secs) + "s"
    else:
        time = str(mins) + "m" + str(secs) + "s"
    return f"https://www.youtube.com/watch?v={video_id}&t={time}"

def transcript_search(query, videos, precision=0.5):
    """
    Searches in video transcripts and outputs results.

    Args:
        query (str): User search query.
        videos (list): List of video objects with transcripts.
        precision (float): Similarity threshold for filtering.

    Returns:
        list[dict] or None: Search results or None if no matches.
    """

    for video in videos:
        if video.transcript is not None:
          cache_embeddings(video.id, video.transcript.text)

    corrected = yandex_spellcheck(query)
    print("Исправленный запрос:", corrected)

    embeddings, chunks = merge_transcripts(videos)
    results = semantic_search(corrected, embeddings, chunks, threshold=precision)
    print("Поиск по субтитрам:\n")
    if results:
        print(f"Найдено: {len(results)} видео\n")
        cnt = 1
        for result in results:
            print(cnt)
            cnt += 1
            url = make_youtube_url(result['video_id'], result['start'])
            print(f"Видео: {url}")
            print(f"Название: {result['video_title']}")
            print(f"Совпадение: {result['score_percent']}%")
            print(f"Таймкод: {result['start']}")
            print(f"Текст:\n{result['text']}")
            print()
    else:
        print("Совпадений не найдено")

    return results

def timestamp_search(query, videos, precision=0.5):
    """
    Searches in video timestamps and outputs results.

    Args:
        query (str): User search query.
        videos (list): List of video objects with timestamps
        precision (float): Similarity threshold for filtering

    Returns:
        list[dict] or None: Search results or None if no matches.
    """

    corrected = yandex_spellcheck(query)
    print("Исправленный запрос:", corrected)

    print("Поиск по таймкодам:\n")
    embeddings, chunks = merge_timestamps(videos)
    if len(embeddings) == 0:
        print("Таймкоды недоступны")
        return

    results = semantic_search(corrected, embeddings, chunks, threshold=precision)
    if results:
        cnt = 1
        print(f"Найдено: {len(results)} видео\n")
        for result in results:
            print(cnt)
            
            cnt += 1
            url = make_youtube_url(result['video_id'], result['start'])
            print(f"Видео: {url}")
            print(f"Название: {result['video_title']}")
            print(f"Совпадение: {result['score_percent']}%")
            print(f"Таймкод: {result['start']}")
            print(f"Текст:\n{result['text']}")
            print()
    else:
        print("Совпадений не найдено")

    return results

def clear_cache():
    """Deletes all cached embedding files in cache directory after user confirmation."""

    response = input("Are you sure of that?? If so, type 'YES': ")
    if response != "YES":
        return
    
    filenames = os.listdir('/cache')
    for filename in filenames:
        dir = f"cache/{filename}"
        os.remove(dir)
