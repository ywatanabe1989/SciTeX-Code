#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2023-03-24 23:13:32 (ywatanabe)"

import readchar
import time
import multiprocessing


def wait_key(p):
    key = "x"
    while key != "q":
        key = readchar.readchar()
        print(key)
    print("q was pressed.")
    p.terminate()
    # event.set()
    # raise Exception


def count():
    counter = 0
    while True:
        print(counter)
        time.sleep(1)
        counter += 1


if __name__ == "__main__":
    p1 = multiprocessing.Process(target=count)

    p1.start()
    waitKey(p1)
    print("aaa")
