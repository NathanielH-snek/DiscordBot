# utils/models.py
from queue import Queue

class Playlist:
    def __init__(self, id: int):
        self.id = id
        self.queue: Queue = Queue(maxsize=0) # maxsize <= 0 means infinite size

    def add_song(self, song: str):
        self.queue.put(song)

    def get_song(self):
        return self.queue.get()

    def empty_playlist(self):
        self.queue.clear()

    @property
    def is_empty(self):
        return self.queue.empty()

    @property
    def track_count(self):
        return self.queue.qsize()