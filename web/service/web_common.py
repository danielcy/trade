import json


def get_base_succ_response(data):
    result = {"success": True, "error_code": 0, "error_msg": "", "result": data}
    return json.dumps(result, ensure_ascii=False)


def get_base_fail_response(error_code, error_message):
    result = {"success": True, "error_code": error_code, "error_msg": error_message}
    return json.dumps(result, ensure_ascii=False)