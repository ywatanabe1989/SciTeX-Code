#!/usr/bin/env python3
# Time-stamp: "2024-02-17 12:38:40 (ywatanabe)"

from pprint import pprint as _pprint
from time import sleep

# def get_params(model, tgt_name=None, sleep_sec=2, show=False):

#     name_shape_dict = {}
#     for name, param in model.named_parameters():
#         learnable = "Learnable" if param.requires_grad else "Freezed"

#         if (tgt_name is not None) & (name == tgt_name):
#             return param
#         if tgt_name is None:
#             # print(f"\n{param}\n{param.shape}\nname: {name}\n")
#             if show is True:
#                 print(
#                     f"\n{param}: {param.shape}\nname: {name}\nStatus: {learnable}\n"
#                 )
#                 sleep(sleep_sec)
#             name_shape_dict[name] = list(param.shape)

#     if tgt_name is None:
#         print()
#         _pprint(name_shape_dict)
#         print()


def check_params(model, tgt_name=None, show=False):

    out_dict = {}

    for name, param in model.named_parameters():
        learnable = "Learnable" if param.requires_grad else "Freezed"

        if tgt_name is None:
            out_dict[name] = (param.shape, learnable)

        elif (tgt_name is not None) & (name == tgt_name):
            out_dict[name] = (param.shape, learnable)

        elif (tgt_name is not None) & (name != tgt_name):
            continue

    if show:
        for k, v in out_dict.items():
            print(f"\n{k}\n{v}")

    return out_dict
