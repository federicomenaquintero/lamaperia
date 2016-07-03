import testutils
import re

def inch_to_mm (inch):
    return inch * 25.4

def mm_to_inch (mm):
    return mm / 25.4

def mm_to_pt (mm):
    return mm / 25.4 * 72.0

def pt_to_mm (pt):
    return pt / 72.0 * 25.4

def unity (value):
    return value

units_re = re.compile ("^([-+]?\d*\.?\d+)\s*(\w+)?$")

def parse_units_str (str):
    m = units_re.match (str)
    if m == None:
        return None

    value = m.group (1)
    unit = m.group (2)

    v = float (value)

    if unit == "mm":
        convert = unity
    elif unit == "in":
        convert = inch_to_mm
    elif unit == None:
        convert = unity

    return convert (v)

def parse_units_value (value):
    if isinstance(value, str):
        return parse_units_str (value)
    elif isinstance(value, float):
        return value
    else:
        raise ValueError ("value must be a float or a string")

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

    def test_can_parse_mm (self):
        self.assertFloatEquals (11.0, parse_units_str ("11.0mm"))
        self.assertFloatEquals (-11.0, parse_units_str ("-11 mm"))

    def test_can_parse_inches (self):
        self.assertFloatEquals (inch_to_mm (11.0), parse_units_str ("11in"))
        self.assertFloatEquals (inch_to_mm (-11.0), parse_units_str ("-11.0 in"))

    def test_can_parse_units_without_specifier (self):
        self.assertFloatEquals (11.0, parse_units_str ("11"))
        self.assertFloatEquals (-11.0, parse_units_str ("-11.0"))

    def test_can_parse_float_value (self):
        self.assertFloatEquals (11.0, parse_units_value (11.0))

    def test_can_parse_string_value (self):
        self.assertFloatEquals (11.0, parse_units_value ("11.0"))
        self.assertFloatEquals (11.0, parse_units_value ("11.0 mm"))
        self.assertFloatEquals (inch_to_mm (-11.0), parse_units_value ("-11 in"))
