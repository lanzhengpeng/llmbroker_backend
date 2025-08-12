from openai import OpenAI
from .video_extension import VideoNamespace
class MyOpenAI(OpenAI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.videos = VideoNamespace(self)  # ✅ 挂载 videos
