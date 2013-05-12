
import numpy
import rcube

def main():
  c = rcube.rcube()

  c.scramble()
  testcountidentities(c)
  testrotationalidentities(c)
  print(c)

def testcountidentities(c):
  counts = {}
  for x in c.cells:
    if x not in counts: counts[x] = 0
    counts[x] += 1
  assert(counts[0] == 9)
  assert(counts[1] == 9)
  assert(counts[2] == 9)
  assert(counts[3] == 9)
  assert(counts[4] == 9)
  assert(counts[5] == 9)


def testrotationalidentities(c):
  ################################################################
  # check that four rotates returns to the original state
  id1 = c.id()
  c.rrotateface(0); id2 = c.id()
  c.rrotateface(0); id3 = c.id()
  c.rrotateface(0); id4 = c.id()
  c.rrotateface(0); id5 = c.id()

  assert(id1!=id2)
  assert(id1!=id3)
  assert(id1!=id4)
  assert(id1==id5)
  ################################################################

  ################################################################
  # check that two double rotates returns to the original state
  id1 = c.id()
  c.drotateface(1); id2 = c.id()
  c.drotateface(1); id3 = c.id()
  assert(id1!=id2)
  assert(id1==id3)
  ################################################################

  ################################################################
  # check that four left rotates returns to the original state
  id1 = c.id()
  c.lrotateface(2); id2 = c.id()
  c.lrotateface(2); id3 = c.id()
  c.lrotateface(2); id4 = c.id()
  c.lrotateface(2); id5 = c.id()

  assert(id1!=id2)
  assert(id1!=id3)
  assert(id1!=id4)
  assert(id1==id5)
  ################################################################


if __name__ == '__main__':
  main()

