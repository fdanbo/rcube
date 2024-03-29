#!/usr/bin/env python

import collections
import numpy
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


class rcubelist:
    def __init__(self, celllists):
        self.matrix = numpy.array(celllists)

    def rotatecopy(self, i):
        return rcubelist(numpy.dot(self.matrix, rcube.MATRICES[i]))

    def gethash(self, n):
        return tuple(self.matrix[n])

    def allrotations(self):
        return numpy.dot(self.matrix, rcube.MATRICES)


class solver:
    def __init__(self, cube):
        # make a list of the start & end points
        cubelist = rcubelist([rcube.SOLVED_CELLS, cube.cells])

        # we solve by searching all possible positions from the solved
        # direction and the scrambled direction, until they intersect.  The
        # queues are the positions to consider next, with the move depth and
        # last move stored with it in a tuple.
        self.set1 = {cubelist.gethash(0): 0}
        self.set2 = {cubelist.gethash(1): 0}
        self.queue = collections.deque([(cubelist, 0, None)])

    def processNext_(self):
        cubelist, distance, lastmove = self.queue.popleft()

        allrotations = cubelist.allrotations()

        for i in range(18):
            # never rotate the same face twice in a row
            if lastmove is not None and i % 6 == lastmove % 6:
                continue

            id1 = tuple(allrotations[0, i])
            id2 = tuple(allrotations[1, i])

            solved_distance = None
            if id1 in self.set2:
                solved_distance = self.set2[id1]
            elif id2 in self.set1:
                solved_distance = self.set1[id2]

            if solved_distance is not None:
                # solved! return the total distance between start and end.
                return distance + solved_distance

            # if we haven't seen these cubes before, then insert them into the
            # queue.  note that since we're doing the same sequence of moves on
            # both cubes, we expect to have either seen both before, or
            # neither.
            if id1 not in self.set1:
                # assert id2 not in self.set2
                self.set1[id1] = distance+1
                self.set2[id2] = distance+1
                self.queue.append(
                    (rcubelist(allrotations[:, i]), distance+1, i))
                if len(self.set1) % 10000 == 0:
                    print('positions: {}, distance: {}'.format(
                        len(self.set1), distance)
                    )

        # was not solved on this iteration
        return False

    def solve(self):
        starttime = time.time()

        while True:
            result = self.processNext_()
            if result is not False:
                move_count = result
                break

        endtime = time.time()
        positions_considered = len(self.set1)+len(self.set2)
        print('solved, positions={}, moves={}'.format(
            positions_considered, move_count))

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
    solve(12)
    # solve()
