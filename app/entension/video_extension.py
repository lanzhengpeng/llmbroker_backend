import requests

class VideoResult:
    def __init__(self, url, cover_image_url):
        self.url = url
        self.cover_image_url = cover_image_url

    @classmethod
    def from_dict(cls, data):
        return cls(
            url=data.get("url"),
            cover_image_url=data.get("cover_image_url"),
        )

    def __repr__(self):
        return f"VideoResult(url={self.url!r}, cover_image_url={self.cover_image_url!r})"


class VideoObject:
    def __init__(self, id, model, video_result, task_status, request_id):
        self.id = id
        self.model = model
        self.video_result = video_result  # 这里是 List[VideoResult]
        self.task_status = task_status
        self.request_id = request_id

    @classmethod
    def from_dict(cls, data: dict):
        video_result_list = data.get("video_result") or []
        video_result_objs = [VideoResult.from_dict(v) for v in video_result_list]
        return cls(
            id=data.get("id"),
            model=data.get("model"),
            video_result=video_result_objs,
            task_status=data.get("task_status"),
            request_id=data.get("request_id"),
        )

    def __repr__(self):
        return (f"VideoObject(id={self.id!r}, model={self.model!r}, "
                f"video_result={self.video_result!r}, task_status={self.task_status!r}, "
                f"request_id={self.request_id!r})")

class VideoGenerations:

    def __init__(self, client):
        self.client = client

    def __call__(self,
                 model: str,
                 prompt: str,
                 quality: str = "quality",
                 with_audio: bool = True,
                 size: str = "1920x1080",
                 fps: int = 30,
                 image_url: str = None):  # ✅ 新增参数 image_url
        url = f"{self.client.base_url}videos/generations"
        print("Request URL:", url)  # 这里打印url
        headers = {
            "Authorization": f"Bearer {self.client.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "prompt": prompt,
            "quality": quality,
            "with_audio": with_audio,
            "size": size,
            "fps": fps
        }
        if image_url:  # ✅ 可选添加
            payload["image_url"] = image_url

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        # 反序列化成 VideoObject 对象
        video_obj = VideoObject.from_dict(data)
        return video_obj

class VideoRetrieveResult:
    def __init__(self, client):
        self.client = client

    def __call__(self, id: str):
        url = f"{self.client.base_url}videos/retrieve_videos_result"
        headers = {
            "Authorization": f"Bearer {self.client.api_key}",
            "Content-Type": "application/json"
        }
        payload = {"id": id}
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        return VideoObject.from_dict(data)
    
class VideoNamespace:
    def __init__(self, client):
        self.generations = VideoGenerations(client)
        self.retrieve_videos_result = VideoRetrieveResult(client)
