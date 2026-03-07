import traceback
import sys
from django.http import JsonResponse


def api_success(data=None, message='Operacao realizada com sucesso', status_code=200, page_info=None, stats=None):
    response = {
        'data': data,
        'status': {
            'code': status_code,
            'message': message,
        },
        'page': page_info,
        'stats': stats,
    }
    return JsonResponse(response, status=status_code)


def api_error(message='Erro ao processar requisicao', status_code=400):
    return JsonResponse({
        'data': None,
        'status': {
            'code': status_code,
            'message': message,
        },
        'page': None,
    }, status=status_code)


def api_form_error(form, message='Corrija os erros no formulario'):
    field_errors = []
    for field, errors in form.errors.items():
        field_errors.append({
            'field': field,
            'messages': list(errors),
        })
    return JsonResponse({
        'data': field_errors,
        'status': {
            'code': 400,
            'message': message,
        },
        'page': None,
    }, status=400)


def api_exception(request, source, message='Erro interno do servidor'):
    exc_info = sys.exc_info()
    trace_str = traceback.format_exc() if exc_info[0] else ''

    try:
        from systemlogs.models import SystemLog
        SystemLog.objects.create(
            level='ERROR',
            source=source,
            message=str(exc_info[1]) if exc_info[1] else message,
            trace=trace_str,
            request_method=request.method if request else None,
            request_path=request.path if request else None,
            user=request.user if request and request.user.is_authenticated else None,
        )
    except Exception:
        pass

    return JsonResponse({
        'data': None,
        'status': {
            'code': 500,
            'message': message,
        },
        'page': None,
    }, status=500)


def log_system_event(level, source, message, trace=None, request=None):
    try:
        from systemlogs.models import SystemLog
        SystemLog.objects.create(
            level=level,
            source=source,
            message=message,
            trace=trace,
            request_method=request.method if request else None,
            request_path=request.path if request else None,
            user=request.user if request and hasattr(request, 'user') and request.user.is_authenticated else None,
        )
    except Exception:
        pass
