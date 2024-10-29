from rest_framework import viewsets
from .models import Message
from .serializers import MessageSerializer
from rest_framework.decorators import api_view
import base64
from django.core.files.storage import default_storage
from rest_framework.response import Response
import os,sys
from django.conf import settings
from PIL import Image
import io

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('-timestamp')
    serializer_class = MessageSerializer

@api_view(['POST'])
def upload_file(request):
    data = request.data  # ��ȡ����������
    base64_image = data.get('base64_image')  # ��ȡ Base64 �ַ���

    if base64_image:
        # ���� Base64 �ַ���
        try:
            format, imgstr = base64_image.split(';base64,')
            ext = format.split('/')[-1]
            image_data = base64.b64decode(imgstr)
            image = Image.open(io.BytesIO(image_data))

            # ����ͼ�������š�����ȣ�
            processed_image_path = 'media/processed_image.' + ext
            image.save(processed_image_path)

            # ���ش�����ͼ�� URL
            file_url = request.build_absolute_uri('/media/' + os.path.basename(processed_image_path))
            return Response({'fileUrl': request.build_absolute_uri(file_url)}, status=201)

        except (ValueError, TypeError) as e:
            return Response({'error': 'Invalid base64 image format.'}, status=400)

    return Response({'error': 'No image data provided.'}, status=400)