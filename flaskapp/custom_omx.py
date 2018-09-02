from queue import Queue, Empty, LifoQueue
from threading import Event, Thread
from time import sleep

import os
from omxplayer.player import OMXPlayer


class CustomOMX:

    def __init__(self):
        self.previous_queue = LifoQueue()
        self.next_queue = Queue()
        self.pause_event = Event()
        self.previous_event = Event()
        self.next_event = Event()
        self.stop_event = Event()
        self.exit_event = Event()
        self.omx_runner = OMXRunner(self.previous_queue, self.next_queue, self.pause_event, self.previous_event,
                                    self.next_event, self.stop_event, self.exit_event)
        self.player_thread = Thread(target=self.omx_runner.run)
        self.player_thread.start()

    def __del__(self):
        self.exit_event.set()

    def set_audio(self, url):
        self.empty_queue()
        self.stop_event.set()
        self.next_queue.put(url)
        self.pause_event.set()

    def add_audio(self, url):
        self.next_queue.put(url)

    def set_playlist(self, url_list):
        self.empty_queue()
        self.stop_event.set()
        for url in url_list:
            self.next_queue.put(url)
        self.pause_event.set()

    def stop(self):
        self.stop_event.set()

    def toggle_pause(self):
        self.pause_event.set()

    def previous(self):
        try:
            previous_music = self.previous_queue.get(False)
        except Empty:
            previous_music = None
        if previous_music:
            next_musics = self.empty_queue()
            next_musics.insert(0, previous_music)
            self.set_playlist(next_musics)

    def next(self):
        self.next_event.set()

    def empty_queue(self):
        queue_content = []
        try:
            queue_element = self.next_queue.get(False)
            while queue_element:
                queue_content.append(queue_element)
                queue_element = self.next_queue.get(False)
        except Empty:
            pass
        return queue_content


class OMXRunner:

    def __init__(self, previous_queue, next_queue, pause_event, previous_event, next_event, stop_event, exit_event):
        self.previous_queue = previous_queue
        self.next_queue = next_queue
        self.pause_event = pause_event
        self.previous_event = previous_event
        self.next_event = next_event
        self.stop_event = stop_event
        self.exit_event = exit_event
        self.player = None
        self.current_music = None

    def run(self):
        while not self.exit_event.is_set():
            sleep(0.05)
            if self.pause_event.is_set():
                self.play_pause()
            if self.stop_event.is_set():
                self.stop()
            if self.previous_event.is_set():
                self.previous()
            if self.next_event.is_set():
                self.next()
            self.try_next()

    def play_pause(self):
        self.stop_event.clear()
        if self.player:
            self.player.play_pause()
        elif self.current_music:
            self.player = OMXPlayer(self.current_music)
        self.pause_event.clear()

    def stop(self):
        if self.player:
            self.player.quit()
            self.player = None

    def previous(self):
        self.stop_event.clear()
        self.stop()

    def next(self):
        self.stop_event.clear()
        self.stop()
        print('next : stopped')
        if self.current_music:
            self.previous_queue.put_nowait(self.current_music)
            print('next : previous : ' + self.current_music)
        try:
            self.current_music = self.next_queue.get_nowait()
            print('next : current : ' + self.current_music)
        except Empty:
            pass
        if self.current_music:
            self.player = OMXPlayer(self.current_music)
        print('next : player created')

    def try_next(self):
        if (not self.player or not self.player.is_playing) and \
                not self.pause_event.is_set() and not self.stop_event.is_set():
            self.next()
