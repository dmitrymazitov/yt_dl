from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlencode
import socket
import json
import re
from subprocess import run
from os import remove, listdir
import sys


class Youtube:

    __API_URL = "https://www.youtube.com/youtubei/v1"

    __DEFAULT_QUERIES = { 
                        "videoId": None,
                        "key": "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
                        "contentCheckOk": "True",
                        "racyCheckOk":"True"
                        }
    __DATA = data = {
                    'context': 
                            {
                            'client': 
                                    {
                                    'clientName': 'ANDROID', 
                                    'clientVersion': '16.20'
                                    }
                            }
                    }
    __HEADERS = {
                 'Content-Type': 'application/json'
                }

    __DASH_VIDEO = {
    # DASH Video # WEBM
                    "2160p": "313, 315, 337",  
                    "1440p": "271, 308, 336",    
                    "1080p": "170, 248, 303, 335, 399",
                    "720p": "169, 247, 302, 334, 398",
                    "480p": "168, 218, 219, 244, 245, 246, 333",
                    "360p": "167, 243, 332",
                    "240p": "242, 331",
                    "144p": "278, 330"
                   }
    __DASH_VIDEO2 = {
    # DASH Video # MP4
                    "4320p": "402, 571",
                    "2160p": "138, 266, 401",  
                    "1440p": "264, 400",    
                    "1080p": "137, 299, 399",
                    "720p": "136, 298, 398",
                    "480p": "135, 212, 397",
                    "360p": "134, 396",
                    "240p": "133, 395",
                    "144p": "160, 394"
                    }
    

    __slots__= (
                "url",
                "title", 
                "api_url", 
                "video_id", 
                "metadata",
                "itag",
                "list_streams",
                )
    
    def __init__(self, url: str = None): 
        
        self.url : str = self.check_url(url)
        self.video_id : str = self.get_ID(self.url)
        self.api_url :str = self.make_api_url(self.video_id)
        self.metadata: json = self.get_metadata(self.api_url)
        self.title: str = self.extract_title()
        self.list_streams : list = self.extract_streams(self.metadata)
    
    @classmethod
    def execute_request(cls, url: str = None, method: str = None, headers: dict = {}, data: bytes = None):
        _timeout=socket._GLOBAL_DEFAULT_TIMEOUT     
        if data:
            data = bytes(json.dumps(data), encoding="utf-8")
        request = Request(
                        url=url,
                        method=method,
                        headers=headers,
                        data=data,
                        )
        response = urlopen(request, timeout=_timeout)
        if response.code == 200 or response.code == 206:
            return response
        else:
            raise HTTPError

        
    @staticmethod
    def check_url(url: str = None):
        # before we parse, we checking the correct types of url: str
        if not isinstance(url, (str| dict | bytes)): 
            raise TypeError
        if url.startswith("https") or url.startswith("www"):
            return url
        else:
            with URLError as u:
                raise u
    
    @staticmethod
    def get_ID(url: str = None):
        pattern = re.compile(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*")
        id = pattern.search(url).group(1)
        return id

    @classmethod
    def make_api_url(cls, id :str = None):
        cls.__DEFAULT_QUERIES["videoId"] = id
        return "/player?".join((cls.__API_URL, urlencode(cls.__DEFAULT_QUERIES)))

    @classmethod
    def get_metadata(cls, url : str = None):
        post_req = cls.execute_request(
                                       url=url,
                                       method="POST", 
                                       headers=cls.__HEADERS, 
                                       data=cls.__DATA
                                      )
        metadata : json = json.loads(post_req.read().decode("utf-8"))
        return metadata
    
    @classmethod
    def get_itag(cls, resol=None):
        itag = cls.__DASH_VIDEO2[f"{str(resol)}p"]
        return itag

    @staticmethod
    def extract_streams(metadata: json = None):
        list_streams : list = [strm for strm in metadata['streamingData']['adaptiveFormats'] if "video/mp4" in strm["mimeType"] or "audio/mp4" in strm["mimeType"]]
        return list_streams
    
    def choosing_streams(self, itag=None):
        itag = self.get_itag(itag)
        video_audio_links : list = [(link["url"], link["mimeType"], link["contentLength"]) for link in self.list_streams if str(link["itag"]) in itag or link["itag"] == 140]
        if len(video_audio_links) > 2:
            return video_audio_links[-2:]
        else: 
            return video_audio_links

    def extract_title(self):
        lst_letters = "abcdefghijklmnopqrstuvwxyz абвгдеёжзийклмнопрстуфхцчшщъыьэюя 0123456789 []-+=№#%!.,"
        title = self.metadata['videoDetails']['title']
        title_convert = ",".join([i for i in title 
                                 if i in lst_letters or i in lst_letters.upper()]).replace(",", "").replace(" ", "_")
        return title_convert

    def get_chunks(self, url: str = None):
        default_size : int = 9437184 # 9.437.184 bytes
        to_start : int = default_size # starting point of getting chunks
        download = 0
        while True:
            try:
                stop_pos = min(download + default_size, to_start) - 1
                range_header = {"Range": f"bytes={download}-{stop_pos}"}
                response = self.execute_request(
                                                url, 
                                                method="GET", 
                                                headers=range_header
                                                )
                file_size = int(response.info()["Content-Range"].split('/')[1])
                to_start = file_size
                self.progress_bar(list((download, to_start)))
                chunks = response.read()
                download += default_size
                yield chunks
            except HTTPError:
                break
        return

    @staticmethod
    def progress_bar(a_list : list = None):
        t1 = round((a_list[0] * 100) / a_list[-1])
        t2 = round((a_list[0] * 100) / a_list[-1])
        ost2 = 100 - t2
        print('\r', end='')
        print("  Prosessing [%s%s] - %s" % ('#' * t2, "." * ost2, str(t1) + '%'), end='')

    def download(self, resol : str = None):
        self.check_download_file(self.title, resol)
        stream = self.choosing_streams(resol)
        for i in stream:
            url = i[0]
            with open(f"videos/{i[1].split('/')[0]}.{self.title}.mp4", "wb") as f:
                for r in self.get_chunks(url):
                    f.write(r)
            print(" ")
        self.merge_vid_aud_streams(self.title, resol)
        self.delete_vid_aud_streams(self.title)
    
    @staticmethod
    def check_download_file(title : str = None, resol : int = None):
        if f"{title}.{resol}p.mp4" in listdir('/home/jayd/yt_dl/videos/'):
            sys.exit()

    @staticmethod
    def merge_vid_aud_streams(title : str = None, resol : int = None):
        run(f"ffmpeg -i videos/audio.{title}.mp4 -i videos/video.{title}.mp4 -async 1 -c copy videos/{title}.{resol}p.mp4", shell=True)

    @staticmethod
    def delete_vid_aud_streams(title : str = None):
        if "video.{self.title}.mp4" or "audio.{self.title}.mp4" in listdir('/home/jayd/yt_dl/videos/'):
            _ = remove(f"videos/video.{title}.mp4")
            _ = remove(f"videos/audio.{title}.mp4")