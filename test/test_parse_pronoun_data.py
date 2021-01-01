
import unittest
import warnings

import src.parse_pronoun_data as ppd
import src.errors as err
import src.warnings as ws


# pairs of valid json and its parsed version:

VALID_JSON_1 = """{"foo": "bar"}""", {"foo": "bar"}
VALID_JSON_2 = """{"foo": 1, "bar": ["a", "b"]}""", {"foo": 1, "bar": ["a", "b"]}
VALID_JSON_3 = """{}""", {}
VALID_JSON_4 = """{"foo": {"bar": "baz"}}""", {"foo": {"bar": "baz"}}

# invalid json data:

INVALID_JSON_1 = """{"foo":}"""
INVALID_JSON_2 = """{"foo"}"""
INVALID_JSON_3 = """{"foo": "bar" """
INVALID_JSON_4 = """kk"""
INVALID_JSON = [INVALID_JSON_1, INVALID_JSON_2, INVALID_JSON_3, INVALID_JSON_4]

# valid pronoun data:

IDPD_W_NO_PROPERTIES = """{}""", {}
IDPD_W_ONE_PROPERTY = """{"they": "xe"}""", {"they": "xe"}
IDPD_W_SEVERAL_PROPERTIES = """{"they": "xe", "them": "xen"}""", {"they": "xe", "them": "xen"}

GRPD_W_ONE_IDPD_1 = """{"foo": {}}""", {"foo": {}}
GRPD_W_ONE_IDPD_2 = """{"foo": {"they": "xe"}}""", {"foo": {"they": "xe"}}
GRPD_W_ONE_IDPD_3 = """{"foo": {"they": "xe", "them": "xen"}}""", {"foo": {"they": "xe", "them": "xen"}}

GRPD_W_MULTIPLE_ID = ("""{"foo": {"they": "xe", "them": "xen"}, "bar": {"they": "xe"}}""",
                      {"foo": {"they": "xe", "them": "xen"}, "bar": {"they": "xe"}})

VALID_IDPDS = [IDPD_W_NO_PROPERTIES, IDPD_W_ONE_PROPERTY, IDPD_W_SEVERAL_PROPERTIES]
VALID_GRPDS = [GRPD_W_ONE_IDPD_1, GRPD_W_ONE_IDPD_2, GRPD_W_ONE_IDPD_3, GRPD_W_MULTIPLE_ID]


class TestGRPDParser(unittest.TestCase):

    def test_pd_string_to_dict(self):
        # test for valid json data:
        self.assertEqual(ppd.GRPDParser.pd_string_to_dict(VALID_JSON_1[0]), VALID_JSON_1[1])
        self.assertEqual(ppd.GRPDParser.pd_string_to_dict(VALID_JSON_2[0]), VALID_JSON_2[1])
        self.assertEqual(ppd.GRPDParser.pd_string_to_dict(VALID_JSON_3[0]), VALID_JSON_3[1])
        self.assertEqual(ppd.GRPDParser.pd_string_to_dict(VALID_JSON_4[0]), VALID_JSON_4[1])

        # test for invalid json data:
        self.assertRaises(err.InvalidPDError, lambda: ppd.GRPDParser.pd_string_to_dict(INVALID_JSON_1))
        self.assertRaises(err.InvalidPDError, lambda: ppd.GRPDParser.pd_string_to_dict(INVALID_JSON_2))
        self.assertRaises(err.InvalidPDError, lambda: ppd.GRPDParser.pd_string_to_dict(INVALID_JSON_3))
        self.assertRaises(err.InvalidPDError, lambda: ppd.GRPDParser.pd_string_to_dict(INVALID_JSON_4))

        # get the right results for the valid pronoun data examples we prepared:
        for inp, out in VALID_IDPDS + VALID_GRPDS:
            self.assertEqual(ppd.GRPDParser.pd_string_to_dict(inp), out)

    def test_type_of_dict(self):
        # error if input is not a dict:
        self.assertRaises(err.InvalidPDError, lambda: ppd.GRPDParser.type_of_pd("{\"they\": \"xe\"}"))

        # error if values are of different types (since it can't be either idpd or grpd then):
        self.assertRaises(err.InvalidPDError, lambda: ppd.GRPDParser.type_of_pd({"a": "foo", "b": ["a"]}))
        self.assertRaises(err.InvalidPDError, lambda: ppd.GRPDParser.type_of_pd({"a": "foo", "b": 1}))
        self.assertRaises(err.InvalidPDError, lambda: ppd.GRPDParser.type_of_pd({"a": "foo", "b": {"c": "bar"}}))
        self.assertRaises(err.InvalidPDError, lambda: ppd.GRPDParser.type_of_pd({"a": {"c": "bar"}, "b": ["a"]}))
        self.assertRaises(err.InvalidPDError, lambda: ppd.GRPDParser.type_of_pd({"a": {"c": "bar"}, "b": 1}))
        # even if we have multiple values:
        self.assertRaises(err.InvalidPDError,
                          lambda: ppd.GRPDParser.type_of_pd({"a": "foo", "b": {"c": "bar"}, "c": "c"}))

        # error if values are something else than all string or all dict, in cases where all values are the same type:
        self.assertRaises(err.InvalidPDError, lambda: ppd.GRPDParser.type_of_pd({"a": ["b"], "b": ["c"]}))
        self.assertRaises(err.InvalidPDError, lambda: ppd.GRPDParser.type_of_pd({"a": 1, "b": 2, "c": 3}))
        # but accept if we have a valid all-values-are-strings or all-values-are-dicts:
        ppd.GRPDParser.type_of_pd({"foo": "bar", "foo2": "baz"})
        ppd.GRPDParser.type_of_pd({"foo": {"bar": "baz"}, "foo2": {"bar2": "baz"}})

        # raise error if an id is an empty string:
        self.assertRaises(err.InvalidPDError, lambda: ppd.GRPDParser.type_of_pd({"": {"wuwu": "wuiwui"}}))
        # but not if the key in idpd is a string:
        ppd.GRPDParser.type_of_pd({"": "wuwu"})
        ppd.GRPDParser.type_of_pd({"wuwu": {"": "wuiwui"}})

        # raise error if a value in a dict in a string-to-dict-mapping is invalid:
        self.assertRaises(err.InvalidPDError,
                          lambda: ppd.GRPDParser.type_of_pd({"foo": {"bar": "baz"}, "bar": {"baz": 1}}))
        self.assertRaises(err.InvalidPDError,
                          lambda: ppd.GRPDParser.type_of_pd({"foo": {"bar": "baz"}, "bar": {"baz": ["a"]}}))
        self.assertRaises(err.InvalidPDError,
                          lambda: ppd.GRPDParser.type_of_pd({"foo": {"bar": {"bar": "baz"}}, "bar": {"baz": "a"}}))

        # make sure that empty dicts are accepted, but the result is not relevant:
        self.assertIn(ppd.GRPDParser.type_of_pd({}), (ppd.IDPD, ppd.GRPD))

        # be okay with one as several key-value pairs in a string-to-dict-mapping,
        #  and return IDPD for such values:
        self.assertEqual(ppd.GRPDParser.type_of_pd({"foo": "bar"}), ppd.IDPD)
        self.assertEqual(ppd.GRPDParser.type_of_pd({"foo": "bar", "bar": "baz"}), ppd.IDPD)

        # be okay with zero, one as well as several key-value-pairs in a singular string-dict-mapping:
        self.assertEqual(ppd.GRPDParser.type_of_pd({"foo": {}}), ppd.GRPD)
        self.assertEqual(ppd.GRPDParser.type_of_pd({"foo": {"bar": "baz"}}), ppd.GRPD)
        self.assertEqual(ppd.GRPDParser.type_of_pd({"foo": {"bar": "baz", "baz": "bar"}}), ppd.GRPD)
        # be okay with combinations thereof:
        self.assertEqual(ppd.GRPDParser.type_of_pd(
            {"foo": {}, "foo2": {"bar": "baz"}, "foo3": {"baz": "bar", "bar": "baz"}}), ppd.GRPD)

        # accept the test values we prepared for valid pronoun data:

        for _, inp in VALID_IDPDS:
            if inp != {}:
                self.assertEqual(ppd.GRPDParser.type_of_pd(inp), ppd.IDPD)

        for _, inp in VALID_GRPDS:
            if inp != {}:
                self.assertEqual(ppd.GRPDParser.type_of_pd(inp), ppd.GRPD)

    def test_return_pd_if_it_is_valid(self):
        # testing is limited to our pre-defined test cases since this function internally calls test_type_of_dict and
        #  should therefore not be wrong in determining if something is valid or not:

        # test pre-defined valid pronoun data:
        for _, inp in VALID_IDPDS + VALID_GRPDS:
            out = ppd.GRPDParser.return_pd_if_it_is_valid(inp)
            self.assertEqual(id(inp), id(out))
            self.assertEqual(inp, out)

        # test the same for some other values to be sure that the exact value of strings doesn not matter and only
        #  the structure is looked at:
        ppd.GRPDParser.return_pd_if_it_is_valid(
            {"foo": {}, "foo2": {"bar": "baz"}, "foo3": {"baz": "bar", "bar": "baz"}})
        ppd.GRPDParser.return_pd_if_it_is_valid({"foo": "bar", "bar": "baz"})

        # make sure the errors raised by type_of_dict are raised by this function as well:
        self.assertRaises(err.InvalidPDError, lambda: ppd.GRPDParser.return_pd_if_it_is_valid({"a": "foo", "b": ["a"]}))
        self.assertRaises(err.InvalidPDError, lambda: ppd.GRPDParser.return_pd_if_it_is_valid({"bar": {"baz": 1}}))

    def test_pd_dict_to_grpd_dict(self):
        # test for idpd values:
        for _, inp in VALID_IDPDS:
            if inp != {}:  # <- special case, since it is undefined whether "{}" is an idpd or an grpd.
                self.assertEqual(ppd.GRPDParser.pd_dict_to_grpd_dict(inp), {"": inp})

        # test for grpd values:
        for _, inp in VALID_GRPDS:
            if inp != {}:  # <- special case, since it is undefined whether "{}" is an idpd or an grpd.
                self.assertEqual(ppd.GRPDParser.pd_dict_to_grpd_dict(inp), inp)

        # confirm that this also works if the words for randomly-looking dicts with "non-official" keywords:
        self.assertEqual(ppd.GRPDParser.pd_dict_to_grpd_dict({"foo": "bar"}), {"": {"foo": "bar"}})
        self.assertEqual(ppd.GRPDParser.pd_dict_to_grpd_dict({"baz": {"foo": "bar"}}), {"baz": {"foo": "bar"}})

        # two manual tests in case our testing with the predefined valid pronoun data examples happens to be wrong:
        self.assertEqual(ppd.GRPDParser.pd_dict_to_grpd_dict({"they": "xe", "them": "xen"}),
                         {"": {"they": "xe", "them": "xen"}})
        self.assertEqual(ppd.GRPDParser.pd_dict_to_grpd_dict({"foo": {"they": "xe", "them": "xen"}}),
                         {"foo": {"they": "xe", "them": "xen"}})

    def test_grpd_dict_to_canonical_grpd_dict(self):
        # test for one id, one non-con property:
        self.assertEqual(ppd.GRPDParser.grpd_dict_to_canonical_grpd_dict(
            {"foo": {"they": "xe"}}),
            {"foo": {"subject": "xe"}})
        # test for one id, one con property:
        self.assertEqual(ppd.GRPDParser.grpd_dict_to_canonical_grpd_dict(
            {"foo": {"subject": "xe"}}),
            {"foo": {"subject": "xe"}})
        # test for one id, two non-con properties:
        self.assertEqual(ppd.GRPDParser.grpd_dict_to_canonical_grpd_dict(
            {"foo": {"they": "xe", "them": "xen"}}),
            {"foo": {"subject": "xe", "object": "xen"}})
        # test for one id, one non-con and one con property:
        self.assertEqual(ppd.GRPDParser.grpd_dict_to_canonical_grpd_dict(
            {"foo": {"they": "xe", "address": "Mr"}}),
            {"foo": {"subject": "xe", "address": "Mr"}})
        # test for one id, two con properties:
        self.assertEqual(ppd.GRPDParser.grpd_dict_to_canonical_grpd_dict(
            {"foo": {"subject": "xe", "address": "Mr"}}),
            {"foo": {"subject": "xe", "address": "Mr"}})

        # combined: test for multiple ids with multiple properties:
        self.assertEqual(ppd.GRPDParser.grpd_dict_to_canonical_grpd_dict(
            {"foo": {"they": "xe", "address": "Mr"}, "bar": {"obj": "them"}}),
            {"foo": {"subject": "xe", "address": "Mr"}, "bar": {"object": "them"}})

        # special cases (further covered by the unittests for `handle_context_values.py`):

        # custom properties - in this case, canonical:
        self.assertEqual(ppd.GRPDParser.grpd_dict_to_canonical_grpd_dict(
            {"foo": {"<wuwu>": "wawa"}}),
            {"foo": {"<wuwu>": "wawa"}})
        self.assertEqual(ppd.GRPDParser.grpd_dict_to_canonical_grpd_dict(
            {"foo": {"_wuwu": "wawa"}}),
            {"foo": {"<wuwu>": "wawa"}})
        # and in this case, not canonical and raising a warning:
        with warnings.catch_warnings(record=True) as w:
            self.assertEqual(ppd.GRPDParser.grpd_dict_to_canonical_grpd_dict(
                {"foo": {"wuwu": "wawa"}}),
                {"foo": {"<wuwu>": "wawa"}})
            self.assertTrue(len(w) == 1 and issubclass(w[-1].category, ws.UnknownPropertyWarning))

        # error for invalid information
        self.assertRaises(err.InvalidInformationError,
                          lambda: ppd.GRPDParser.grpd_dict_to_canonical_grpd_dict({"foo": {"gender-nouns": "fufu"}}))
        self.assertRaises(err.InvalidInformationError,
                          lambda: ppd.GRPDParser.grpd_dict_to_canonical_grpd_dict({"foo": {"gender-addressing": "hi"}}))
        ppd.GRPDParser.grpd_dict_to_canonical_grpd_dict({"foo": {"gender-nouns": "neutral"}})
        ppd.GRPDParser.grpd_dict_to_canonical_grpd_dict({"foo": {"gender-addressing": "t"}})

        # error for doubled information
        self.assertRaises(err.DoubledInformationError,
                          lambda: ppd.GRPDParser.grpd_dict_to_canonical_grpd_dict({"foo": {"they": "a", "subj": "b"}}))

    def test_full_parsing_pipeline(self):
        # error when given pd is neither grpd nor idpd:
        self.assertRaises(err.InvalidPDError,
                          lambda: ppd.GRPDParser.full_parsing_pipeline({"foo": {"bar": {"baz": "wuwu"}}}))
        self.assertRaises(err.InvalidPDError,
                          lambda: ppd.GRPDParser.full_parsing_pipeline({"foo": {"bar": "baz", "baz": 1}}))
        self.assertRaises(err.InvalidPDError,
                          lambda: ppd.GRPDParser.full_parsing_pipeline({"": {"they": "xe"}}))

        # turn grpd as well as idpd into grpd in the end:
        self.assertEqual(ppd.GRPDParser.full_parsing_pipeline(
            {"foo": {"subject": "they"}}),
            {"foo": {"subject": "they"}})
        self.assertEqual(ppd.GRPDParser.full_parsing_pipeline(
            {"subject": "they"}),
            {"": {"subject": "they"}})

        # accepts grpd with multiple ids:
        self.assertEqual(ppd.GRPDParser.full_parsing_pipeline(
            {"foo": {"subject": "they"}, "bar": {"object": "them"}}),
            {"foo": {"subject": "they"}, "bar": {"object": "them"}})

        # tests done when converting properties to canonical properties - copied from tests for the dedicated function:

        self.assertEqual(ppd.GRPDParser.full_parsing_pipeline(
            {"foo": {"they": "xe"}}),
            {"foo": {"subject": "xe"}})
        # test for one id, one con property:
        self.assertEqual(ppd.GRPDParser.full_parsing_pipeline(
            {"foo": {"subject": "xe"}}),
            {"foo": {"subject": "xe"}})
        # test for one id, two non-con properties:
        self.assertEqual(ppd.GRPDParser.full_parsing_pipeline(
            {"foo": {"they": "xe", "them": "xen"}}),
            {"foo": {"subject": "xe", "object": "xen"}})
        # test for one id, one non-con and one con property:
        self.assertEqual(ppd.GRPDParser.full_parsing_pipeline(
            {"foo": {"they": "xe", "address": "Mr"}}),
            {"foo": {"subject": "xe", "address": "Mr"}})
        # test for one id, two con properties:
        self.assertEqual(ppd.GRPDParser.full_parsing_pipeline(
            {"foo": {"subject": "xe", "address": "Mr"}}),
            {"foo": {"subject": "xe", "address": "Mr"}})

        # combined: test for multiple ids with multiple properties:
        self.assertEqual(ppd.GRPDParser.full_parsing_pipeline(
            {"foo": {"they": "xe", "address": "Mr"}, "bar": {"obj": "them"}}),
            {"foo": {"subject": "xe", "address": "Mr"}, "bar": {"object": "them"}})

        # special cases (further covered by the unittests for `handle_context_values.py`):

        # custom properties - in this case, canonical:
        self.assertEqual(ppd.GRPDParser.full_parsing_pipeline(
            {"foo": {"<wuwu>": "wawa"}}),
            {"foo": {"<wuwu>": "wawa"}})
        self.assertEqual(ppd.GRPDParser.full_parsing_pipeline(
            {"foo": {"_wuwu": "wawa"}}),
            {"foo": {"<wuwu>": "wawa"}})
        # and in this case, not canonical and raising a warning:
        with warnings.catch_warnings(record=True) as w:
            self.assertEqual(ppd.GRPDParser.full_parsing_pipeline(
                {"foo": {"wuwu": "wawa"}}),
                {"foo": {"<wuwu>": "wawa"}})
            self.assertTrue(len(w) == 1 and issubclass(w[-1].category, ws.UnknownPropertyWarning))

        # error for invalid information
        self.assertRaises(err.InvalidInformationError,
                          lambda: ppd.GRPDParser.full_parsing_pipeline({"foo": {"gender-nouns": "fufu"}}))
        self.assertRaises(err.InvalidInformationError,
                          lambda: ppd.GRPDParser.full_parsing_pipeline({"foo": {"gender-addressing": "lolol"}}))
        ppd.GRPDParser.full_parsing_pipeline({"foo": {"gender-nouns": "neutral"}})
        ppd.GRPDParser.full_parsing_pipeline({"foo": {"gender-addressing": "t"}})

        # error for doubled information
        self.assertRaises(err.DoubledInformationError,
                          lambda: ppd.GRPDParser.full_parsing_pipeline({"foo": {"they": "a", "subj": "b"}}))
