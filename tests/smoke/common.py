# Copyright 2018 The Bazel Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import subprocess
import sys
import unittest
import zipfile

DEVNULL = open(os.devnull, 'wb')


def _do_exec(command, ignore_error=False, silent=True):
    if silent:
        retcode = subprocess.call(command, stdout=DEVNULL, stderr=DEVNULL)
    else:
        retcode = subprocess.call(command)
    if retcode != 0 and not ignore_error:
        raise Exception("command " + " ".join(command) + " failed")


def _do_exec_expect_fail(command, silent=True):
    if silent:
        retcode = subprocess.call(command, stdout=DEVNULL, stderr=DEVNULL)
    else:
        retcode = subprocess.call(command)
    if retcode == 0:
        raise Exception("command " + " ".join(command) + " should have failed")


class BazelKotlinTestCase(unittest.TestCase):
    _pkg = None
    _last_built_target = ""

    def __init__(self, methodName='runTest'):
        super(BazelKotlinTestCase, self).__init__(methodName)
        os.chdir(subprocess.check_output(["bazel", "info", "workspace"]).replace("\n", ""))
        self._pkg = os.path.dirname(os.path.relpath(sys.modules[self.__module__].__file__))

    def _target(self, target_name):
        if target_name.startswith("//"):
            return target_name
        else:
            return "//%s:%s" % (self._pkg, target_name)

    def _bazel_bin(self, file):
        return "bazel-bin/" + self._pkg + "/" + file

    def _open_bazel_bin(self, file):
        return open(self._bazel_bin(file))

    def _query(self, query, implicits=False):
        res = []
        q = ['bazel', 'query', query]
        if not implicits:
            q.append('--noimplicit_deps')
        self._last_command = " ".join(q)

        p = subprocess.Popen(self._last_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            res.append(line.replace("\n", ""))
        ret = p.wait()
        if ret != 0:
            raise Exception("error (%d) evaluating query: %s" % (ret, self._last_command))
        else:
            return res

    def libQuery(self, label, implicits=False):
        return self._query('\'kind("java_import|.*_library", deps(%s))\'' % label, implicits)

    def assertJarContains(self, jar, *files):
        curr = ""
        try:
            for f in files:
                curr = f
                jar.getinfo(f)
        except Exception as ex:
            self.fail("jar does not contain file [%s]" % curr)

    def assertJarDoesNotContain(self, jar, *files):
        tally = {}
        for n in jar.namelist():
            tally[n] = True
        for f in files:
            self.assertNotIn(f, tally, "jar should not contain file " + f)

    def build(self, target, ignore_error=False, silent=True):

        _do_exec(["bazel", "build", self._target(target)], ignore_error, silent)

    def getWorkerArgsMap(self):
        arg_map = {}
        key = None
        for line in self._open_bazel_bin(self._last_built_target + "-worker.args"):
            line = line.rstrip("\n")
            if not key:
                key = line
            else:
                arg_map[key] = line
                key = None
        return arg_map

    def buildJarExpectingFail(self, target, silent=True):
        self._last_built_target = target
        _do_exec_expect_fail(["bazel", "build", self._target(target)], silent)

    def buildJarGetZipFile(self, target, extension, silent=True):
        jar_file = target + "." + extension
        self._last_built_target = target
        self.build(jar_file, silent=silent)
        return zipfile.ZipFile(self._open_bazel_bin(jar_file))

    def buildLaunchExpectingSuccess(self, target, command="run", ignore_error=False, silent=True):
        self._last_built_target = target
        self.build(target, silent)
        _do_exec(["bazel", command, self._target(target)], ignore_error=ignore_error, silent=silent)