import re
import math
import pytest

def inch_to_mm (inch):
    return inch * 25.4

def mm_to_inch (mm):
    return mm / 25.4

def mm_to_pt (mm):
    return mm / 25.4 * 72.0

def pt_to_mm (pt):
    return pt / 72.0 * 25.4

# Parses a string that represents either decimal or sexagesimal
# degrees into a decimal degrees value.  Returns None if invalid.
#
# Valid strings:
#    decimal degrees: -19.234    25.6  (just a regular float number without exponents)
#
#    sexagesimal degrees:
#    15d
#    15d30m
#    15d30m6s
#    all the above can be negative as well.  All need to end in either of d/m/s.

def parse_degrees (value):
    decimal_re = re.compile (r"^[-+]?\d*\.?\d+$")
    if decimal_re.match (value):
        return float(value)

    sexagesimal_re = re.compile (r"^([-+]?\d+)d((\d+)m((\d+)s)?)?$")
    m = sexagesimal_re.match (value)

    if m == None:
        return None

    (deg, min, sec) = m.group (1, 3, 5)

    deg = float (deg)

    if min == None:
        min = 0.0
    else:
        min = float(min)

    if sec == None:
        sec = 0.0
    else:
        sec = float(sec)

    decimals = min / 60.0 + sec / 3600.0

    if deg < 0:
        return deg - decimals
    else:
        return deg + decimals

########## tests ##########

EPSILON = 1e-6

def float_equals (a, b):
    return math.fabs (a - b) < EPSILON

def mm_inch_roundtrip (x):
    assert float_equals (inch_to_mm (mm_to_inch (x)), x)
    assert float_equals (mm_to_inch (inch_to_mm (x)), x)

def test_mm_inch_roundtrip ():
    mm_inch_roundtrip (0)
    mm_inch_roundtrip (1)
    mm_inch_roundtrip (10)

def mm_pt_rountrip (x):
    assert float_equals (mm_to_pt (pt_to_mm (x)), x)
    assert float_equals (pt_to_mm (mm_to_pt (x)), x)

def test_mm_to_pt ():
    mm_inch_roundtrip (0)
    mm_inch_roundtrip (1)
    mm_inch_roundtrip (10)

def test_parse_degrees ():
    assert parse_degrees ("") == None
    assert parse_degrees (" ") == None
    assert float_equals (parse_degrees ("19"), 19)
    assert float_equals (parse_degrees ("-19"), -19)
    assert parse_degrees ("19.5d") == None
    assert float_equals (parse_degrees ("19.5"), 19.5)
    assert float_equals (parse_degrees ("-19.5"), -19.5)
    assert float_equals (parse_degrees ("19d"), parse_degrees ("19.0"))
    assert float_equals (parse_degrees ("-19d"), parse_degrees ("-19.0"))
    assert float_equals (parse_degrees ("19d30m"), parse_degrees ("19.5"))
    assert float_equals (parse_degrees ("-19d30m"), parse_degrees ("-19.5"))
    assert float_equals (parse_degrees ("19d20m15s"), 19 + 20.0 / 60 + 15.0 / 3600)
    assert float_equals (parse_degrees ("-19d20m15s"), -(19 + 20.0 / 60 + 15.0 / 3600))
