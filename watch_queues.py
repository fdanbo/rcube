#!/usr/bin/env python

import redis
import time


def watch_queues():
    r = redis.StrictRedis(db=4)
    while True:
        print('c: {}, r: {}'.format(
            r.llen('c'),
            r.llen('r')))
        time.sleep(2)


if __name__ == '__main__':
    watch_queues()
