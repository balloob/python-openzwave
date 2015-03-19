# Python 2/3 compatibilities
import sys

if sys.hexversion >= 0x3000000:
    def isstr(s):
        return isinstance(s, str)

    from pydispatch import dispatcher
else:
    def isstr(s):
        return isinstance(s, basestring)

    from louie import dispatcher
