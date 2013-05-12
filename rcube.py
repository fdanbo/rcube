
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
                             [3]*9+[4]*9+[5]*9, dtype=numpy.int16)
    # self.cells = scipy.sparse.csr_matrix(self.cells)
    # TODO: consider an API for creating this cube instead for testing
    # self.cells = numpy.array(range(54), dtype=numpy.int16)

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

  def scramble(self):
    for i in range(1000):
      self.rotate(random.randint(0, 17))

  def findsolution(self):
    solvedCubeQueue = [rcube()]
    solvedIDSet = set(x.hash() for x in solvedCubeQueue)

    myCubeQueue = [self.copy()]
    myCubeIDSet = set(x.hash() for x in myCubeQueue)

    while True:
      c1 = solvedCubeQueue.pop(0)
      for i in range(18):
        c2 = c1.copy()
        c2.rotate(i)
        id = c2.hash()
        if id in myCubeIDSet:
          print('solved from solved side!')
          break
        if id not in solvedIDSet:
          solvedIDSet.add(id)
          solvedCubeQueue.append(c2)
          if len(solvedIDSet)%10000 == 0:
            print('s1: {n}'.format(n=len(solvedIDSet)))

      c1 = myCubeQueue.pop(0)
      for i in range(18):
        c2 = c1.copy()
        c2.rotate(i)
        id = c2.hash()
        if id in solvedIDSet:
          print('solved from my side!')
          break
        if id not in myCubeIDSet:
          myCubeIDSet.add(id)
          myCubeQueue.append(c2)
          if len(myCubeIDSet)%10000 == 0:
            print('s2: {n}'.format(n=len(myCubeIDSet)))

  def id(self):
    return sum([int(x)<<(i*3) for i,x in enumerate(self.cells)])

  def hash(self):
    return hashlib.md5(self.cells)


def main():
  c = rcube()
  c.scramble()
  c.findsolution()

def search():
  idset = set()
  cubeQueue = [(rcube(), 0)]
  highestDistance = 1
  while len(cubeQueue)>0:
    currentCube, d = cubeQueue.pop(0)
    if d>highestDistance:
      highestDistance = d
      print("distance: {d}".format(d=d))
      print("positions: {p}".format(p=len(idset)))
    for i in range(6):
      c = currentCube.copy()
      c.rotate(i)
      id = c.id()
      if id not in idset:
        idset.add(id)
        cubeQueue.append((c, d+1))

if __name__ == '__main__':
  main()
