#!/usr/bin/env python

import hashlib
import numpy
import random

import matrices

# we number the faces like so: front, left, top, right, bottom, back

# we number the cells on a face as 0-8 from the top-left to the bottom-right.  if there's no
# top/bottom, or no left/right, this is still deterministic because of the handedness.

class rcube():
  MATRICES = matrices.createRCubeMatrices()

  def __init__(self):
    self.cells = numpy.array([0]*9+[1]*9+[2]*9+
                             [3]*9+[4]*9+[5]*9, dtype=numpy.int8)

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
    return hashlib.md5(self.cells).digest()

class solver():
  def __init__(self, cube):
    solvedCube = rcube()

    # we solve by searching all possible positions from the solved direction and the scrambled
    # direction, until they intersect.  The queues are the positions to consider next, with the
    # move depth and last move stored with it in a tuple.
    self.set1 = set([solvedCube.hash()])
    self.queue1 = [(solvedCube, 0, None)]

    self.set2 = set([cube.hash()])
    self.queue2 = [(cube, 0, None)]

  @staticmethod
  def process_(myqueue, myset, otherset, verbose=False):
    c1, depth, lastMove = myqueue.pop(0)
    for i in range(18):
      # skip same face moves
      if lastMove is not None and i%6==lastMove%6:
        continue
      c2 = c1.copy()
      c2.rotate(i)
      id = c2.hash()
      if id in otherset:
        # solved!
        return True
      if id not in myset:
        myset.add(id)
        myqueue.append((c2, depth+1, i))
        if verbose and len(myset)%10000 == 0:
          print('positions: {}, depth: {}'.format(len(myset), depth))

  def solve(self):
    while True:
      if self.process_(self.queue1, self.set1, self.set2, verbose=True):
        break
      if self.process_(self.queue2, self.set2, self.set1, verbose=False):
        break

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
