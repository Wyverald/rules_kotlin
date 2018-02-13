/*
 * Copyright 2018 The Bazel Authors. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package tests.smoke.junittest

import org.junit.*
import org.junit.runner.RunWith
import org.junit.runners.JUnit4
import org.junit.runners.Suite
import java.nio.file.Paths


@RunWith(JUnit4::class)
class JunitTest {
    @Test
    fun dummyTest() {
        if(!Paths.get("tests", "smoke", "data" ,"datafile.txt").toFile().exists()) {
            throw RuntimeException("could not read datafile")
        }
    }
}