"""scons.Node.Python

Python nodes.

"""

#
# __COPYRIGHT__
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import SCons.Node

class Value(SCons.Node.Node):
    """A class for Python variables, typically passed on the command line 
    or generated by a script, but not from a file or some other source.
    """
    def __init__(self, value):
        SCons.Node.Node.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)

    def build(self):
        """A "builder" for Values."""
        pass

    current = SCons.Node.Node.children_are_up_to_date

    def is_under(self, dir):
        # Make Value nodes get built regardless of 
        # what directory scons was run from. Value nodes
        # are outside the filesystem:
        return 1

    def get_contents(self):
        """The contents of a Value are the concatenation
        of all the contents of its sources with the node's value itself."""
        contents = str(self.value)
        for kid in self.children(None):
            contents = contents + kid.get_contents()
        return contents

    def calc_csig(self, calc=None):
        """Because we're a Python value node and don't have a real
        timestamp, we get to ignore the calculator and just use the
        value contents."""
        try:
            binfo = self.binfo
        except AttributeError:
            binfo = self.binfo = self.new_binfo()
        try:
            return binfo.csig
        except AttributeError:
            binfo.csig = self.get_contents()
            self.store_info(binfo)
            return binfo.csig
