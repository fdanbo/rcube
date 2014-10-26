#!/usr/bin/env python

import cPickle
import cProfile
import multiprocessing
import multiprocessing.queues
import numpy
import redis
import random
import time

import matrices


# we number the faces like so: front, left, top, right, bottom, back
#
# we number the cells on a face as 0-8 from the top-left to the bottom-right.
# if there's no top/bottom, or no left/right, this is still deterministic
# because of the handedness.
class rcube:
    MATRICES = matrices.createRCubeMatrices()
    SOLVED_CELLS = numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0,
                                1, 1, 1, 1, 1, 1, 1, 1, 1,
                                2, 2, 2, 2, 2, 2, 2, 2, 2,
                                3, 3, 3, 3, 3, 3, 3, 3, 3,
                                4, 4, 4, 4, 4, 4, 4, 4, 4,
                                5, 5, 5, 5, 5, 5, 5, 5, 5],
                               dtype=numpy.uint8)

    def __init__(self, initialCells=None):
        self.cells = (initialCells if initialCells is not None
                      else rcube.SOLVED_CELLS.copy())

    def __repr__(self):
        c = self.cells
        s = """
         {:3d}{:3d}{:3d}
         {:3d}{:3d}{:3d}
         {:3d}{:3d}{:3d}
{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}
{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}
{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}{:3d}
         {:3d}{:3d}{:3d}
         {:3d}{:3d}{:3d}
         {:3d}{:3d}{:3d}
""".format(c[18], c[19], c[20], c[21], c[22], c[23], c[24], c[25], c[26], c[9],
           c[10], c[11], c[0], c[1], c[2], c[27], c[28], c[29], c[45], c[46],
           c[47], c[12], c[13], c[14], c[3], c[4], c[5], c[30], c[31], c[32],
           c[48], c[49], c[50], c[15], c[16], c[17], c[6], c[7], c[8], c[33],
           c[34], c[35], c[51], c[52], c[53], c[36], c[37], c[38], c[39],
           c[40], c[41], c[42], c[43], c[44])
        return s

    def clone(self):
        c = rcube()
        c.cells = self.cells.copy()
        return c

    def rotate(self, i):
        self.cells = numpy.dot(self.cells, rcube.MATRICES[i])

    def rotatecopy(self, i):
        return rcube(numpy.dot(self.cells, rcube.MATRICES[i]))

    def rotateinto(self, i, out):
        numpy.dot(self.cells, rcube.MATRICES[i], out=out.cells)

    def rrotateface(self, i):
        self.rotate(i)

    def drotateface(self, i):
        self.rotate(6+i)

    def lrotateface(self, i):
        self.rotate(12+i)

    @staticmethod
    def oppositemove(i):
        if i > 11:
            # left rotation
            return i-12
        elif i > 5:
            # double rotation
            return i
        else:
            # right rotation
            return i+12

    def scramble(self, movecount=1000, deterministic=False):
        if deterministic:
            oldstate = random.getstate()
            random.seed('deterministic seed')

        for i in range(movecount):
            self.rotate(random.randint(0, 17))

        if deterministic:
            random.setstate(oldstate)

    def hash(self):
        return tuple(self.cells)


class RedisQueue:
    def __init__(self, name):
        self.name = name
        self.redis = redis.StrictRedis(db=4)

    def clear(self):
        self.redis.delete(self.name)

    def put(self, val):
        s = cPickle.dumps(val)
        self.redis.rpush(self.name, s)

    def get(self):
        key, s = self.redis.blpop(self.name)
        return cPickle.loads(s)


def rotator_process(stop_event):
    incoming_queue = RedisQueue('r')
    outgoing_queue = RedisQueue('c')
    while not stop_event.is_set():
        twocubes, distance = incoming_queue.get()
        allrotations = numpy.dot(twocubes, rcube.MATRICES)
        for i in range(allrotations.shape[1]):
            outgoing_queue.put((allrotations[:, i], distance+1))


def dup_checker_process(startcubes, stop_event):
    incoming_queue = RedisQueue('c')
    outgoing_queue = RedisQueue('r')
    set1 = {tuple(startcubes[0]): 0}
    set2 = {tuple(startcubes[1]): 0}

    while True:
        twocubes, distance = incoming_queue.get()

        id1 = tuple(twocubes[0])
        id2 = tuple(twocubes[1])

        solved_distance = None
        if id1 in set2:
            solved_distance = set2[id1]
        elif id2 in set1:
            solved_distance = set1[id2]

        if solved_distance is not None:
            # solved! return the (distance, positions_considered)
            stop_event.set()
            return (distance + solved_distance,
                    len(set1) + len(set2))

        if id1 not in set1:
            # not seen before, go ahead and compute rotations
            assert id2 not in set2
            set1[id1] = distance
            set2[id2] = distance
            if len(set1) % 10000 == 0:
                print('{}, depth={}'.format(len(set1), distance))
            outgoing_queue.put((twocubes, distance))


class solver:
    def __init__(self, cube):
        self.twocubes = (rcube.SOLVED_CELLS, cube.cells)
        self.stop_event = multiprocessing.Event()

        process_count = 3

        self.rotator_processes = [
            multiprocessing.Process(
                target=rotator_process,
                args=(self.stop_event,))
            for i in range(process_count)]

    def solve(self):
        starttime = time.time()

        rotate_queue = RedisQueue('r')
        rotate_queue.clear()

        check_queue = RedisQueue('c')
        check_queue.clear()

        rotate_queue.put((self.twocubes, 0))
        for p in self.rotator_processes:
            p.start()
        move_count, positions_considered = 1, 1
        cProfile.runctx(
            'dup_checker_process(self.twocubes, self.stop_event)',
            globals(), {'self': self})

        endtime = time.time()
        rotate_queue.clear()
        check_queue.clear()

        print('solved, moves={}, positions={}'.format(
            move_count, positions_considered))

        total_seconds = (endtime - starttime)
        throughput = positions_considered / total_seconds
        print('throughput: {:.0f} positions/second'.format(throughput))


def solve(movecount=None):
    c = rcube()
    if movecount is None:
        c.scramble()
    else:
        c.scramble(movecount=movecount,
                   deterministic=True)
    print(c)

    s = solver(c)
    s.solve()


if __name__ == '__main__':
    solve(10)
    # solve(12)
    # solve()
