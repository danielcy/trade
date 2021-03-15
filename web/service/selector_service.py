from core.selector import *
from django.http import HttpResponse
from web.service.web_common import *
from utils.jq_system import *

selector_map = {
    "月K五十金叉选股": MonthGoldenSelector(),
    "RPS 90选股": Rps90Selector(),
    "上行趋势选股": UpGoingSelector(),
    "龙头板块选股": DragonHeadSelector(),
    "同花顺资金抄底选股": BottomFishingSelector(),
}


def get_selectors(request):
    return HttpResponse(get_base_succ_response(list(selector_map.keys())))


def launch_selector(request):
    if request.method == 'POST':
        if request.body:
            d = json.loads(request.body)
            selector_key = d.get('name')
            ts = d.get('ts')
            selector = selector_map[selector_key]
            login()
            pipe = SelectPipeline()
            pipe.chain(selector)
            id = pipe.launch(ts)
            return HttpResponse(get_base_succ_response(id))
        else:
            return HttpResponse(get_base_fail_response(200001, "非法的参数输入"))
    else:
        return HttpResponse(get_base_fail_response(100001, "非法的请求方法"))


def get_selector_result(request):
    if request.method == 'POST':
        if request.body:
            d = json.loads(request.body)
            id = d.get('id')
            pipe = SelectPipeline()
            data = pipe.get_display_result(id)
            return HttpResponse(get_base_succ_response(data))
        else:
            return HttpResponse(get_base_fail_response(200001, "非法的参数输入"))
    else:
        return HttpResponse(get_base_fail_response(100001, "非法的请求方法"))
