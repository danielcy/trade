from django.http import HttpResponse
from web.service.web_common import *
from playback.main import *
from web import runner, playback_processor


def run_playback(request):
    id = playback_processor.launch()
    return HttpResponse(get_base_succ_response(id))


def get_playback_result(request):
    if request.method == 'POST':
        if request.body:
            d = json.loads(request.body)
            id = d.get('id')
            data = playback_processor.get_result(id)
            return HttpResponse(get_base_succ_response(data))
        else:
            return HttpResponse(get_base_fail_response(200001, "非法的参数输入"))
    else:
        return HttpResponse(get_base_fail_response(100001, "非法的请求方法"))
