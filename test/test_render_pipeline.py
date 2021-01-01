
import unittest
import warnings
import copy

import src.warnings as ws
import src.errors as err
import src.gender_nouns as gn
from src.render_pipeline import GRenderer


class TestGRenderer(unittest.TestCase):

    @staticmethod
    def grpd_are_different(grpd1, grpd2):
        # tests if the two passed grpds are different, in that all mutable objects they contain have different
        #  identities in both.
        dict_ids_1 = set(id(d) for d in grpd1.values())
        dict_ids_2 = set(id(d) for d in grpd2.values())
        if dict_ids_1 & dict_ids_2:
            return False
        return True

    @staticmethod
    def templates_are_different(template1, template2):
        # tests if the passed templates are different, in that all mutable objects they contain have different
        #  identities in both.
        tag_ids_1 = set(id(template1[t]) for t in range(1, len(template1), 2))
        tag_ids_2 = set(id(template2[t]) for t in range(1, len(template2), 2))
        if tag_ids_1 & tag_ids_2:
            return False
        list_ids_1 = set(id(v) for t in range(1, len(template1), 2)
                         for v in template1[t].values() if type(template1[t]) is list)
        list_ids_2 = set(id(v) for t in range(1, len(template2), 2)
                         for v in template1[t].values() if type(template2[t]) is list)
        if list_ids_1 & list_ids_2:
            return False
        return True

    def check_run_aftermath(self, pd1, pd2, template1, template2, pd1_original, template1_original):
        # make sure that the resulting pd is id-different to the input-pd, the resulting template is id-different to the
        #  input template, and the input pd template and template are not different than the deepcopied backups of them.
        self.assertTrue(self.grpd_are_different(pd1, pd2))
        self.assertTrue(self.templates_are_different(template1, template2))
        self.assertEqual(pd1, pd1_original)
        self.assertEqual(template1, template1_original)

    def test_id_resolution(self):
        # we make one test case for every cell of the table that defines the workings of id resolution.
        # we only test inputs that could've validly come out of the template- and pronoun data parsing pipeline.

        # -- only idpd given:

        pd1 = {"": {"foo": "bar", "wuwu": "wawa"}}
        pd1_original = copy.deepcopy(pd1)

        # #ids = 0:
        with warnings.catch_warnings(record=True) as w:
            template1 = ["text", {"a": "b"}, " text ", {"d": "e"}, " test"]
            template1_original = copy.deepcopy(template1)
            ids = frozenset()
            unspecified_ids = True
            template2, pd2 = GRenderer.id_resolution(template1, ids, unspecified_ids, pd1)
            # check result:
            self.assertEqual(template2, ["text", {"a": "b", "id": "usr"}, " text ", {"d": "e", "id": "usr"}, " test"])
            self.assertEqual(pd2, {"usr": {"foo": "bar", "wuwu": "wawa"}})
            # make sure the result does not reference parts of the original, and the original is unmodified:
            self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)
            # make sure a warning was properly raised:
            self.assertTrue(len(w) == 1 and issubclass(w[-1].category, ws.IdMatchingNecessaryWarning))

        # all ids are equal:
        with warnings.catch_warnings(record=True) as w:
            template1 = ["text", {"a": "b", "id": "bar"}, " text ", {"d": "e", "id": "bar"}, " test"]
            template1_original = copy.deepcopy(template1)
            ids = frozenset({"bar"})
            unspecified_ids = False
            template2, pd2 = GRenderer.id_resolution(template1, ids, unspecified_ids, pd1)
            # check result:
            self.assertEqual(template2, template1)
            self.assertEqual(pd2, {"bar": {"foo": "bar", "wuwu": "wawa"}})
            # make sure the result does not reference parts of the original, and the original is unmodified:
            self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)
            # make sure a warning was properly raised:
            self.assertTrue(len(w) == 1 and issubclass(w[-1].category, ws.IdMatchingNecessaryWarning))

        # all tags have ids, yet not all have the same ids:
        template1 = ["text", {"a": "b", "id": "bar"}, " text ", {"d": "e", "id": "foo"}, " test"]
        template1_original = copy.deepcopy(template1)
        ids = frozenset({"bar", "foo"})
        unspecified_ids = False
        self.assertRaises(err.IdResolutionError, lambda: GRenderer.id_resolution(template1, ids, unspecified_ids, pd1))
        # make sure the result does not reference parts of the original, and the original is unmodified:
        self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)

        # some tags have ids, but not all:
        template1 = ["text", {"a": "b", "id": "bar"}, " text ", {"d": "e"}, " test"]
        template1_original = copy.deepcopy(template1)
        ids = frozenset({"bar"})
        unspecified_ids = True
        self.assertRaises(err.IdResolutionError, lambda: GRenderer.id_resolution(template1, ids, unspecified_ids, pd1))
        # make sure the result does not reference parts of the original, and the original is unmodified:
        self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)

        # -- only one id ("foo") in the whole grpd:

        pd1 = {"foo": {"foo": "bar", "wuwu": "wawa"}}
        pd1_original = copy.deepcopy(pd1)

        # #ids = 0:
        with warnings.catch_warnings(record=True) as w:
            template1 = ["text", {"a": "b"}, " text ", {"d": "e"}, " test"]
            template1_original = copy.deepcopy(template1)
            ids = frozenset()
            unspecified_ids = True
            template2, pd2 = GRenderer.id_resolution(template1, ids, unspecified_ids, pd1)
            # check result:
            self.assertEqual(template2, ["text", {"a": "b", "id": "foo"}, " text ", {"d": "e", "id": "foo"}, " test"])
            self.assertEqual(pd2, pd1)
            # make sure the result does not reference parts of the original, and the original is unmodified:
            self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)
            # make sure a warning was properly raised:
            self.assertTrue(len(w) == 1 and issubclass(w[-1].category, ws.IdMatchingNecessaryWarning))

        # all ids are equal ("bar"):
        template1 = ["text", {"a": "b", "id": "bar"}, " text ", {"d": "e", "id": "bar"}, " test"]
        template1_original = copy.deepcopy(template1)
        ids = frozenset({"bar"})
        unspecified_ids = False
        self.assertRaises(err.IdResolutionError, lambda: GRenderer.id_resolution(template1, ids, unspecified_ids, pd1))
        # make sure the result does not reference parts of the original, and the original is unmodified:
        self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)

        # all ids are equal ("foo"):
        template1 = ["text", {"a": "b", "id": "foo"}, " text ", {"d": "e", "id": "foo"}, " test"]
        template1_original = copy.deepcopy(template1)
        ids = frozenset({"foo"})
        unspecified_ids = False
        template2, pd2 = GRenderer.id_resolution(template1, ids, unspecified_ids, pd1)
        # check result:
        self.assertEqual(template2, template1)
        self.assertEqual(pd2, {"foo": {"foo": "bar", "wuwu": "wawa"}})
        # make sure the result does not reference parts of the original, and the original is unmodified:
        self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)
        # make sure a warning was properly raised:

        # all tags have ids, yet not all have the same ids:
        template1 = ["text", {"a": "b", "id": "bar"}, " text ", {"d": "e", "id": "foo"}, " test"]
        template1_original = copy.deepcopy(template1)
        ids = frozenset({"bar", "foo"})
        unspecified_ids = False
        self.assertRaises(err.IdResolutionError, lambda: GRenderer.id_resolution(template1, ids, unspecified_ids, pd1))
        # make sure the result does not reference parts of the original, and the original is unmodified:
        self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)

        # some tags have ids, but not all:
        template1 = ["text", {"a": "b", "id": "bar"}, " text ", {"d": "e"}, " test"]
        template1_original = copy.deepcopy(template1)
        ids = frozenset({"bar"})
        unspecified_ids = True
        self.assertRaises(err.IdResolutionError, lambda: GRenderer.id_resolution(template1, ids, unspecified_ids, pd1))
        # make sure the result does not reference parts of the original, and the original is unmodified:
        self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)

        # -- pronoun data is given for multiple ids

        pd1 = {"foo": {"foo": "bar", "wuwu": "wawa"}, "bar": {"foo": "bar", "wuwu": "wawa"}}
        pd1_original = copy.deepcopy(pd1)

        # #ids = 0:
        template1 = ["text", {"a": "b"}, " text ", {"d": "e"}, " test"]
        template1_original = copy.deepcopy(template1)
        ids = frozenset()
        unspecified_ids = True
        self.assertRaises(err.IdResolutionError, lambda: GRenderer.id_resolution(template1, ids, unspecified_ids, pd1))
        # make sure the result does not reference parts of the original, and the original is unmodified:
        self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)

        # all tag have the same id - and it is mentioned in the pronoun data:
        with warnings.catch_warnings(record=True) as w:
            template1 = ["text", {"a": "b", "id": "bar"}, " text ", {"d": "e", "id": "bar"}, " test"]
            template1_original = copy.deepcopy(template1)
            ids = frozenset({"bar"})
            unspecified_ids = False
            template2, pd2 = GRenderer.id_resolution(template1, ids, unspecified_ids, pd1)
            # check result:
            self.assertEqual(template2, template1)
            self.assertEqual(pd2, pd1)
            # make sure the result does not reference parts of the original, and the original is unmodified:
            self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)
            # make sure no warning was raised:
            self.assertTrue(len(w) == 0)

        # all tag have the same id - and it is not mentioned in the pronoun data:
        template1 = ["text", {"a": "b", "id": "baz"}, " text ", {"d": "e", "id": "baz"}, " test"]
        template1_original = copy.deepcopy(template1)
        ids = frozenset({"baz"})
        unspecified_ids = False
        self.assertRaises(err.IdResolutionError, lambda: GRenderer.id_resolution(template1, ids, unspecified_ids, pd1))
        # make sure the result does not reference parts of the original, and the original is unmodified:
        self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)

        # all tags have ids, yet not all have the same ids - and they are identical to those in the given pd:
        with warnings.catch_warnings(record=True) as w:
            template1 = ["text", {"a": "b", "id": "bar"}, " text ", {"d": "e", "id": "foo"}, " test"]
            template1_original = copy.deepcopy(template1)
            ids = frozenset({"bar", "foo"})
            unspecified_ids = False
            template2, pd2 = GRenderer.id_resolution(template1, ids, unspecified_ids, pd1)
            # check result:
            self.assertEqual(template2, template1)
            self.assertEqual(pd2, pd1)
            # make sure the result does not reference parts of the original, and the original is unmodified:
            self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)
            # make sure no warning was raised:
            self.assertTrue(len(w) == 0)

        # all tags have ids, yet not all have the same ids - and they are a subset to those in the given pd:
        with warnings.catch_warnings(record=True) as w:
            pd1_b = {"foo": {"foo": "bar", "wuwu": "wawa"}, "bar": {"foo": "bar", "wuwu": "wawa"}, "baz": {"foo": "ba"}}
            pd1_b_original = copy.deepcopy(pd1_b)
            template1 = ["text", {"a": "b", "id": "bar"}, " text ", {"d": "e", "id": "foo"}, " test"]
            template1_original = copy.deepcopy(template1)
            ids = frozenset({"bar", "foo"})
            unspecified_ids = False
            template2, pd2 = GRenderer.id_resolution(template1, ids, unspecified_ids, pd1_b)
            # check result:
            self.assertEqual(template2, template1)
            self.assertEqual(pd2, pd1_b)
            # make sure the result does not reference parts of the original, and the original is unmodified:
            self.check_run_aftermath(pd1_b, pd2, template1, template2, pd1_b_original, template1_original)
            # make sure no warning was raised:
            self.assertTrue(len(w) == 0)

        # all tags have ids, yet not all have the same ids - and they differ from those in the given pd:
        template1 = ["text", {"a": "b", "id": "bar"}, " text ", {"d": "e", "id": "baz"}, " test"]
        template1_original = copy.deepcopy(template1)
        ids = frozenset({"bar", "baz"})
        unspecified_ids = False
        self.assertRaises(err.IdResolutionError, lambda: GRenderer.id_resolution(template1, ids, unspecified_ids, pd1))
        # make sure the result does not reference parts of the original, and the original is unmodified:
        self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)

        # some tags have ids, but not all - but the amount doesn't fit:
        template1 = ["text", {"a": "b", "id": "bar"}, " text ", {"d": "e"}, " test ", {"d": "e", "id": "foo"},
                     " test"]
        template1_original = copy.deepcopy(template1)
        ids = frozenset({"bar", "foo"})
        unspecified_ids = True
        self.assertRaises(err.IdResolutionError, lambda: GRenderer.id_resolution(template1, ids, unspecified_ids, pd1))
        # make sure the result does not reference parts of the original, and the original is unmodified:
        self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)

        # some tags have ids, but not all - and the amount fits, but not the names:
        template1 = ["text", {"a": "b", "id": "baz"}, " text ", {"d": "e"}, " test"]
        template1_original = copy.deepcopy(template1)
        ids = frozenset({"baz"})
        unspecified_ids = True
        self.assertRaises(err.IdResolutionError, lambda: GRenderer.id_resolution(template1, ids, unspecified_ids, pd1))
        # make sure the result does not reference parts of the original, and the original is unmodified:
        self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)

        # some tags have ids, but not all - and the amount as well as the names fit:
        with warnings.catch_warnings(record=True) as w:
            template1 = ["text", {"a": "b", "id": "foo"}, " text ", {"d": "e"}, " test"]
            template1_original = copy.deepcopy(template1)
            ids = frozenset({"foo"})
            unspecified_ids = True
            template2, pd2 = GRenderer.id_resolution(template1, ids, unspecified_ids, pd1)
            # check result:
            self.assertEqual(template2, ["text", {"a": "b", "id": "foo"}, " text ", {"d": "e", "id": "bar"}, " test"])
            self.assertEqual(pd2, pd1)
            # make sure the result does not reference parts of the original, and the original is unmodified:
            self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)
            # make sure a warning was properly raised:
            self.assertTrue(len(w) == 1 and issubclass(w[-1].category, ws.IdMatchingNecessaryWarning))

    def test_resolve_addressing(self):
        pd1 = {"foo": {"gender-addressing": "t"}, "bar": {"gender-addressing": "f", "a": "b"}, "baz": {"wuwu": "wawa"},
               "bai": {"gender-addressing": "true"}, "bui": {"gender-addressing": "false"}}
        pd1_original = copy.deepcopy(pd1)

        # test for template without addressing:
        template1 = ["test ", {"context": "wuwu", "id": "foo"}, " text ", {"context": "wawa", "id": "bar"}, " test"]
        template1_original = copy.deepcopy(template1)
        template2, pd2 = GRenderer.resolve_addressing(template1, pd1)
        # check result:
        self.assertEqual(template2, template1)
        self.assertEqual(pd2, pd1)
        # make sure the result does not reference parts of the original, and the original is unmodified:
        self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)

        # test for template with one tag with addressing - gender-addressing=t:
        template1 = ["test ", {"context": "address", "id": "foo"}, " text"]
        template1_original = copy.deepcopy(template1)
        template2, pd2 = GRenderer.resolve_addressing(template1, pd1)
        # check result:
        self.assertEqual(template2, ["test ", {"context": "address", "id": "foo"}, " text"])
        self.assertEqual(pd2, pd1)
        # make sure the result does not reference parts of the original, and the original is unmodified:
        self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)

        # test for template with one tag with addressing - gender-addressing=f:
        template1 = ["test ", {"context": "address", "id": "bar"}, " text"]
        template1_original = copy.deepcopy(template1)
        template2, pd2 = GRenderer.resolve_addressing(template1, pd1)
        # check result:
        self.assertEqual(template2, ["test ", {"context": "personal-name", "id": "bar"}, " text"])
        self.assertEqual(pd2, pd1)
        # make sure the result does not reference parts of the original, and the original is unmodified:
        self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)

        # test for template with one tag with addressing - gender-addressing=true:
        template1 = ["test ", {"context": "address", "id": "bai"}, " text"]
        template1_original = copy.deepcopy(template1)
        template2, pd2 = GRenderer.resolve_addressing(template1, pd1)
        # check result:
        self.assertEqual(template2, ["test ", {"context": "address", "id": "bai"}, " text"])
        self.assertEqual(pd2, pd1)
        # make sure the result does not reference parts of the original, and the original is unmodified:
        self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)

        # test for template with one tag with addressing - gender-addressing=false:
        template1 = ["test ", {"context": "address", "id": "bui"}, " text"]
        template1_original = copy.deepcopy(template1)
        template2, pd2 = GRenderer.resolve_addressing(template1, pd1)
        # check result:
        self.assertEqual(template2, ["test ", {"context": "personal-name", "id": "bui"}, " text"])
        self.assertEqual(pd2, pd1)
        # make sure the result does not reference parts of the original, and the original is unmodified:
        self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)

        # test for template with one tag with gender-addressing - gender-addressing unspecified:
        with warnings.catch_warnings(record=True) as w:
            template1 = ["test ", {"context": "address", "id": "baz"}, " text"]
            template1_original = copy.deepcopy(template1)
            template2, pd2 = GRenderer.resolve_addressing(template1, pd1)
            # check result:
            self.assertEqual(template2, ["test ", {"context": "address", "id": "baz"}, " text"])
            self.assertEqual(pd2, pd1)
            # make sure the result does not reference parts of the original, and the original is unmodified:
            self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)
            # make sure the default value used warning was raised:
            self.assertTrue(len(w) == 1 and issubclass(w[-1].category, ws.DefaultValueUsedWarning))

        # template with multiple tags:
        with warnings.catch_warnings(record=True) as w:
            template1 = ["test ", {"context": "address", "id": "bai"},
                         " text ", {"context": "address", "id": "baz"},
                         " text ", {"context": "address", "id": "foo"},
                         " text ", {"context": "wawa", "id": "bar"},
                         " text ", {"context": "address", "id": "bar"}, " test"]
            template1_original = copy.deepcopy(template1)
            template2, pd2 = GRenderer.resolve_addressing(template1, pd1)
            # check result:
            self.assertEqual(template2, ["test ", {"context": "address", "id": "bai"},
                                         " text ", {"context": "address", "id": "baz"},
                                         " text ", {"context": "address", "id": "foo"},
                                         " text ", {"context": "wawa", "id": "bar"},
                                         " text ", {"context": "personal-name", "id": "bar"}, " test"])
            self.assertEqual(pd2, pd1)
            # make sure the result does not reference parts of the original, and the original is unmodified:
            self.check_run_aftermath(pd1, pd2, template1, template2, pd1_original, template1_original)
            # make sure the default value used warning was raised:
            self.assertTrue(len(w) == 1 and issubclass(w[-1].category, ws.DefaultValueUsedWarning))

    def test_render_final_context_values(self):
        # render tag with canonical properties:
        self.assertEqual(GRenderer.render_final_context_values(
            ["test ", {"id": "foo", "context": "subject"}, " text"],
            {"foo": {"subject": "they", "object": "them"}, "bar": {"object": "zen"}}),
            "test they text")

        # render tag with custom properties:
        self.assertEqual(GRenderer.render_final_context_values(
            ["test ", {"id": "foo", "context": "<wawawa>"}, " text"],
            {"foo": {"<wawawa>": "they", "object": "them"}, "bar": {"object": "zen"}}),
            "test they text")

        # render tag with noun to gender:
        self.assertEqual(GRenderer.render_final_context_values(
            ["test ", {"id": "foo", "context": gn.GenderedNoun("actor")}, " text"],
            {"foo": {"gender-nouns": "female", "object": "them"}, "bar": {"object": "zen"}}),
            "test actress text")

        # render tag with noun to gender, but no preferred gendering:
        with warnings.catch_warnings(record=True) as w:
            self.assertEqual(GRenderer.render_final_context_values(
                ["test ", {"id": "foo", "context": gn.GenderedNoun("actor")}, " text"],
                {"foo": {"object": "them"}, "bar": {"object": "zen"}}),
                "test actor text")
            self.assertTrue(len(w) == 1 and issubclass(w[-1].category, ws.DefaultValueUsedWarning))

        # render tag with a mixture of these:
        self.assertEqual(GRenderer.render_final_context_values(
            ["test ", {"id": "foo", "context": gn.GenderedNoun("actor")}, " text ",
             {"id": "bar", "context": "object"}, " test ", {"id": "bar", "context": "<wuwuwu>"}, " test"],
            {"foo": {"gender-nouns": "female", "object": "them"}, "bar": {"object": "zen", "<wuwuwu>": "wawa"}}),
            "test actress text zen test wawa test")

    def test_render_with_full_rendering_pipeline(self):
        # test to confirm that id matching is properly done:
        with warnings.catch_warnings(record=True) as w:
            self.assertEqual(GRenderer.render_with_full_rendering_pipeline(
                ["test ", {"id": "foo", "context": "subject"}, " text ", {"id": "foo", "context": "subject"}, " test ",
                 {"context": "object"}, " foo"],
                frozenset({"foo"}), True, {"foo": {"subject": "they"}, "bar": {"object": "them"}}),
                "test they text they test them foo")
            self.assertTrue(len(w) == 1 and issubclass(w[-1].category, ws.IdMatchingNecessaryWarning))

        # test to confirm that addressing is done correctly (one tag):
        with warnings.catch_warnings(record=True) as w:
            self.assertEqual(GRenderer.render_with_full_rendering_pipeline(
                ["test ", {"id": "foo", "context": "address"}, " text"],
                frozenset({"foo"}), False, {"foo": {"gender-addressing": "f", "personal-name": "Eberhard"}}),
                "test Eberhard text")
            self.assertTrue(len(w) == 0)

        # test to confirm that context values are rendered correctly (three tags; see test above):
        with warnings.catch_warnings(record=True) as w:
            self.assertEqual(GRenderer.render_with_full_rendering_pipeline(
                ["test ", {"id": "foo", "context": gn.GenderedNoun("actor")}, " text ",
                 {"id": "bar", "context": "object"}, " test ", {"id": "bar", "context": "<wuwuwu>"}, " test"],
                frozenset({"foo", "bar"}), False,
                {"foo": {"gender-nouns": "female", "object": "them"}, "bar": {"object": "zen", "<wuwuwu>": "wawa"}}),
                "test actress text zen test wawa test")
            self.assertTrue(len(w) == 0)

        # test to confirm that all three work correctly together (four tags):
        with warnings.catch_warnings(record=True) as w:
            self.assertEqual(GRenderer.render_with_full_rendering_pipeline(
                ["test ", {"id": "foo", "context": gn.GenderedNoun("actor")}, " text ", {"context": "address"}, " wawa ",
                 {"id": "bar", "context": "object"}, " test ", {"id": "bar", "context": "<wuwuwu>"}, " test"],
                frozenset({"foo", "bar"}), True,
                {"foo": {"gender-nouns": "female", "object": "them"}, "bar": {"object": "zen", "<wuwuwu>": "wawa"},
                 "baz": {"gender-addressing": "f", "personal-name": "Avery"}}),
                "test actress text Avery wawa zen test wawa test")
            self.assertTrue(len(w) == 1 and issubclass(w[-1].category, ws.IdMatchingNecessaryWarning))
