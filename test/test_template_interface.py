
import unittest
import os
import warnings
import copy

import src.warnings as ws
import src.errors as err
import src.gender_nouns as gn
from src.pronoun_data_interface import PronounData
from src.template_interface import Template


class TestTemplate(unittest.TestCase):

    def setUp(self) -> None:
        # the content of the files is chosen so that it shows that the whole template parsing pipeline is called and not
        #  just the parser.
        for f_name in ("valid.gr", "valid.wuwuwu"):
            with open(f_name, "w") as f:
                f.write("""text test  {carpenter} text""")
        for f_name in ("invalid.gr", "invalid.wuwuwu"):
            with open(f_name, "w") as f:
                f.write("""text test  {id:fufu} text""")

    def tearDown(self) -> None:
        for f_name in ("valid.gr", "valid.wuwuwu"):
            os.remove(f_name)
        for f_name in ("invalid.gr", "invalid.wuwuwu"):
            os.remove(f_name)

    def test__init__(self):
        # initialize with normal input string:
        template = "text test {they} wuw {id:foo*first-name}"
        tr = Template(template)
        self.assertEqual(tr.parsed_template,
                         ["text test ", {"context": "subject"}, " wuw ", {"id": "foo", "context": "personal-name"}, ""])
        self.assertEqual(tr.contains_unspecified_ids, True)
        self.assertEqual(tr.used_ids, frozenset({"foo"}))
        # for a template where all tags have id values assigned:
        template = "text test {id:bar*they} wuwu {id:foo*first-name}"
        tr = Template(template)
        self.assertEqual(tr.contains_unspecified_ids, False)
        self.assertEqual(tr.used_ids, frozenset({"foo", "bar"}))
        # ^ the tests above also confirm that the template parsing pipeline is applied correctly.
        # raise the warnings you are supposed to raise:
        with self.assertWarns(ws.NotAWordWarning):
            template = "text test {wuwuwu} wuwu"
            tr = Template(template)
            self.assertEqual(tr.parsed_template, ["text test ", {"context": gn.GenderedNoun("wuwuwu")}, " wuwu"])
        # raise an error for invalid input:
        self.assertRaises(err.SyntaxError, lambda: Template("fufufu \\"))
        self.assertRaises(err.SyntaxPostprocessingError, lambda: Template("{fufu*fufa*wuwu}"))

        # initialize with file name - for correct file type:
        with warnings.catch_warnings(record=True) as w:
            tr = Template("valid.gr", takes_file_path=True)
            self.assertEqual(tr.parsed_template,
                             ["text test  ", {"context": gn.GenderedNoun("carpenter")}, " text"])
            self.assertEqual(tr.contains_unspecified_ids, True)
            self.assertEqual(tr.used_ids, frozenset())
            self.assertTrue(len(w) == 0)
        # raises error properly:
        self.assertRaises(err.SyntaxPostprocessingError, lambda: Template("invalid.gr", takes_file_path=True))

        # initialize with file name - for incorrect file type:
        with self.assertWarns(ws.UnexpectedFileFormatWarning):  # <- raises warning
            tr = Template("valid.wuwuwu", takes_file_path=True)
            "{text test  {carpenter} text"
            self.assertEqual(tr.parsed_template,
                             ["text test  ", {"context": gn.GenderedNoun("carpenter")}, " text"])
            self.assertEqual(tr.contains_unspecified_ids, True)
            self.assertEqual(tr.used_ids, frozenset())
        # raises error properly:
        with warnings.catch_warnings(record=True) as w:
            self.assertRaises(err.SyntaxPostprocessingError, lambda: Template("invalid.wuwuwu", takes_file_path=True))

        # check if disabling warnings works properly:
        with warnings.catch_warnings(record=True) as w:
            Template("{wuwu}", warning_settings=ws.DISABLE_ALL_WARNINGS)
            self.assertTrue(len(w) == 0)
        ws.WarningManager.set_warning_settings(ws.ENABLE_DEFAULT_WARNINGS)

    def test_render(self):
        tr = Template("wuwu wawa {id:foo * context:they} tsts {them}")
        # ^ this is chosen in a way that proves that we walk through the rendering pipeline directly as it requires
        #  id resolution.

        parsed_template_backup = copy.deepcopy(tr.parsed_template)

        # the following tests also check if warnings are raised correctly:

        # parse directly with pd in string form:
        with self.assertWarns(ws.IdMatchingNecessaryWarning):
            self.assertEqual(tr.render("""{"foo": {"subj": "ze"}, "bar": {"them": "zen"}}"""), "wuwu wawa ze tsts zen")

        # parse directly with pd in dict form:
        with self.assertWarns(ws.IdMatchingNecessaryWarning):
            self.assertEqual(tr.render({"foo": {"subj": "ze"}, "bar": {"them": "zen"}}), "wuwu wawa ze tsts zen")

        # parse from a PronounData-object:
        with self.assertWarns(ws.IdMatchingNecessaryWarning):
            self.assertEqual(tr.render(PronounData({"foo": {"subj": "ze"}, "bar": {"them": "zen"}})),
                             "wuwu wawa ze tsts zen")

        # parse from a file:
        with open("test.grpd", "w") as f:
            f.write("""{"foo": {"subj": "ze"}, "bar": {"them": "zen"}}""")
        with self.assertWarns(ws.IdMatchingNecessaryWarning):
            self.assertEqual(tr.render("test.grpd", takes_file_path=True), "wuwu wawa ze tsts zen")
        os.remove("test.grpd")

        # parse from a file with wrong file name:
        with self.assertWarns(ws.UnexpectedFileFormatWarning):
            with open("test.wuwuwu", "w") as f:
                f.write("""{"foo": {"subj": "ze"}, "bar": {"them": "zen"}}""")
            self.assertEqual(tr.render("test.wuwuwu", takes_file_path=True), "wuwu wawa ze tsts zen")
            os.remove("test.wuwuwu")

        # check if errors are raised properly:
        self.assertRaises(err.IdResolutionError, lambda: tr.render({}))

        # check if parsed pronoun data was not modified by all of this:
        self.assertEqual(tr.parsed_template, parsed_template_backup)

        # check if pronoun data objects are not modified by the rendering process, either:
        pd = PronounData({"foo": {"subj": "ze"}, "bar": {"them": "zen"}})
        pd_backup = copy.deepcopy(pd.get_pd())
        with self.assertWarns(ws.IdMatchingNecessaryWarning):
            tr.render(pd)
        self.assertEqual(pd.get_pd(), pd_backup)

        # check if warnings can be disabled correctly:
        with warnings.catch_warnings(record=True) as w:
            tr.render(pd, warning_settings=ws.DISABLE_ALL_WARNINGS)
            self.assertEqual(w, [])
        ws.WarningManager.set_warning_settings(ws.ENABLE_DEFAULT_WARNINGS)
