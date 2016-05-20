import testutils

def inch_to_mm (inch):
    return inch * 25.4

def mm_to_inch (mm):
    return mm / 25.4

def mm_to_pt (mm):
    return mm / 25.4 * 72.0

def pt_to_mm (pt):
    return pt / 72.0 * 25.4

########## tests ##########

class TestUnitConversions (testutils.TestCaseHelper):
    def mm_inch_roundtrip (self, x):
        self.assertFloatEquals (inch_to_mm (mm_to_inch (x)), x)
        self.assertFloatEquals (mm_to_inch (inch_to_mm (x)), x)

    def test_mm_to_inch_conversion_roundtrips (self):
        self.mm_inch_roundtrip (0)
        self.mm_inch_roundtrip (1)
        self.mm_inch_roundtrip (10)
        self.mm_inch_roundtrip (-1)
        self.mm_inch_roundtrip (-10)

    def mm_pt_roundtrip (self, x):
        self.assertFloatEquals (mm_to_pt (pt_to_mm (x)), x)
        self.assertFloatEquals (pt_to_mm (mm_to_pt (x)), x)

    def test_mm_to_pt_conversion_roundtrips (self):
        self.mm_pt_roundtrip (0)
        self.mm_pt_roundtrip (1)
        self.mm_pt_roundtrip (10)
        self.mm_pt_roundtrip (-1)
        self.mm_pt_roundtrip (-10)
