# ToDo: Apparently, the warnings-module's warning catching function is not thread save; feel free to make a pr to
#  replace it with `self.assertWarns` in all tests. Tests that expect no warning to happen could be implemented by
#  stickign a `@unittest.expectedFailure` to them.
#  On 2nd thought, that might not be a good idea for any test except the tests of the `warnings` module, since these are
#  the only multi-threaded tests, and `@unittest.expectedFailure` would require fragmenting the test functions.
