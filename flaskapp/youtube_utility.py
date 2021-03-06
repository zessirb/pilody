from bs4 import BeautifulSoup
import pafy
import urllib


class YoutubeUtility:

    @staticmethod
    def get_youtube_video(youtube_url):
        video = pafy.new(youtube_url)
        video.audio_url = video.getbestaudio().url
        return video

    @staticmethod
    def get_youtube_playlist(playlist_url):
        video_list = pafy.get_playlist2(playlist_url)
        for video in video_list:
            try:
                video.audio_url = video.getbestaudio().url
            except Exception:
                video.audio_url = None
        return video_list

    @staticmethod
    def get_youtube_next_video_url(youtube_url):
        try:
            soup = BeautifulSoup(urllib.request.urlopen(youtube_url))
            next_video_item = soup.find('li', {'class': 'video-list-item'})
            if next_video_item:
                next_video_link = next_video_item.find('a')
                if next_video_link:
                    return 'https://www.youtube.com' + next_video_link.get('href')
        except ValueError:
            pass
