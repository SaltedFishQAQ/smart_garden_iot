import json

import constants.entity
import constants.rule as const

from typing import Union, Callable, Tuple


def convert_checker(compare, dst: Union[int, float, str]) -> Callable[[Union[float, str]], Tuple[bool, bool]]:
    if isinstance(dst, int):
        dst = float(dst)

    def actuator(src: Union[float, str]) -> Tuple[bool, bool]:
        if isinstance(src, str):
            if isinstance(dst, str) is False:
                return False, False
            # compare content
            if compare == const.COMPARE_EQUAL:
                return src == dst, True
            elif compare == const.COMPARE_NOT_EQUAL:
                return src != dst, True
            else:
                return False, False
        else:
            if isinstance(src, float) is False:
                try:
                    src = float(src)
                except ValueError:
                    return False, False
            if isinstance(dst, float) is False:
                return False, False
            # compare value
            if compare == const.COMPARE_EQUAL:
                return src == dst, True
            elif compare == const.COMPARE_NOT_EQUAL:
                return src != dst, True
            elif compare == const.COMPARE_GREATER_THAN:
                return src > dst, True
            elif compare == const.COMPARE_GREATER_THAN_EQUAL:
                return src >= dst, True
            elif compare == const.COMPARE_LESS_THAN:
                return src < dst, True
            elif compare == const.COMPARE_LESS_THAN_EQUAL:
                return src <= dst, True
            else:
                return False, False

    return actuator


def convert_message(dst, opt):
    if dst == "":
        return "", "", False

    if opt == const.OPT_LIGHT_ON:
        msg = json.dumps({
            'type': 'opt',
            'status': True
        })
    elif opt == const.OPT_LIGHT_OFF:
        msg = json.dumps({
            'type': 'opt',
            'status': False
        })
    else:
        return "", "", False

    return dst, msg, True
