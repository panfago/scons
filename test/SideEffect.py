#!/usr/bin/env python
#
# Copyright (c) 2001, 2002 Steven Knight
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

import TestSCons
import os.path

test = TestSCons.TestSCons()

test.write('SConstruct', 
"""
def copy(source, target):
    print 'copy() < %s > %s' % (source, target)
    open(target, "wb").write(open(source, "rb").read())

def build(env, source, target):
    copy(str(source[0]), str(target[0]))
    if target[0].side_effects:
        side_effect = open(str(target[0].side_effects[0]), "ab")
        side_effect.write('%s -> %s\\n'%(str(source[0]), str(target[0])))

Build = Builder(action=build)
env = Environment(BUILDERS={'Build':Build})
env.Build('foo.out', 'foo.in')
env.Build('bar.out', 'bar.in')
env.Build('blat.out', 'blat.in')
env.SideEffect('log.txt', ['foo.out', 'bar.out', 'blat.out'])
env.Build('log.out', 'log.txt')
""")

test.write('foo.in', 'foo.in\n')
test.write('bar.in', 'bar.in\n')
test.write('blat.in', 'blat.in\n')

test.run(arguments = 'foo.out bar.out', stdout=test.wrap_stdout("""\
copy() < foo.in > foo.out
copy() < bar.in > bar.out
"""))

expect = """\
foo.in -> foo.out
bar.in -> bar.out
"""
assert test.read('log.txt') == expect

test.write('bar.in', 'bar.in 2 \n')

test.run(arguments = 'log.txt', stdout=test.wrap_stdout("""\
copy() < bar.in > bar.out
copy() < blat.in > blat.out
scons: Nothing to be done for `log.txt'.
"""))

expect = """\
foo.in -> foo.out
bar.in -> bar.out
bar.in -> bar.out
blat.in -> blat.out
"""
assert test.read('log.txt') == expect

test.write('foo.in', 'foo.in 2 \n')

test.run(arguments = ".", stdout=test.wrap_stdout("""\
copy() < foo.in > foo.out
copy() < log.txt > log.out
"""))

expect = """\
foo.in -> foo.out
bar.in -> bar.out
bar.in -> bar.out
blat.in -> blat.out
foo.in -> foo.out
"""
assert test.read('log.txt') == expect

test.run(arguments = "-c .")

test.fail_test(os.path.exists(test.workpath('foo.out')))
test.fail_test(os.path.exists(test.workpath('bar.out')))
test.fail_test(os.path.exists(test.workpath('blat.out')))
test.fail_test(os.path.exists(test.workpath('log.txt')))

test.run(arguments = "-j 4 .", stdout=test.wrap_stdout("""\
copy() < bar.in > bar.out
copy() < blat.in > blat.out
copy() < foo.in > foo.out
copy() < log.txt > log.out
"""))

expect = """\
bar.in -> bar.out
blat.in -> blat.out
foo.in -> foo.out
"""
assert test.read('log.txt') == expect

test.write('SConstruct', 
"""
import os.path
import os

def copy(source, target):
    print 'copy() < %s > %s' % (source, target)
    open(target, "wb").write(open(source, "rb").read())

def build(env, source, target):
    copy(str(source[0]), str(target[0]))
    if target[0].side_effects:
        try: os.mkdir('log')
        except: pass
        copy(str(target[0]), os.path.join('log', str(target[0])))

Build = Builder(action=build)
env = Environment(BUILDERS={'Build':Build})
env.Build('foo.out', 'foo.in')
env.Build('bar.out', 'bar.in')
env.Build('blat.out', 'blat.in')
env.SideEffect(Dir('log'), ['foo.out', 'bar.out', 'blat.out'])
""")

test.run(arguments='foo.out')

test.fail_test(not os.path.exists(test.workpath('foo.out')))
test.fail_test(not os.path.exists(test.workpath('log/foo.out')))
test.fail_test(os.path.exists(test.workpath('log/bar.out')))
test.fail_test(os.path.exists(test.workpath('log/blat.out')))

test.run(arguments='log')
test.fail_test(not os.path.exists(test.workpath('log/bar.out')))
test.fail_test(not os.path.exists(test.workpath('log/blat.out')))

test.pass_test()
