from rest_framework import viewsets
from .models import Message
from .serializers import MessageSerializer
from rest_framework.decorators import api_view
import base64
from rest_framework.response import Response
import os
from PIL import Image
import io
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('-timestamp')
    serializer_class = MessageSerializer


@api_view(['POST'])
def upload_file(request):
    data = request.data  # ��ȡ����������
    base64_image = data.get('base64_image')  # ��ȡ Base64 �ַ���
    base64_video = data.get('base64_video')  # ��ȡ Base64 �ַ�������Ƶ��

    if base64_image:
        # ����ͼ��
        return process_image(request, base64_image)

    elif base64_video:
        # ������Ƶ
        return process_video(request, base64_video)

    return Response({'error': 'No image or video data provided.'}, status=400)


def process_image(request, base64_image):
    try:
        format, imgstr = base64_image.split(';base64,')
        ext = format.split('/')[-1]
        image_data = base64.b64decode(imgstr)
        image = Image.open(io.BytesIO(image_data))

        # ����ͼ�������š�����ȣ�
        processed_image_path = 'media/temp_image.' + ext
        image.save(processed_image_path)

        # ���ش�����ͼ�� URL
        file_url = request.build_absolute_uri('/media/' + os.path.basename(processed_image_path))
        return Response({'fileUrl': file_url}, status=201)

    except (ValueError, TypeError) as e:
        return Response({'error': 'Invalid base64 image format.'}, status=400)


def process_video(request, base64_video):
    try:
        format, vidstr = base64_video.split(';base64,')
        ext = format.split('/')[-1]
        video_data = base64.b64decode(vidstr)

        # ������Ƶ�ļ�
        processed_video_path = 'media/temp_video.' + ext
        with open(processed_video_path, 'wb') as video_file:
            video_file.write(video_data)

        # ���ش�������Ƶ URL
        file_url = request.build_absolute_uri('/media/' + os.path.basename(processed_video_path))
        return Response({'fileUrl': file_url}, status=201)

    except (ValueError, TypeError) as e:
        return Response({'error': 'Invalid base64 video format.'}, status=400)