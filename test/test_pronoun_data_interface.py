
import unittest
import os
import warnings

import src.warnings as ws
import src.errors as err
from src.pronoun_data_interface import PronounData


class TestPronounData(unittest.TestCase):

    def setUp(self) -> None:
        for f_name in ("valid-grpd.grpd", "valid-grpd.idpd", "valid-grpd.wuwuwu"):
            with open(f_name, "w") as f:
                f.write("""{"foo": {"subject": "they", "object": "them"}}""")
        for f_name in ("valid-idpd.grpd", "valid-idpd.idpd", "valid-idpd.wuwuwu"):
            with open(f_name, "w") as f:
                f.write("""{"subject": "they", "object": "them"}""")
        # these files are invalid in a way that won't be detected unless the pd-parsing-pipeline is properly called!
        #  we can thus use these to test if the pd-parsing-pipeline is properly applied to
        for f_name in ("invalid-grpd.grpd", "invalid-grpd.idpd"):
            with open(f_name, "w") as f:
                f.write("""{"foo": {"subject": "they", "object": 1}}""")
        for f_name in ("invalid-idpd.grpd", "invalid-idpd.idpd"):
            with open(f_name, "w") as f:
                f.write("""{"subject": "they", "object": 1}""")

    def tearDown(self) -> None:
        for f_name in ("valid-grpd.grpd", "valid-grpd.idpd", "valid-grpd.wuwuwu"):
            os.remove(f_name)
        for f_name in ("valid-idpd.grpd", "valid-idpd.idpd", "valid-idpd.wuwuwu"):
            os.remove(f_name)
        for f_name in ("invalid-grpd.grpd", "invalid-grpd.idpd"):
            os.remove(f_name)
        for f_name in ("invalid-idpd.grpd", "invalid-idpd.idpd"):
            os.remove(f_name)

    def test__init__(self):
        # initialize with normal input string:
        pd = PronounData("""{"foo": {"subject": "they", "object": "them"}}""")
        self.assertEqual(pd.get_pd(), {"foo": {"subject": "they", "object": "them"}})
        # and make sure that the pronoun data pipeline is properly applied:
        pd = PronounData("""{"subject": "they", "object": "them"}""")
        self.assertEqual(pd.get_pd(), {"": {"subject": "they", "object": "them"}})
        # and raises the warnings it is supposed to raise:
        with self.assertWarns(ws.UnknownPropertyWarning):
            PronounData("""{"wuwu": "wawa"}""")
        # and raises the errors it is supposed to raise:
        self.assertRaises(err.InvalidPDError, lambda: PronounData("""{"foo": {"wawa": 1}}"""))

        # initialize with normal input dict:
        pd = PronounData({"foo": {"subject": "they", "object": "them"}})
        self.assertEqual(pd.get_pd(), {"foo": {"subject": "they", "object": "them"}})
        # and make sure that the pronoun data pipeline is properly applied:
        pd = PronounData({"subject": "they", "object": "them"})
        self.assertEqual(pd.get_pd(), {"": {"subject": "they", "object": "them"}})
        # and raises the warnings it is supposed to raise:
        with self.assertWarns(ws.UnknownPropertyWarning):
            PronounData({"wuwu": "wawa"})
        # and raises the errors it is supposed to raise:
        self.assertRaises(err.InvalidPDError, lambda: PronounData({"foo": {"wawa": 1}}))

        # initialize with file name - for correct file names:
        with warnings.catch_warnings(record=True) as w:
            pd = PronounData("valid-grpd.grpd", takes_file_path=True)
            self.assertEqual(pd.get_pd(), {"foo": {"subject": "they", "object": "them"}})
            self.assertTrue(len(w) == 0)
        with warnings.catch_warnings(record=True) as w:
            pd = PronounData("valid-idpd.idpd", takes_file_path=True)
            self.assertEqual(pd.get_pd(), {"": {"subject": "they", "object": "them"}})
            self.assertTrue(len(w) == 0)

        # initialize with file name - for incorrect file names:
        with self.assertWarns(ws.UnexpectedFileFormatWarning):
            pd = PronounData("valid-grpd.idpd", takes_file_path=True)
            self.assertEqual(pd.get_pd(), {"foo": {"subject": "they", "object": "them"}})
        with self.assertWarns(ws.UnexpectedFileFormatWarning):
            pd = PronounData("valid-idpd.grpd", takes_file_path=True)
            self.assertEqual(pd.get_pd(), {"": {"subject": "they", "object": "them"}})
        with self.assertWarns(ws.UnexpectedFileFormatWarning):
            pd = PronounData("valid-grpd.wuwuwu", takes_file_path=True)
            self.assertEqual(pd.get_pd(), {"foo": {"subject": "they", "object": "them"}})
        with self.assertWarns(ws.UnexpectedFileFormatWarning):
            pd = PronounData("valid-idpd.wuwuwu", takes_file_path=True)
            self.assertEqual(pd.get_pd(), {"": {"subject": "they", "object": "them"}})

        # test if pronoun data parsing pipeline is properly applied for takes_file_path=True (with all errors risen):
        for f_name in ("invalid-grpd.grpd", "invalid-idpd.grpd", "invalid-grpd.idpd", "invalid-idpd.idpd"):
            self.assertRaises(err.InvalidPDError, lambda: PronounData(f_name, takes_file_path=True))

        # initialize with other pronoun data object:
        pd1 = PronounData({"foo": {"subject": "ze", "object": "zen"}})
        pd2 = PronounData(pd1)
        self.assertEqual(pd1.get_pd(), pd2.get_pd())

        # check if disabling warnings works properly:
        with warnings.catch_warnings(record=True) as w:
            PronounData({"subject": "they", "wuwu": "wawa"}, warning_settings=ws.DISABLE_ALL_WARNINGS)
            self.assertTrue(len(w) == 0)
        ws.WarningManager.set_warning_settings(ws.ENABLE_DEFAULT_WARNINGS)
        # ^ this is only necessary because we use functions that should not be exposed to the user; otherwise, we could
        # just leave it because the next user-exposed function we call will cancel it out anyways.

    def test_get_pd(self):
        # there are no tests for this since the tests for the initialisation test exactly this; whether the input to
        # `__init__` and the output of `get_pd` match.
        pass
