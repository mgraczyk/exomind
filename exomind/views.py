from django.http import JsonResponse

from exomind.whitenoise_catchall_middleware import WhiteNoiseCatchAllMiddleware


def catchall(request, **kwargs):
    accept = request.META.get('HTTP_ACCEPT', '').lower()
    if accept and '*/*' not in accept and 'text/html' not in accept:
        return JsonResponse({
            'success': False,
            'message': 'Does not exist',
        },
                            status=404)

    return WhiteNoiseCatchAllMiddleware.serve_file_by_path(request, '/')
