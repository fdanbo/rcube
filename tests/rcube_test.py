
import collections
import unittest

import rcube


class RCubeTestCase(unittest.TestCase):
    def assert_color_counts(self, c):
        'make sure there are exactly 9 of each color'
        self.assertEqual(len(c.cells), 9*6)

        counts = collections.Counter()
        for x in c.cells:
            counts[x] += 1
        for i in range(6):
            self.assertEqual(counts[i], 9)

    def assert_four_left_rotations(self, c):
        '''rotating the same face four times to the left should leave the cube
        unchanged'''
        # check that four rotates of any face returns to the original state.
        for face in range(6):
            cubes = [c]
            for i in range(4):
                newcube = cubes[-1].clone()
                newcube.lrotateface(face)
                cubes.append(newcube)

            # first & last should match, all others should be different
            for i in range(5):
                for j in range(i+1, 5):
                    if i == 0 and j == 4:
                        self.assertEqual(cubes[i].hash(), cubes[j].hash())
                    else:
                        self.assertNotEqual(cubes[i].hash(), cubes[j].hash())

    def assert_two_double_rotations(self, c):
        '''double-rotating the same face twice should leave the cube
        unchanged'''
        # check that four rotates of any face returns to the original state.
        for face in range(6):
            cubes = [c]
            for i in range(2):
                newcube = cubes[-1].clone()
                newcube.drotateface(face)
                cubes.append(newcube)

            # first & last should match, all others should be different
            for i in range(3):
                for j in range(i+1, 3):
                    if i == 0 and j == 2:
                        self.assertEqual(cubes[i].hash(), cubes[j].hash())
                    else:
                        self.assertNotEqual(cubes[i].hash(), cubes[j].hash())

    def assert_four_right_rotations(self, c):
        '''rotating the same face four times to the right should leave the cube
        unchanged'''
        # check that four rotates of any face returns to the original state.
        for face in range(6):
            cubes = [c]
            for i in range(4):
                newcube = cubes[-1].clone()
                newcube.rrotateface(face)
                cubes.append(newcube)

            # first & last should match, all others should be different
            for i in range(5):
                for j in range(i+1, 5):
                    if i == 0 and j == 4:
                        self.assertEqual(cubes[i].hash(), cubes[j].hash())
                    else:
                        self.assertNotEqual(cubes[i].hash(), cubes[j].hash())

    def assert_cube(self, c):
        'run all the consistency tests on a cube'
        self.assert_color_counts(c)
        self.assert_four_left_rotations(c)
        self.assert_two_double_rotations(c)
        self.assert_four_right_rotations(c)

    def test_cube_identities(self):
        c = rcube.rcube()

        # make each possible rotation once, make sure cube is consistent.
        for i in range(18):
            c.rotate(i)
            self.assert_cube(c)

    def test_cubelist(self):
        for i in range(18):
            c1 = rcube.rcube()
            c2 = rcube.rcube()
            c2.scramble(20)

            c1rotated = c1.rotatecopy(i)
            c2rotated = c2.rotatecopy(i)

            cubelist = rcube.rcubelist([c1.cells, c2.cells])
            self.assertEqual(cubelist.gethash(0), c1.hash())
            self.assertEqual(cubelist.gethash(1), c2.hash())

            rotatedlist = cubelist.rotatecopy(i)
            c1rotated2 = rcube.rcube(rotatedlist.matrix[0])
            c2rotated2 = rcube.rcube(rotatedlist.matrix[1])
            self.assert_cube(c1rotated2)
            self.assert_cube(c2rotated2)
            self.assertEqual(c1rotated.hash(), c1rotated2.hash())
            self.assertEqual(c2rotated.hash(), c2rotated2.hash())

            self.assertEqual(rotatedlist.gethash(0), c1rotated.hash())
            self.assertEqual(rotatedlist.gethash(1), c2rotated.hash())

    def test_allrotations(self):
        c1 = rcube.rcube()
        c2 = rcube.rcube()
        c2.scramble(20)

        cubelist = rcube.rcubelist([c1.cells, c2.cells])
        allrotations = cubelist.allrotations()

        for i, c in enumerate([c1, c2]):
            for j in range(18):
                rotated_cube_1 = c.rotatecopy(j)
                rotated_cube_2 = rcube.rcube(allrotations[i][j])
                self.assert_cube(rotated_cube_2)
                self.assertEqual(rotated_cube_1.hash(), rotated_cube_2.hash())

    def test_scrambled_cubes(self):
        for i in range(100):
            c = rcube.rcube()
            c.scramble()
            self.assert_cube(c)
