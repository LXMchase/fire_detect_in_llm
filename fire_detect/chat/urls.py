from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, upload_file

router = DefaultRouter()
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', upload_file, name='upload_file'),
]