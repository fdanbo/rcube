
import numpy

# change a matrix to rotate the listed elements when dotted
def rotate(mat, elts):
  previous = elts[0]
  for e in elts[1:]:
    mat[previous][previous] = 0
    mat[previous][e] = 1
    previous = e
  mat[previous][previous] = 0
  mat[previous][elts[0]] = 1


def createRCubeMatrices():
  matrices = []

  # rotating the front face
  rot = numpy.identity(54, numpy.int16)
  rotate(rot, [0, 2, 8, 6]);
  rotate(rot, [1, 5, 7, 3]);
  rotate(rot, [11, 26, 33, 36])
  rotate(rot, [14, 25, 30, 37])
  rotate(rot, [17, 24, 27, 38])
  matrices.append(rot)

  # rotating the left face
  rot = numpy.identity(54, numpy.int16)
  rotate(rot, [9, 11, 17, 15]);
  rotate(rot, [10, 14, 16, 12]);
  rotate(rot, [18, 0, 36, 53])
  rotate(rot, [21, 3, 39, 50])
  rotate(rot, [24, 6, 42, 47])
  matrices.append(rot)

  # rotating the top face
  rot = numpy.identity(54, numpy.int16)
  rotate(rot, [18, 20, 26, 24]);
  rotate(rot, [19, 23, 25, 21]);
  rotate(rot, [47, 29, 2, 11])
  rotate(rot, [46, 28, 1, 10])
  rotate(rot, [45, 27, 0, 9])
  matrices.append(rot)

  # rotating the right face
  rot = numpy.identity(54, numpy.int16)
  rotate(rot, [27, 29, 35, 33]);
  rotate(rot, [28, 32, 34, 30]);
  rotate(rot, [26, 45, 44, 8])
  rotate(rot, [23, 48, 41, 5])
  rotate(rot, [20, 51, 38, 2])
  matrices.append(rot)

  # rotating the bottom face
  rot = numpy.identity(54, numpy.int16)
  rotate(rot, [36, 38, 44, 42]);
  rotate(rot, [37, 41, 43, 39]);
  rotate(rot, [6, 33, 51, 15])
  rotate(rot, [7, 34, 52, 16])
  rotate(rot, [8, 35, 53, 17])
  matrices.append(rot)

  # rotating the back face
  rot = numpy.identity(54, numpy.int16)
  rotate(rot, [45, 47, 53, 51]);
  rotate(rot, [46, 50, 52, 48]);
  rotate(rot, [20, 9, 42, 35])
  rotate(rot, [19, 12, 43, 32])
  rotate(rot, [18, 15, 44, 29])
  matrices.append(rot)

  doubleMoveMatrices = []
  leftMoveMatrices = []
  for m in matrices:
    dbl = numpy.dot(m, m)
    doubleMoveMatrices.append(dbl)
    leftMoveMatrices.append(numpy.dot(m, dbl))

  matrices += doubleMoveMatrices
  matrices += leftMoveMatrices

  return matrices
  #return [scipy.sparse.csr_matrix(m) for m in matrices]
