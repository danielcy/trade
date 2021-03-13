from jqdatasdk import *


def get_stock_display_template(codes):
    result = ""
    if isinstance(codes, list):
        for code in codes:
            info = get_security_info(code)
            result = result + "【{}】{}；".format(code, info.display_name)
        return result
    else:
        info = get_security_info(codes)
        result = result + "【{}】{}".format(codes, info.display_name)
        return result
