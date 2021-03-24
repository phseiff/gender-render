
import copy
import unittest

import src.global_capitalization_system as gcs
import src.errors as err


class TestGlobalCapitalizationSystem(unittest.TestCase):

    def test_isupper(self):
        # for upper-cased:

        self.assertTrue(gcs.isupper("WUWU"))  # <-- only upper-case letters
        self.assertTrue(gcs.isupper("WU2U"))  # <-- ^ plus non-capitalizable symbols
        self.assertTrue(gcs.isupper("1111"))  # <-- only non-capitalizable symbols
        self.assertTrue(gcs.isupper(""))  # <-- empty string

        # for non-upper-cased:

        self.assertFalse(gcs.isupper("wuwu"))  # <-- only lower-case letters
        self.assertFalse(gcs.isupper("Wuuu"))  # <-- some lower-case letters
        self.assertFalse(gcs.isupper("Wu11"))  # <-- ^ plus some non-capitalizeable letters

    def test_islower(self):
        # for lower-cased:

        self.assertTrue(gcs.islower("wuwu"))  # <-- only lower-case letters
        self.assertTrue(gcs.islower("wu2u"))  # <-- ^ plus non-capitalizable symbols
        self.assertTrue(gcs.islower("1111"))  # <-- only non-capitalizable symbols
        self.assertTrue(gcs.islower(""))  # <-- empty string

        # for non-lower-cased:

        self.assertFalse(gcs.islower("WUWU"))  # <-- only upper-case letters
        self.assertFalse(gcs.islower("Wuuu"))  # <-- some upper-case letters
        self.assertFalse(gcs.islower("Wu11"))  # <-- ^ plus some non-capitalizable letters

    def test_get_capitalization_from_context_value(self):
        # lower-case:
        self.assertEqual(gcs.get_capitalization_from_context_value("wuwu"), "lower-case")  # <-- standard
        self.assertEqual(gcs.get_capitalization_from_context_value("w   "), "lower-case")  # <-- != alt-studly-caps
        self.assertEqual(gcs.get_capitalization_from_context_value("1w  "), "lower-case")  # <-- != studly-caps
        self.assertEqual(gcs.get_capitalization_from_context_value("1uwu"), "lower-case")  # <-- != capitalized
        self.assertEqual(gcs.get_capitalization_from_context_value("1111"), "lower-case")  # <-- is the default

        # capitalized:
        self.assertEqual(gcs.get_capitalization_from_context_value("Wuwu"), "capitalized")  # <-- standard
        self.assertEqual(gcs.get_capitalization_from_context_value("W   "), "capitalized")  # <-- != all-caps
        self.assertEqual(gcs.get_capitalization_from_context_value("Wu1u"), "capitalized")  # <-- != studly-caps

        # all-caps:
        self.assertEqual(gcs.get_capitalization_from_context_value("WUWU"), "all-caps")  # <-- standard
        self.assertEqual(gcs.get_capitalization_from_context_value("W1W1"), "all-caps")  # <-- != studly-caps
        self.assertEqual(gcs.get_capitalization_from_context_value("1W1W"), "all-caps")  # <-- != alt-studly-caps

        # studly-caps:
        self.assertEqual(gcs.get_capitalization_from_context_value("WuWu"), "studly-caps")  # <-- standard
        self.assertEqual(gcs.get_capitalization_from_context_value("W1Wu"), "studly-caps")  # <-- still valid

        # alt-studly-caps:
        self.assertEqual(gcs.get_capitalization_from_context_value("wUwU"), "alt-studly-caps")  # <-- standard
        self.assertEqual(gcs.get_capitalization_from_context_value("w1wU"), "alt-studly-caps")  # <-- still valid

        # erroneous:
        with self.assertRaises(err.InvalidCapitalizationError):
            gcs.get_capitalization_from_context_value("wuUU")
        # using non-capitalizable symbols won't save this:
        with self.assertRaises(err.InvalidCapitalizationError):
            gcs.get_capitalization_from_context_value("wu1U")

    def test_assign_and_check_capitalization_value_of_tag(self):
        # erroneous inputs:

        # invalid capitalization value:
        with self.assertRaises(err.InvalidCapitalizationError):
            gcs.assign_and_check_capitalization_value_of_tag({"context": "subject", "capitalization": "foo"})
        # invalid capitalization in context value:
        with self.assertRaises(err.InvalidCapitalizationError):
            gcs.assign_and_check_capitalization_value_of_tag({"context": "SUbject"})
        # capitalization value specified, and capitalization is atypical:
        with self.assertRaises(err.InvalidCapitalizationError):
            gcs.assign_and_check_capitalization_value_of_tag({"context": "Subject", "capitalization": "capitalized"})
        # the same thing, but with non-matching context-capitalization and capitalization value:
        with self.assertRaises(err.InvalidCapitalizationError):
            gcs.assign_and_check_capitalization_value_of_tag({"context": "Subject", "capitalization": "lower-case"})
        # multiple (actually, all) of the above:
        with self.assertRaises(err.InvalidCapitalizationError):
            gcs.assign_and_check_capitalization_value_of_tag({"context": "SUbject", "capitalization": "foo"})

        # valid inputs:

        # reading from the context value's capitalization:
        inp = {"context": "subject"}
        out = {"context": "subject", "capitalization": "lower-case"}
        self.assertEqual(gcs.assign_and_check_capitalization_value_of_tag(inp), out)
        # making the context value lower-case in the process:
        inp = {"context": "Subject"}
        out = {"context": "subject", "capitalization": "capitalized"}
        self.assertEqual(gcs.assign_and_check_capitalization_value_of_tag(inp), out)
        # a slightly more complicates case:
        inp = {"context": "W1W"}
        out = {"context": "w1w", "capitalization": "all-caps"}
        self.assertEqual(gcs.assign_and_check_capitalization_value_of_tag(inp), out)

        # reading from the capitalization value:
        inp = {"context": "subject", "capitalization": "all-caps"}
        out = inp
        self.assertEqual(gcs.assign_and_check_capitalization_value_of_tag(inp), out)

        # additional attributes stay unfazed:
        inp = {"context": "subject", "capitalization": "all-caps", "foo": "bar"}
        out = inp
        self.assertEqual(gcs.assign_and_check_capitalization_value_of_tag(inp), out)

    def test_apply_capitalization_to_tag(self):
        # empty string:
        inp1 = {"context": "", "foo": "bar", "capitalization": "lower-case"}
        inp2 = {"context": "", "foo": "bar", "capitalization": "capitalized"}
        inp3 = {"context": "", "foo": "bar", "capitalization": "all-caps"}
        inp4 = {"context": "", "foo": "bar", "capitalization": "studly-caps"}
        inp5 = {"context": "", "foo": "bar", "capitalization": "alt-studly-caps"}
        for inp in [inp1, inp2, inp3, inp4, inp5]:
            backup = copy.deepcopy(inp)
            self.assertEqual(gcs.apply_capitalization_to_tag(inp), "")  # <- check for capitalization correctness
            self.assertEqual(inp, backup)  # <-- make sure the tag isn't modified

        # lower-case:
        pair0 = ({"capitalization": "lower-case", "foo": "bar", "context": "F"}, "f")  # <- length 1
        pair1 = ({"capitalization": "lower-case", "foo": "bar", "context": "f"}, "f")  # <- length 1, but already right
        pair2 = ({"capitalization": "lower-case", "foo": "bar", "context": "foo"}, "foo")  # <- already lower-case
        pair3 = ({"capitalization": "lower-case", "foo": "bar", "context": "FOO"}, "foo")  # <- fully upper-case
        pair4 = ({"capitalization": "lower-case", "foo": "bar", "context": "FoO"}, "foo")  # <- a mixture
        pair5 = ({"capitalization": "lower-case", "foo": "bar", "context": "Fo1"}, "fo1")  # <- plus non-capitalizables
        pair6 = ({"capitalization": "lower-case", "foo": "bar", "context": "111"}, "111")  # <- only non-capitalizables
        for inp, out in [pair0, pair1, pair2, pair3, pair4, pair5, pair6]:
            backup = copy.deepcopy(inp)
            self.assertEqual(gcs.apply_capitalization_to_tag(inp), out)
            self.assertEqual(inp, backup)

        # capitalized:
        pair0 = ({"capitalization": "capitalized", "foo": "bar", "context": "f"}, "F")  # <- length 1
        pair1 = ({"capitalization": "capitalized", "foo": "bar", "context": "F"}, "F")  # <- length 1, but already right
        pair2 = ({"capitalization": "capitalized", "foo": "bar", "context": "foo"}, "Foo")  # <- all lower-case
        pair3 = ({"capitalization": "capitalized", "foo": "bar", "context": "FOO"}, "Foo")  # <- all upper-case
        pair4 = ({"capitalization": "capitalized", "foo": "bar", "context": "FoO"}, "Foo")  # <- a mixture
        pair5 = ({"capitalization": "capitalized", "foo": "bar", "context": "Fo1"}, "Fo1")  # <- plus non-capitalizables
        pair6 = ({"capitalization": "capitalized", "foo": "bar", "context": "fO1"}, "Fo1")  # <- plus non-capitalizables
        pair7 = ({"capitalization": "capitalized", "foo": "bar", "context": "1oo"}, "1oo")  # <- plus non-capitalizables
        pair8 = ({"capitalization": "capitalized", "foo": "bar", "context": "111"}, "111")  # <- only non-capitalizables
        for inp, out in [pair0, pair1, pair2, pair3, pair4, pair5, pair6, pair7, pair8]:
            backup = copy.deepcopy(inp)
            self.assertEqual(gcs.apply_capitalization_to_tag(inp), out)
            self.assertEqual(inp, backup)

        # all-caps:
        pair0 = ({"capitalization": "all-caps", "foo": "bar", "context": "f"}, "F")  # <- length 1
        pair1 = ({"capitalization": "all-caps", "foo": "bar", "context": "F"}, "F")  # <- length 1, but already right
        pair2 = ({"capitalization": "all-caps", "foo": "bar", "context": "foo"}, "FOO")  # <- all lower-case
        pair3 = ({"capitalization": "all-caps", "foo": "bar", "context": "FOO"}, "FOO")  # <- all already upper-case
        pair4 = ({"capitalization": "all-caps", "foo": "bar", "context": "FoO"}, "FOO")  # <- a mixture
        pair5 = ({"capitalization": "all-caps", "foo": "bar", "context": "Fo1"}, "FO1")  # <- plus non-capitalizables
        pair6 = ({"capitalization": "all-caps", "foo": "bar", "context": "111"}, "111")  # <- only non-capitalizables
        for inp, out in [pair0, pair1, pair2, pair3, pair4, pair5, pair6]:
            backup = copy.deepcopy(inp)
            self.assertEqual(gcs.apply_capitalization_to_tag(inp), out)
            self.assertEqual(inp, backup)

        # studly-caps:
        pair0 = ({"capitalization": "studly-caps", "foo": "bar", "context": "f"}, "F")  # <- length 1
        pair1 = ({"capitalization": "studly-caps", "foo": "bar", "context": "F"}, "F")  # <- length 1, but already right
        pair2 = ({"capitalization": "studly-caps", "foo": "bar", "context": "foo"}, "FoO")  # <- all lower-case
        pair3 = ({"capitalization": "studly-caps", "foo": "bar", "context": "FOO"}, "FoO")  # <- all upper-case
        pair4 = ({"capitalization": "studly-caps", "foo": "bar", "context": "fOo"}, "FoO")  # <- a mixture
        pair5 = ({"capitalization": "studly-caps", "foo": "bar", "context": "FoO"}, "FoO")  # <- already right
        pair6 = ({"capitalization": "studly-caps", "foo": "bar", "context": "Fo1"}, "Fo1")  # <- plus non-capitalizables
        pair7 = ({"capitalization": "studly-caps", "foo": "bar", "context": "fO1"}, "Fo1")  # <- plus non-capitalizables
        pair8 = ({"capitalization": "studly-caps", "foo": "bar", "context": "111"}, "111")  # <- only non-capitalizables
        for inp, out in [pair0, pair1, pair2, pair3, pair4, pair5, pair6, pair7, pair8]:
            backup = copy.deepcopy(inp)
            self.assertEqual(gcs.apply_capitalization_to_tag(inp), out)
            self.assertEqual(inp, backup)

        # alt-studly-caps:
        pair0 = ({"capitalization": "alt-studly-caps", "foo": "bar", "context": "F"}, "f")  # <- length 1
        pair1 = ({"capitalization": "alt-studly-caps", "context": "f"}, "f")  # <- length 1, but already right
        pair2 = ({"capitalization": "alt-studly-caps", "foo": "bar", "context": "foo"}, "fOo")  # <- all lower-case
        pair3 = ({"capitalization": "alt-studly-caps", "foo": "bar", "context": "FOO"}, "fOo")  # <- all upper-case
        pair4 = ({"capitalization": "alt-studly-caps", "foo": "bar", "context": "FoO"}, "fOo")  # <- a mixture
        pair5 = ({"capitalization": "alt-studly-caps", "foo": "bar", "context": "fOo"}, "fOo")  # <- already right
        pair6 = ({"capitalization": "alt-studly-caps", "context": "Fo1"}, "fO1")  # <- plus non-capitalizables
        pair7 = ({"capitalization": "alt-studly-caps", "context": "fO1"}, "fO1")  # <- plus non-capitalizables
        pair8 = ({"capitalization": "alt-studly-caps", "context": "111"}, "111")  # <- only non-capitalizables
        for inp, out in [pair0, pair1, pair2, pair3, pair4, pair5, pair6, pair7, pair8]:
            backup = copy.deepcopy(inp)
            self.assertEqual(gcs.apply_capitalization_to_tag(inp), out)
            self.assertEqual(inp, backup)
