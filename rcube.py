#!/usr/bin/env python

import hashlib
import numpy
import random

import matrices

# we number the faces like so: front, left, top, right, bottom, back

# we number the cells on a face as 0-8 from the top-left to the bottom-right.  if there's no
# top/bottom, or no left/right, this is still deterministic because of the handedness.

class rcube:
  MATRICES = matrices.createRCubeMatrices()

  def __init__(self, initialCells=None):
    self.cells = (initialCells if initialCells is not None else
                  numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0,
                               1, 1, 1, 1, 1, 1, 1, 1, 1,
                               2, 2, 2, 2, 2, 2, 2, 2, 2,
                               3, 3, 3, 3, 3, 3, 3, 3, 3,
                               4, 4, 4, 4, 4, 4, 4, 4, 4,
                               5, 5, 5, 5, 5, 5, 5, 5, 5], dtype=numpy.uint8))

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
""".format(c[18], c[19], c[20], c[21], c[22], c[23], c[24], c[25], c[26],
           c[9], c[10], c[11], c[0], c[1], c[2], c[27], c[28], c[29], c[45], c[46], c[47],
           c[12], c[13], c[14], c[3], c[4], c[5], c[30], c[31], c[32], c[48], c[49], c[50],
           c[15], c[16], c[17], c[6], c[7], c[8], c[33], c[34], c[35], c[51], c[52], c[53],
           c[36], c[37], c[38], c[39], c[40], c[41], c[42], c[43], c[44])
    return s

  def copy(self):
    c = rcube()
    c.cells = self.cells.copy()
    return c

  def rotate(self, i):
    self.cells = numpy.dot(self.cells, rcube.MATRICES[i])

  def rotatecopy(self, i):
    return rcube(numpy.dot(self.cells, rcube.MATRICES[i]))

  def rrotateface(self, i): self.rotate(i)
  def drotateface(self, i): self.rotate(6+i)
  def lrotateface(self, i): self.rotate(12+i)

  @staticmethod
  def oppositemove(i):
    # left rotation
    if i>11: return i-12
    # double rotation
    elif i>5: return i
    # right rotation
    else: return i+12

  def scramble(self, movecount=1000):
    for i in range(movecount):
      self.rotate(random.randint(0, 17))

  def findsolution(self):
    s = solver(self)
    s.solve()

  def hash(self):
    return ''.join([chr(i) for i in self.cells])

class solver:
  def __init__(self, cube):
    solvedCube = rcube()

    # we solve by searching all possible positions from the solved direction and the scrambled
    # direction, until they intersect.  The queues are the positions to consider next, with the
    # move depth and last move stored with it in a tuple.
    self.set1 = set([solvedCube.hash()])
    self.set2 = set([cube.hash()])
    self.queue = [(solvedCube, cube, 0, None)]

  def processNext_(self):
    cube1, cube2, d, lm = self.queue.pop(0)
    for i in range(18):
      # skip same face moves
      if lm is not None and i%6==lm%6:
        continue

      c1 = cube1.rotatecopy(i)
      id1 = c1.hash()

      c2 = cube2.rotatecopy(i)
      id2 = c2.hash()

      if id1 in self.set2 or id2 in self.set1:
        # solved!
        print('solved, p={}, d={}'.format(len(self.set1), d))
        return True

      # we expect either both to be in their sets, or neither
      if id1 not in self.set1:
        assert id2 not in self.set2
        self.set1.add(id1)
        self.set2.add(id2)
        self.queue.append((c1, c2, d+1, i))
        if len(self.set1)%10000 == 0:
          print('positions: {}, depth: {}'.format(len(self.set1), d))
    return False

  def solve(self):
    while not self.processNext_():
      pass

def speedtest1():
  c = rcube()
  for i in range(9):
    c.rotate(i)
  print(c)
  c.findsolution()

def speedtest2():
  c = rcube()
  for i in range(10):
    c.rotate(i)
  print(c)
  c.findsolution()

def solve():
  c = rcube()
  c.scramble()
  c.findsolution()

if __name__ == '__main__':
  speedtest1()
