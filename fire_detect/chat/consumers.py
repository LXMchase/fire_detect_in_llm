from channels.generic.websocket import AsyncWebsocketConsumer
import json
from http import HTTPStatus
from dashscope import Generation  # 确保已安装 dashscope
import cv2
from django.conf import settings
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from tools.fire_line import process_image_otsu

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        username = data.get('username')
        content = data.get('content')

        if message_type == 'text':
            response_message = await self.handle_text_message(content)
        elif message_type == 'image':
            print("######", content)
            response_message = await self.handle_image_upload(content)
        elif message_type == 'video':
            print("###### Video Content:", content)
            response_message = await self.handle_video_upload(content)  # 新增的视频处理逻辑
        else:
            response_message = "Unknown message type."

        await self.send(text_data=json.dumps({
            'username': 'Server',
            'content': response_message,
            'type': message_type  # 可以传回消息类型
        }))

    def build_file_url(self, file_name):
        # 构建文件的绝对 URL
        host = 'localhost'  # 客户端 IP 地址
        port = 8000  # 客户端端口
        protocol = 'http'  # 可以根据需要选择 'http' 或 'https'
        if port == 443:
            protocol = 'https'

        return f"{protocol}://{host}:{port}/media/{file_name}"
    async def handle_text_message(self, content):
        try:
            # 调用 Generation 来处理文本消息
            responses = Generation.call(
                model="qwen-plus",
                messages=[{'role': 'user', 'content': content}],
                result_format='message',
                stream=True,
                incremental_output=True,
                api_key="sk-xxx"  # 替换为您的 API 密钥
            )

            # 处理响应并返回结果
            response_message = ""
            for response in responses:
                if response.status_code == HTTPStatus.OK:
                    response_message += response.output.choices[0]['message']['content']
                else:
                    response_message += f"Error: {response.status_code} - {response.message}"

            print(response_message)
            return response_message or "No response generated."
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return f"Error calling LLM API: {str(e)}"

    async def handle_image_upload(self, image_url):
        try:
            # 直接使用传入的 image_url，假设它是相对于 MEDIA_URL 的路径
            # 获取文件名
            image_name = os.path.basename(image_url)
            # 构建完整的文件路径
            processed_image_path = os.path.join(settings.MEDIA_ROOT, image_name)
            print("Processing image", processed_image_path)
            # 检查文件是否存在
            if not os.path.exists(processed_image_path):
                return "Image not found."

            # 调用 process_image_otsu 函数处理图像
            processed_image = process_image_otsu(processed_image_path, histogram_folder='', width=50)
            # 获取源文件的扩展名
            _, ext = os.path.splitext(image_name)
            processed_image_name = f"{os.path.splitext(image_name)[0]}_processed{ext}"  # 保持原扩展名
            processed_image_path = os.path.join(settings.MEDIA_ROOT, processed_image_name)

            # 使用 OpenCV 保存处理后的图像
            cv2.imwrite(processed_image_path, processed_image)
            # 构建 URL
            file_url = self.build_file_url(processed_image_name)
            print("file_url", file_url)
            return file_url

        except Exception as e:
            print("Error processing image:", str(e))
            return "Error processing image."

    async def handle_video_upload(self, video_url):
        try:
            # 获取文件名
            video_name = os.path.basename(video_url)
            processed_video_path = os.path.join(settings.MEDIA_ROOT, video_name)
            print("Processing video", processed_video_path)

            # 检查文件是否存在
            if not os.path.exists(processed_video_path):
                return "Video not found."

            # 这里可以添加视频处理逻辑，例如提取缩略图等
            # 例如，假设我们只返回视频的 URL
            file_url = self.build_file_url(video_name)
            return file_url

        except Exception as e:
            print("Error processing video:", e)
            return "Error processing video."