#!/usr/bin/env python

import collections
import itertools
import numpy
import random

import matrices


# we number the faces like so: front, left, top, right, bottom, back
#
# we number the cells on a face as 0-8 from the top-left to the bottom-right.
# if there's no top/bottom, or no left/right, this is still deterministic
# because of the handedness.
class rcube:
    MATRICES = matrices.createRCubeMatrices()

    def __init__(self, initialCells=None):
        self.cells = (initialCells if initialCells is not None else
                      numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0,
                                   1, 1, 1, 1, 1, 1, 1, 1, 1,
                                   2, 2, 2, 2, 2, 2, 2, 2, 2,
                                   3, 3, 3, 3, 3, 3, 3, 3, 3,
                                   4, 4, 4, 4, 4, 4, 4, 4, 4,
                                   5, 5, 5, 5, 5, 5, 5, 5, 5],
                                  dtype=numpy.uint8))

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

    def findsolution(self):
        s = solver(self)
        s.solve()

    def hash(self):
        return tuple(self.cells)


class solver:
    def __init__(self, cube):
        solvedCube = rcube()

        # we solve by searching all possible positions from the solved
        # direction and the scrambled direction, until they intersect.  The
        # queues are the positions to consider next, with the move depth and
        # last move stored with it in a tuple.
        self.set1 = set([solvedCube.hash()])
        self.set2 = set([cube.hash()])
        self.queue = collections.deque([(solvedCube, cube, 0, None)])

    def processNext_(self):
        cube1, cube2, distance, lastmove = self.queue.popleft()

        for i in range(18):
            # never rotate the same face twice in a row
            if lastmove is not None and i % 6 == lastmove % 6:
                continue

            c1 = cube1.rotatecopy(i)
            id1 = c1.hash()

            c2 = cube2.rotatecopy(i)
            id2 = c2.hash()

            if id1 in self.set2 or id2 in self.set1:
                # solved!
                print('solved, positions={}, distance={}'.format(
                    len(self.set1), distance))
                return True

            # if we haven't seen these cubes before, then insert them into the
            # queue.  note that since we're doing the same sequence of moves on
            # both cubes, we expect to have either seen both before, or
            # neither.
            if id1 not in self.set1:
                assert id2 not in self.set2
                self.set1.add(id1)
                self.set2.add(id2)
                self.queue.append((c1, c2, distance+1, i))
                if len(self.set1) % 10000 == 0:
                    print('positions: {}, distance: {}'.format(
                        len(self.set1), distance)
                    )

        return False

    def solve(self):
        while not self.processNext_():
            pass


def solve(movecount=None):
    c = rcube()
    if movecount is None:
        c.scramble()
    else:
        c.scramble(movecount=movecount,
                   deterministic=True)
    print(c)
    c.findsolution()


if __name__ == '__main__':
    solve(12)
    # solve()
