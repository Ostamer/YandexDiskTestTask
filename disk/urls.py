from django.urls import path
from .views import FileListView, DownloadFileView

urlpatterns = [
    path('', FileListView.as_view(), name='index'),
    path('files/', FileListView.as_view(), name='file_list'),
    path('download/', DownloadFileView.as_view(), name='download_file'),
]
