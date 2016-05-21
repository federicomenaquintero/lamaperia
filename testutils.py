import unittest
import math

EPSILON = 1e-6

class TestCaseHelper (unittest.TestCase):
    def assertFloatEquals (self, a, b):
        self.assertTrue (math.fabs (a - b) < EPSILON)
