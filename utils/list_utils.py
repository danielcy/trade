import math
import logger


# 两个列表相减，a列表-b列表，若列表长度不一致，短的一方用0填充
def minus_list(a, b):
    len_a = len(a)
    len_b = len(b)
    result = []
    if len_a == len_b:
        for i in range(len_a):
            result.append(a[i] - b[i])
        return result
    temp = []
    temp = fill(temp, 0, abs(len_a - len_b))
    if len_a > len_b:
        temp.extend(b)
        for i in range(len_a):
            result.append(a[i] - temp[i])
    else:
        temp.extend(a)
        for i in range(len_b):
            result.append(temp[i] - b[i])
    return result


def add_list(a, b):
    len_a = len(a)
    len_b = len(b)
    result = []
    if len_a == len_b:
        for i in range(len_a):
            result.append(a[i] + b[i])
        return result
    temp = []
    temp = fill(temp, 0, abs(len_a - len_b))
    if len_a > len_b:
        temp.extend(b)
        for i in range(len_a):
            result.append(a[i] + temp[i])
    else:
        temp.extend(a)
        for i in range(len_b):
            result.append(temp[i] + b[i])
    return result


# 两个列表相除，规则同上
def divide_list(a, b):
    len_a = len(a)
    len_b = len(b)
    result = []
    if len_a == len_b:
        for i in range(len_a):
            if b[i] == 0:
                result.append(999999)
            else:
                result.append(a[i]/b[i])
        return result
    temp = []
    temp = fill(temp, 1, abs(len_a - len_b))
    if len_a > len_b:
        temp.extend(b)
        for i in range(len_a):
            result.append(a[i]/temp[i])
    else:
        temp.extend(a)
        for i in range(len_b):
            result.append(temp[i]/b[i])
    return result


# 列表元素乘以常数
def multiply_num(a, num):
    result = []
    for element in a:
        result.append(element * num)
    return result


#列表元素除以常数
def divide_num(a, num):
    result = []
    for element in a:
        result.append(element / num)
    return result


def abs_list(a):
    c = a.copy()
    result = []
    for element in c:
        result.append(abs(element))
    return result


# 将列表中负数置为0
def clear_negative_number(a):
    c = a.copy()
    for i in range(len(c)):
        if c[i] < 0:
            c[i] = 0
    return c


# 获取N周期内最低值
def llv(a, cnt):
    if cnt == 0:
        result = []
        fill(result, min(a), len(a))
        return result
    result = a.copy()
    for i in range(len(a)):
        if i + 1 < cnt:
            result[i] = min(a[:i+1])
        else:
            result[i] = min(a[i+1-cnt:i+1])
    return result


def ref_list(a, n):
    result = []
    for i in range(n):
        result.append(0)
    result.extend(a[0:-1*n])
    return result


# 获取最新N周期没最高值
def hhv(a, cnt):
    if cnt == 0:
        result = []
        fill(result, max(a), len(a))
        return result
    result = a.copy()
    for i in range(len(a)):
        if i + 1 < cnt:
            result[i] = max(a[:i+1])
        else:
            result[i] = max(a[i+1-cnt:i+1])
    return result


# 用element的值填充列表，填充cnt个
def fill(target, element, cnt):
    for i in range(cnt):
        target.append(element)
    return target


# 如果a中元素不为0返回b元素，否则返回c元素
def if_list(a, b, c):
    if len(a) != len(b) or len(a) != len(c):
        logger.warning("if_list: 列表元素长度不一")
        return []
    result = []
    for i in range(len(a)):
        if a[i] > 0:
            result.append(b[i])
        else:
            result.append(c[i])
    return result

