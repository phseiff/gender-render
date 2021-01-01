
import unittest
import os
import warnings
import copy

import src.warnings as ws
import src.errors as err
import src.gender_nouns as gn
from src import render_template


class TestInit(unittest.TestCase):

    def setUp(self) -> None:
        # templates:
        for f_name in ("valid.gr", "valid.wuwuwu"):
            with open(f_name, "w") as f:
                f.write("""text test  {obj} text""")
        for f_name in ("invalid.gr", "invalid.wuwuwu"):
            with open(f_name, "w") as f:
                f.write("""text test  {id:fufu} text""")
        # pronoun data:
        for f_name in ("valid.grpd", "valid.fufufu"):
            with open(f_name, "w") as f:
                f.write("""{"foo": {"subject": "they", "object": "them"}}""")
        for f_name in ("invalid.grpd", "invalid.fufufu"):
            with open(f_name, "w") as f:
                f.write("""{"foo": {"subject": "they", "object": 1}}""")

    def tearDown(self) -> None:
        # templates:
        for f_name in ("valid.gr", "valid.wuwuwu"):
            os.remove(f_name)
        for f_name in ("invalid.gr", "invalid.wuwuwu"):
            os.remove(f_name)
        # pronoun data:
        for f_name in ("valid.grpd", "valid.fufufu"):
            os.remove(f_name)
        for f_name in ("invalid.grpd", "invalid.fufufu"):
            os.remove(f_name)

    def test_render_template(self):

        # test with a string as a template and a string as the pd:
        with self.assertWarns(ws.IdMatchingNecessaryWarning):
            # ^ also check if template parsing properly raises warning
            self.assertEqual(render_template(
                "wawa wuwu {id:foo*actor}", """{"gender-nouns": "female"}"""),
                "wawa wuwu actress")
        # ^ this makes sure that the whole render pipeline is called by containing gendered nouns and requiring correct
        # id resolution.

        # test with a string as a template and a dict as the pd:
        with self.assertWarns(ws.UnknownPropertyWarning):
            # ^ also check if pd parsing properly raises warnings
            self.assertEqual(render_template(
                "wawa {id:foo*they} rock", {"foo": {"subj": "xe", "wawa": "xen"}}),
                "wawa xe rock")

        # -- test if errors are risen correctly:

        # in the template:
        self.assertRaises(err.SyntaxError, lambda: render_template("wuwu \\", {}))
        # in the pd:
        self.assertRaises(err.InvalidPDError, lambda: render_template("wuwu", "{"))
        self.assertRaises(err.InvalidPDError, lambda: render_template("wuwu", {"wuwu": 1}))
        # in the pd (given as a string):
        self.assertRaises(err.InvalidPDError, lambda: render_template("wuwu", """{"wuwu": 1}"""))
        # when rendering:
        self.assertRaises(err.IdResolutionError, lambda: render_template("{they}", {}))

        # -- test when using files as input:

        # simple test (with id resolution and warnings):
        with self.assertWarns(ws.IdMatchingNecessaryWarning):
            self.assertEqual(render_template(
                "valid.gr", "valid.grpd", takes_file_path=True),
                "text test  them text")

        # error for invalid gr:
        self.assertRaises(err.SyntaxPostprocessingError, lambda: render_template(
            "invalid.gr", "valid.grpd", takes_file_path=True))
        # error for invalid pd:
        self.assertRaises(err.InvalidPDError, lambda: render_template(
            "valid.gr", "invalid.grpd", takes_file_path=True))
        # error for both pd:
        self.assertRaises((err.InvalidPDError, err.SyntaxPostprocessingError), lambda: render_template(
            "invalid.gr", "invalid.grpd", takes_file_path=True))

        # warning for wrong file type for gr:
        with self.assertWarns(ws.UnexpectedFileFormatWarning):
            render_template("valid.wuwuwu", "valid.grpd", takes_file_path=True)
        # warning for wrong file type in pd:
        with self.assertWarns(ws.UnexpectedFileFormatWarning):
            render_template("valid.gr", "valid.fufufu", takes_file_path=True)

        # properly accept new settings:
        with warnings.catch_warnings(record=True) as w:
            self.assertEqual(render_template(
                "wawa {id:foo*<wu>} rock", {"foo": {"subj": "xe", "_wu": "xen"}},
                warning_settings=ws.DISABLE_ALL_WARNINGS),
                "wawa xen rock")
            self.assertEqual(len(w), 0)
        ws.WarningManager.set_warning_settings(ws.ENABLE_DEFAULT_WARNINGS)
