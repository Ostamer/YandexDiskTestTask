import requests
from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
import os
import mimetypes

YANDEX_API_BASE_URL = 'https://cloud-api.yandex.net/v1/disk/public/resources'
YANDEX_API_DOWNLOAD_URL = 'https://cloud-api.yandex.net/v1/disk/public/resources/download'


class FileListView(View):
    def get(self, request):
        public_key = request.GET.get('public_key')
        if public_key:
            headers = {
                'Authorization': 'y0_AgAAAAA7w-ZuAATuwQAAAAEXSPfVAABi70fr4JdB0JGTf9MNolMU7zIZRw',
            }
            try:
                response = requests.get(YANDEX_API_BASE_URL, params={'public_key': public_key}, headers=headers)
                response.raise_for_status()

                items = response.json().get('_embedded', {}).get('items', [])

                unique_extensions = set()
                for item in items:
                    extension = os.path.splitext(item['name'])[1].lower()
                    unique_extensions.add(extension)
                    item['extension'] = extension

                return render(request, 'file_list.html',
                              {'files': items, 'public_key': public_key, 'extensions': unique_extensions})
            except requests.HTTPError as e:
                return HttpResponse(f"Ошибка при получении данных с Яндекс.Диска: {str(e)}",
                                    status=e.response.status_code)
        return render(request, 'index.html')


class DownloadFileView(View):
    def get(self, request):
        public_key = request.GET.get('public_key')
        file_path = request.GET.get('file_path')
        filename = request.GET.get('filename')

        if public_key and file_path:
            download_url_response = requests.get(
                YANDEX_API_DOWNLOAD_URL,
                params={'public_key': public_key, 'path': file_path}
            )

            if download_url_response.status_code == 200:
                download_url = download_url_response.json().get('href')

                file_response = requests.get(download_url, stream=True)

                if file_response.status_code == 200:
                    if not filename:
                        filename = os.path.basename(file_path)

                    content_type = file_response.headers.get('Content-Type', 'application/octet-stream')
                    extension = mimetypes.guess_extension(content_type) or ''

                    if not filename.endswith(extension):
                        filename += extension

                    http_response = HttpResponse(file_response.content)
                    http_response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    http_response['Content-Type'] = 'application/octet-stream'
                    return http_response

                return HttpResponse("Ошибка: Не удалось загрузить файл", status=file_response.status_code)

            return HttpResponse("Ошибка: Не удалось получить URL для скачивания",
                                status=download_url_response.status_code)

        return HttpResponse("Ошибка: Не указан public_key или путь к файлу", status=400)
