
import unittest
import string
import copy
from typing import List, Tuple

from test import check_type
import src.parse_templates as pt
import src.errors as err
import src.gender_nouns as gn
import src.warnings as ws

# testing classes:


class TestChars(unittest.TestCase):

    def test_type(self):
        for c in string.printable:
            # test if whitespace is properly detected:
            if c in "\t\n \u200B":
                self.assertEqual(pt.Chars.type(c), pt.Chars.ws)

            # test if special characters are properly detected:
            elif c in "{}\\:*":
                self.assertEqual(pt.Chars.type(c), c)

            # test if other characters are properly detected:
            else:
                self.assertEqual(pt.Chars.type(c), pt.Chars.char)

        # test if all possible values are different:
        all_type_identifiers = list("{}\\:*") + [pt.Chars.ws, pt.Chars.char]
        all_type_identifiers_minus_doubled_ones = set(all_type_identifiers)
        self.assertEqual(set(all_type_identifiers), set(all_type_identifiers_minus_doubled_ones))

    def test_escape_gr_string(self):
        # test if escaping special chars in the middle, the beginning as well as at the end works:
        self.assertEqual(pt.Chars.escape_gr_string("{test_test"), "\\{test_test")
        self.assertEqual(pt.Chars.escape_gr_string("test_test{"), "test_test\\{")
        self.assertEqual(pt.Chars.escape_gr_string("test_{test"), "test_\\{test")

        # test if two characters separate as well as adjacent to each other are property escaped:
        self.assertEqual(pt.Chars.escape_gr_string("test_{test{"), "test_\\{test\\{")
        self.assertEqual(pt.Chars.escape_gr_string("test_{{test"), "test_\\{\\{test")

        # test if multiple different characters can be escaped in one string:
        self.assertEqual(pt.Chars.escape_gr_string("test_{test:"), "test_\\{test\\:")

        # test if all the right characters are counted as escape characters:
        for c in string.printable:
            if c in "{}\\:* \n\t\u200B":
                self.assertEqual(pt.Chars.escape_gr_string(c), "\\" + c)
            else:
                self.assertEqual(pt.Chars.escape_gr_string(c), c)

        # same test, but for strict=False:
        for c in string.printable:
            if c in "{}\\":
                self.assertEqual(pt.Chars.escape_gr_string(c, strict=False), "\\" + c)
            else:
                self.assertEqual(pt.Chars.escape_gr_string(c, strict=False), c)


class TestStates(unittest.TestCase):

    # a list of all types of states for further tests to use:
    state_identifiers = ["not_within_tags", "in_empty_section", "in_not_empty_section",
                         "in_section_with_one_finished_word", "in_empty_value_section",
                         "in_not_empty_value_section"]  # "escaped" is not a type, but an enhancer!

    def test_state_identifiers_on_difference(self):
        # test if all state identifiers are different:
        all_values = self.state_identifiers.copy()
        all_values.sort()

        all_values_once = list(set(all_values))
        all_values_once.sort()

        self.assertEqual(all_values, all_values_once)

    def test_escapement_methods(self):
        # test the escapement methods. Since these are encapsulated in this class,
        #  we don't test the specific data structures behind them, but rather that converting between escaped and
        #  unescaped states works as expected.
        for s in self.state_identifiers:
            state = pt.States.__dict__[s]

            # test if escaping and unescaping again equals not escaping at all:
            self.assertEqual(pt.States.unescape(pt.States.escape(state)), state)

            # test if is_escaped works correctly:
            self.assertFalse(pt.States.is_escaped(state))
            self.assertTrue(pt.States.is_escaped(pt.States.escape(state)))

            # test if switch_escapement works correctly:
            self.assertEqual(pt.States.switch_escapement(pt.States.escape(state)), state)
            self.assertEqual(pt.States.switch_escapement(state), pt.States.escape(state))


class TestStateTransitioner(unittest.TestCase):

    def test_transition_state(self):
        # test if the output of transition_state matches our type expectations;
        #  testing if it works out for all possible inputs would require replicating the transition tree, which would
        #  be unreasonable, and is already covered by the parsing tests further down below.
        for c in ("{", "a", " "):  # <- iterate over all character types
            char_type = pt.Chars.type(c)
            for s in TestStates.state_identifiers:  # <- iterate over all state types
                state = pt.States.__dict__[s]
                if char_type in pt.StateTransitioner.state_transitions[state]:
                    new_state, transition_fkt = pt.StateTransitioner.transition_state(state, c)
                    full_return = (new_state, transition_fkt)

                    # check if result really has the right type:
                    self.assertTrue(check_type.is_instance(new_state, str))
                    self.assertTrue(check_type.is_instance(transition_fkt, type(lambda: None)))

                    # check if value is really read from the state_transitions_dict correctly:
                    self.assertEqual(full_return, pt.StateTransitioner.state_transitions[state][char_type])
                else:
                    # make sure an error is raised if the state does not allow a special character:
                    self.assertRaises(err.SyntaxError, lambda: pt.StateTransitioner.transition_state(state, c))


class TestSectionTypes(unittest.TestCase):

    def test_format_of_section_type_list(self):
        # test the list for its data type:
        self.assertTrue(check_type.is_instance(pt.SectionTypes.section_types_w_priorities,
                                               List[Tuple[str, float, bool]]))

        # check if every priority value is in allowed range (between 0 and 1000):
        for _, priority, _2 in pt.SectionTypes.section_types_w_priorities:
            self.assertTrue(0 <= priority <= 1000)

    def test_section_type_accepts_multiple_values(self):
        for section_type, _, accepts_multiples in pt.SectionTypes.section_types_w_priorities:

            # test if it returns a bool for every section type:
            self.assertTrue(type(pt.SectionTypes.section_type_accepts_multiple_values(section_type)) is bool)

            # test if it returns True at the right times:
            self.assertEqual(pt.SectionTypes.section_type_accepts_multiple_values(section_type), accepts_multiples)

    def test_section_type_exists(self):
        # test if all section types exist:
        for section_type, _, _ in pt.SectionTypes.section_types_w_priorities:
            self.assertTrue(pt.SectionTypes.section_type_exists(section_type))

        # test if fictional section type does not exist:
        self.assertFalse(pt.SectionTypes.section_type_exists("test test test"))

    def test_create_section_types_for_untyped_tag(self):
        # allows valid finished typings:
        for typing in [
            ["id", "context"], ["context", "id"],  # <- fully specified
            ["context"],  # <- only the necessary sections
        ]:
            self.assertEqual(typing, pt.SectionTypes.create_section_types_for_untyped_tag(typing))

        # finish typings where types are omitted:
        self.assertEqual(pt.SectionTypes.create_section_types_for_untyped_tag(["", "context"]),
                         ["id", "context"])
        self.assertEqual(pt.SectionTypes.create_section_types_for_untyped_tag(["context", ""]),
                         ["context", "id"])
        self.assertEqual(pt.SectionTypes.create_section_types_for_untyped_tag(["id", ""]),
                         ["id", "context"])
        self.assertEqual(pt.SectionTypes.create_section_types_for_untyped_tag(["", "id"]),
                         ["context", "id"])
        self.assertEqual(pt.SectionTypes.create_section_types_for_untyped_tag(["", ""]),
                         ["id", "context"])

        # raise an error if typing is too long:
        self.assertRaises(err.SyntaxPostprocessingError,
                          lambda: pt.SectionTypes.create_section_types_for_untyped_tag(["", "", ""]))

        # raise an error if section type is used more than once:
        self.assertRaises(err.SyntaxPostprocessingError,
                          lambda: pt.SectionTypes.create_section_types_for_untyped_tag(["id", "id"]))

        # raise an error if a section type is unknown:
        self.assertRaises(err.SyntaxPostprocessingError,
                          lambda: pt.SectionTypes.create_section_types_for_untyped_tag(["wuwu"]))

        # raise an error if the output typing has no context-section:
        self.assertRaises(err.SyntaxPostprocessingError,
                          lambda: pt.SectionTypes.create_section_types_for_untyped_tag(["id"]))


class TestGRParser(unittest.TestCase):

    def test_parse_gr_template_from_str(self):
        # corner case: empty template:
        self.assertEqual(pt.GRParser.parse_gr_template_from_str(""),
                         [""])

        # template, but only text:
        self.assertEqual(pt.GRParser.parse_gr_template_from_str("text text text"),
                         ["text text text"])

        # template, but only text and escaped chars:
        self.assertEqual(pt.GRParser.parse_gr_template_from_str("text \\\\ text \\{ "),
                         ["text \\ text { "])

        # 1. template with 1 tag and 1 section 1 value and no type declaration:
        self.assertEqual(pt.GRParser.parse_gr_template_from_str("text {wuwu} test"),
                         ["text ", [("", ["wuwu"])], " test"])

        # 1a: corner case: template starts with the tag:
        self.assertEqual(pt.GRParser.parse_gr_template_from_str("{wuwu} test"),
                         ["", [("", ["wuwu"])], " test"])

        # 1b: corner case: template ends with the tag:
        self.assertEqual(pt.GRParser.parse_gr_template_from_str("text {wuwu}"),
                         ["text ", [("", ["wuwu"])], ""])

        # 1c. corner case: only one section with no type information, but ending with ws before the tag ends:
        self.assertEqual(pt.GRParser.parse_gr_template_from_str("text {wuwu \n}"),
                         ["text ", [("", ["wuwu"])], ""])

        # 2. template with 1 tag 1 section 3 values and no type declaration:
        self.assertEqual(pt.GRParser.parse_gr_template_from_str("text {wuwu wawa fufu} test"),
                         ["text ", [("", ["wuwu", "wawa", "fufu"])], " test"])

        # 3. template with 1 tag 1 section 1 value and a type declaration:
        self.assertEqual(pt.GRParser.parse_gr_template_from_str("text {tt:wuwu} test"),
                         ["text ", [("tt", ["wuwu"])], " test"])

        # 4. template with 1 tag 3 values and a type declaration:
        self.assertEqual(pt.GRParser.parse_gr_template_from_str("text {tt:wuwu wawa fufu} test"),
                         ["text ", [("tt", ["wuwu", "wawa", "fufu"])], " test"])

        # 1234: tag with multiple sections (1, 2, 3 and 4) combined:
        self.assertEqual(pt.GRParser.parse_gr_template_from_str(
            "text {wuwu*wuwu wawa fufu*tt:wuwu*tt:wuwu wawa fufu} test"),
            ["text ",
             [("", ["wuwu"]), ("", ["wuwu", "wawa", "fufu"]), ("tt", ["wuwu"]), ("tt", ["wuwu", "wawa", "fufu"])],
             " test"]
        )

        # 1234, but with added whitespace in places where it shouldn't matter:
        self.assertEqual(pt.GRParser.parse_gr_template_from_str(
            "text {  wuwu  * wuwu\n wawa \tfufu\t *tt:\twuwu *tt\n:wuwu\n\nwawa fufu\n} test"),
            ["text ",
             [("", ["wuwu"]), ("", ["wuwu", "wawa", "fufu"]), ("tt", ["wuwu"]), ("tt", ["wuwu", "wawa", "fufu"])],
             " test"]
        )

        # corner case: values in tags contains escaped special characters:
        self.assertEqual(pt.GRParser.parse_gr_template_from_str("{wuwu\\{\\\\mm:\\}}"),
                         ["", [("wuwu{\\mm", ["}"])], ""])

        # multiple tags:
        self.assertEqual(pt.GRParser.parse_gr_template_from_str(
            "text {wuwu*wuwu wawa fufu} hmmm{tt:wuwu*tt:wuwu wawa fufu} test"),
            ["text ", [("", ["wuwu"]), ("", ["wuwu", "wawa", "fufu"])], " hmmm",
             [("tt", ["wuwu"]), ("tt", ["wuwu", "wawa", "fufu"])], " test"]
        )

        # corner case: multiple tags adjacent to each other:
        self.assertEqual(pt.GRParser.parse_gr_template_from_str(
            "text {wuwu*wuwu wawa fufu}{tt:wuwu*tt:wuwu wawa fufu} test"),
            ["text ", [("", ["wuwu"]), ("", ["wuwu", "wawa", "fufu"])], "",
             [("tt", ["wuwu"]), ("tt", ["wuwu", "wawa", "fufu"])], " test"]
        )

        # allow ":" and "*" outside of tags:
        self.assertEqual(pt.GRParser.parse_gr_template_from_str(
            "text text: wuwu* "),
            ["text text: wuwu* "]
        )

        # test error: template isn't closed properly
        self.assertRaises(err.SyntaxError, lambda: pt.GRParser.parse_gr_template_from_str("wuwu {wawa"))

        # test error: template ends with an escape character without anything following it:
        self.assertRaises(err.SyntaxError, lambda: pt.GRParser.parse_gr_template_from_str("wuwu \\"))

        # test error: template has more than one type in a tag (SyntaxPostprocessingError):
        self.assertRaises(err.SyntaxError, lambda: pt.GRParser.parse_gr_template_from_str("{aa ff:wuwu}"))

        # test error: template has more than one column in a tag (SyntaxPostprocessingError):
        self.assertRaises(err.SyntaxError, lambda: pt.GRParser.parse_gr_template_from_str("{aa:bb:cc}"))

        # test error: template opens a tag within another tag (SyntaxPostprocessingError):
        self.assertRaises(err.SyntaxError, lambda: pt.GRParser.parse_gr_template_from_str("{ff:{wuwu}}"))

        # test error: tag closes without ever being opened:
        self.assertRaises(err.SyntaxError, lambda: pt.GRParser.parse_gr_template_from_str("wuwu}"))

    def test_assign_types_to_all_sections(self):
        # classic untyped single-section-tag:
        self.assertEqual(pt.GRParser.assign_types_to_all_sections(
            ["wuwu", [("", ["wuwu"])], "wawa"]),
            ["wuwu", [("context", ["wuwu"])], "wawa"])

        # "id", "":
        self.assertEqual(pt.GRParser.assign_types_to_all_sections(
            ["wuwu", [("id", ["wowo"]), ("", ["wuwu"])], "wawa"]),
            ["wuwu", [("id", ["wowo"]), ("context", ["wuwu"])], "wawa"])

        # "", "id":
        self.assertEqual(pt.GRParser.assign_types_to_all_sections(
            ["wuwu", [("", ["wuwu"]), ("id", ["wowo"])], "wawa"]),
            ["wuwu", [("context", ["wuwu"]), ("id", ["wowo"])], "wawa"])

        # "id", "context":
        self.assertEqual(pt.GRParser.assign_types_to_all_sections(
            ["wuwu", [("id", ["wowo"]), ("context", ["wuwu"])], "wawa"]),
            ["wuwu", [("id", ["wowo"]), ("context", ["wuwu"])], "wawa"])

        # "context", "id":
        self.assertEqual(pt.GRParser.assign_types_to_all_sections(
            ["wuwu", [("context", ["wuwu"]), ("id", ["wowo"])], "wawa"]),
            ["wuwu", [("context", ["wuwu"]), ("id", ["wowo"])], "wawa"])

        # quick check if the errors raised by create_section_types_for_untyped_tag get raised here, too:
        self.assertRaises(err.SyntaxPostprocessingError, lambda: pt.GRParser.assign_types_to_all_sections(
            ["wuwu", [("unknown_type!!!", ["wuwu"])], "wawa"]
        ))

        # test if output and input are different objects...
        inp = ["wuwu", [("id", ["val1"]), ("context", ["val2"])], "wawa"]
        out = pt.GRParser.assign_types_to_all_sections(inp)
        self.assertNotEqual(id(inp), id(out))
        self.assertNotEqual(id(inp[1]), id(out[1]))
        self.assertNotEqual(id(inp[1][0]), id(out[1][0]))
        self.assertNotEqual(id(inp[1][0][1]), id(out[1][0][1]))

        # ...even if they have the same value:
        self.assertEqual(inp, out)

    def test_split_tags_with_multiple_context_values(self):
        # test when only one context value is given - including multiple sections:
        self.assertEqual(pt.GRParser.split_tags_with_multiple_context_values(
            ["test", [("context", ["wuwu"]), ("tt", ["wawa"])], "test"]),
            ["test", [("tt", ["wawa"]), ("context", ["wuwu"])], "test"])

        # test when multiple context value are given - also including multiple sections:
        self.assertEqual(pt.GRParser.split_tags_with_multiple_context_values((
            ["test", [("tt1", "wowo"), ("context", ["wuwu", "wawa", "fufu"]), ("tt", ["wawa"])], "test"])),
            ["test", [("tt1", "wowo"), ("tt", ["wawa"]), ("context", ["wuwu"])], " ",
                     [("tt1", "wowo"), ("tt", ["wawa"]), ("context", ["wawa"])], " ",
                     [("tt1", "wowo"), ("tt", ["wawa"]), ("context", ["fufu"])], "test"])

        # corner case: test when the minimum amount of context values that counts as "multiple" is given:
        self.assertEqual(pt.GRParser.split_tags_with_multiple_context_values((
            ["test", [("tt1", "wowo"), ("context", ["wuwu", "wawa"]), ("tt", ["wawa"])], "test"])),
            ["test", [("tt1", "wowo"), ("tt", ["wawa"]), ("context", ["wuwu"])], " ",
                     [("tt1", "wowo"), ("tt", ["wawa"]), ("context", ["wawa"])], "test"])

        # don't test if tags without context values are affected, since these are not allowed at that stage of the
        # pipeline anymore:
        # self.assertEqual(pt.GRParser.split_tags_with_multiple_context_values(
        #     ["test", [("wawa", ["wuwu"]), ("wowo", ["wiwi"])], "test"]),
        #     ["test", [("wawa", ["wuwu"]), ("wowo", ["wiwi"])], "test"])

        # corner case: test for templates without tags:
        self.assertEqual(pt.GRParser.split_tags_with_multiple_context_values(
            ["test test wu wu"]),
            ["test test wu wu"])

        # define values for our next two tests:
        inp, out = (
            ["test", [("context", ["wuwu"]), ("tt", ["wawa", "wuwu"])],
             "test", [("tt1", "wowo"), ("context", ["wuwu", "wawa", "fufu"]), ("tt", ["wawa"])],
             "test", [("tt1", "wowo"), ("context", ["wuwu", "wawa"]), ("tt", ["wawa"])], "test"],

            ["test", [("tt", ["wawa", "wuwu"]), ("context", ["wuwu"])],
             "test", [("tt1", "wowo"), ("tt", ["wawa"]), ("context", ["wuwu"])], " ",
                     [("tt1", "wowo"), ("tt", ["wawa"]), ("context", ["wawa"])], " ",
                     [("tt1", "wowo"), ("tt", ["wawa"]), ("context", ["fufu"])],
             "test", [("tt1", "wowo"), ("tt", ["wawa"]), ("context", ["wuwu"])], " ",
                     [("tt1", "wowo"), ("tt", ["wawa"]), ("context", ["wawa"])], "test"])

        # test for templates with multiple tags:
        self.assertEqual(pt.GRParser.split_tags_with_multiple_context_values(inp), out)

        # make sure that input and output are in no way identical:
        self.assertNotEqual(id(inp), id(out))
        self.assertNotEqual(id(inp[3]), id(out[3]))
        self.assertNotEqual(id(inp[3][1][1]), id(out[3][1][1]))
        self.assertNotEqual(id(inp[3][1][1]), id(out[3][2][1]))
        self.assertNotEqual(id(inp[3][1][1]), id(out[5][1][1]))
        self.assertNotEqual(id(inp[3][1][1]), id(out[5][2][1]))
        self.assertNotEqual(id(inp[3][1][1]), id(out[7][1][1]))
        self.assertNotEqual(id(inp[1][1][1]), id(out[1][1][1]))

    def test_make_sure_that_sections_dont_exceed_allowed_amount_of_values(self):
        # error if section that allows only one value has multiple:
        self.assertRaises(err.SyntaxPostprocessingError,
                          lambda: pt.GRParser.make_sure_that_sections_dont_exceed_allowed_amount_of_values(
                              ["test", [("id", ["wuwu", "wuwu"])], "test"]))

        # error if a tag has proper as well as inproper:
        self.assertRaises(err.SyntaxPostprocessingError,
                          lambda: pt.GRParser.make_sure_that_sections_dont_exceed_allowed_amount_of_values(
                              ["test", [("id", ["wuwu", "wuwu"]), ("context", ["wowo"])], "test"]))

        for inp in (
                # one section legally w/ multiple values:
                ["test", [("context", ["wuwu", "wuwu"])], "test"],
                # one section legally w/ multiple values, as well as one section that allows and has only one value:
                ["test", [("context", ["wuwu", "wuwu"]), ("id", ["fufu"])], "test"]
        ):
            # no error is risen:
            out = pt.GRParser.make_sure_that_sections_dont_exceed_allowed_amount_of_values(inp)

            # out- and input are identical and equal:
            self.assertEqual(out, inp)
            self.assertEqual(id(out), id(inp))

    def test_convert_tags_to_indexable_dicts(self):
        # prepare by adding more values to test with:
        pt.SectionTypes.section_types_w_priorities += [
            ("wuwu", 0, False),
            ("wuiwui", 0, True),
            ("wowo", 0, True)
        ]

        # a. test for section with only one value that allows only one value:
        self.assertEqual(pt.GRParser.convert_tags_to_indexable_dicts(
            ["test", [("wuwu", ["wawa"])], "test"]),
            ["test", {"wuwu": "wawa"}, "test"])

        # b. test for sections with multiple values:
        self.assertEqual(pt.GRParser.convert_tags_to_indexable_dicts(
            ["test", [("wuiwui", ["wawa", "wuwu", "fufu"])], "test"]),
            ["test", {"wuiwui": ["wawa", "wuwu", "fufu"]}, "test"])

        # c. test for section that allows multiple values, but only has one:
        self.assertEqual(pt.GRParser.convert_tags_to_indexable_dicts(
            ["test", [("wowo", ["hihi"])], "test"]),
            ["test", {"wowo": ["hihi"]}, "test"])

        # a+b. test for tag with both types of section:
        self.assertEqual(pt.GRParser.convert_tags_to_indexable_dicts(
            ["test", [("wuwu", ["wawa"]), ("wuiwui", ["wawa", "wuwu", "fufu"]), ("wowo", ["hihi"])], "test"]),
            ["test", {"wuwu": "wawa", "wuiwui": ["wawa", "wuwu", "fufu"], "wowo": ["hihi"]}, "test"])

        # test for templates with multiple tags:
        self.assertEqual(pt.GRParser.convert_tags_to_indexable_dicts(
            ["test", [("wuwu", ["wawa"]), ("wuiwui", ["wawa", "wuwu", "fufu"]), ("wowo", ["hihi"])],
             "test", [("wuwu", ["wawa"])],
             "test", [("wowo", ["hihi"])],
             "test", [("wuiwui", ["wawa", "wuwu", "fufu"])], "test"]),

            ["test", {"wuwu": "wawa", "wuiwui": ["wawa", "wuwu", "fufu"], "wowo": ["hihi"]},
             "test", {"wuwu": "wawa"},
             "test", {"wowo": ["hihi"]},
             "test", {"wuiwui": ["wawa", "wuwu", "fufu"]}, "test"])

        # corner case: test for templates without tags:
        self.assertEqual(pt.GRParser.convert_tags_to_indexable_dicts(
            ["test test wu wu"]),
            ["test test wu wu"])

        # make sure that the new template is in no way id-identical to the old one:
        inp = ["test", [("wuiwui", ["wawa", "wuwu", "fufu"])], "test"]
        out = pt.GRParser.convert_tags_to_indexable_dicts(inp)
        self.assertNotEqual(id(out), id(inp))
        self.assertNotEqual(id(out[1]["wuiwui"]), id(inp[1][0][1]))

        # make sure the same goes for templates that contain no text and are therefore equal in in- and output:
        inp = ["test"]
        out = pt.GRParser.convert_tags_to_indexable_dicts(inp)
        self.assertNotEqual(id(out), id(inp))

        # remove the test values we just added:
        pt.SectionTypes.section_types_w_priorities = [val for val in pt.SectionTypes.section_types_w_priorities
                                                      if val[0] not in ("wuwu", "wuiwui", "wowo")]

    def test_convert_context_values_to_canonicals(self):
        # set test example values for context values and canonical context values:
        inp, out = ("Mr_s", "address")  # ToDo: Maybe iterate over several key-value pairs? Feel free to pull-request.
        inp2, out2 = ("they", "subject")

        # test for one context value:
        self.assertEqual(pt.GRParser.convert_context_values_to_canonicals(
            ["test", {"context": inp}, "test"]),
            ["test", {"context": out}, "test"])

        # define output and input for next two tests:
        inp_value, out_value = (
            ["test", {"context": inp, "wuwu": "wawa", "wowo": ["fufu"]}, "test"],
            ["test", {"context": out, "wuwu": "wawa", "wowo": ["fufu"]}, "test"])

        # test for one context value and some other sections:
        self.assertEqual(pt.GRParser.convert_context_values_to_canonicals(inp_value), out_value)

        # test if output and input values are actually id-different:
        self.assertNotEqual(id(inp_value), id(out_value))
        self.assertNotEqual(id(inp_value[1]), id(out_value[1]))
        self.assertNotEqual(id(inp_value[1]["wowo"]), id(out_value[1]["wowo"]))

        # test for template with multiple tags:
        self.assertEqual(pt.GRParser.convert_context_values_to_canonicals(
            ["test", {"context": inp, "wuwu": "wawa"}, "test", {"context": inp2, "wowo": ["fufu"]}, "test"]),
            ["test", {"context": out, "wuwu": "wawa"}, "test", {"context": out2, "wowo": ["fufu"]}, "test"])

    def test_full_parsing_pipeline(self):

        # -- first of all, test syntax-parsing-related stuff:

        # templates without tags:
        self.assertEqual(pt.GRParser.full_parsing_pipeline(""), [""])
        self.assertEqual(pt.GRParser.full_parsing_pipeline("wuwutt JJkk * ii :\n\n "), ["wuwutt JJkk * ii :\n\n "])

        # template with one tag (left-aligned, right-aligned, middle), two tags (separate, adjacent):
        self.assertEqual(pt.GRParser.full_parsing_pipeline("{they} text"), ["", {"context": "subject"}, " text"])
        self.assertEqual(pt.GRParser.full_parsing_pipeline("text {they}"), ["text ", {"context": "subject"}, ""])
        self.assertEqual(pt.GRParser.full_parsing_pipeline("t {they} t"), ["t ", {"context": "subject"}, " t"])
        # the aforementioned multiple-tags:
        self.assertEqual(pt.GRParser.full_parsing_pipeline("t {they} t2{them}"),
                         ["t ", {"context": "subject"}, " t2", {"context": "object"}, ""])
        self.assertEqual(pt.GRParser.full_parsing_pipeline("t {they}{them} t2"),
                         ["t ", {"context": "subject"}, "", {"context": "object"}, " t2"])

        # extra whitespace & ":"/"*" outside of tags & escaped characters:
        self.assertEqual(pt.GRParser.full_parsing_pipeline("t { they\n} t2{ them \t}"),
                         ["t ", {"context": "subject"}, " t2", {"context": "object"}, ""])
        self.assertEqual(pt.GRParser.full_parsing_pipeline("ww : \\{ oo ** "), ["ww : { oo ** "])

        # tag with multiple sections & an extra tag:
        self.assertEqual(pt.GRParser.full_parsing_pipeline("test {id:tom * context:they} tt {them}"),
                         ["test ", {"id": "tom", "context": "subject"}, " tt ", {"context": "object"}, ""])

        # errors when syntax errors occur:
        self.assertRaises(err.SyntaxError, lambda: pt.GRParser.full_parsing_pipeline("ww {context:"))
        self.assertRaises(err.SyntaxError, lambda: pt.GRParser.full_parsing_pipeline("ww \\"))
        self.assertRaises(err.SyntaxError, lambda: pt.GRParser.full_parsing_pipeline("{fuu fuu:wuwu}"))
        self.assertRaises(err.SyntaxError, lambda: pt.GRParser.full_parsing_pipeline("{aa:bb:cc}"))
        self.assertRaises(err.SyntaxError, lambda: pt.GRParser.full_parsing_pipeline("{fufu:{wuwu}}"))
        self.assertRaises(err.SyntaxError, lambda: pt.GRParser.full_parsing_pipeline("wuwu}"))

        # -- now we come to type assignments:

        # implicitly typed:
        self.assertEqual(pt.GRParser.full_parsing_pipeline("{they}"), ["", {"context": "subject"}, ""])
        self.assertEqual(pt.GRParser.full_parsing_pipeline("{foo*they}"), ["", {"id": "foo", "context": "subject"}, ""])
        # (partially) explicitly typed:
        self.assertEqual(pt.GRParser.full_parsing_pipeline("{context:they}"), ["", {"context": "subject"}, ""])
        self.assertEqual(pt.GRParser.full_parsing_pipeline("{foo*context:they}"),
                         ["", {"id": "foo", "context": "subject"}, ""])
        self.assertEqual(pt.GRParser.full_parsing_pipeline("{id:foo*they}"),
                         ["", {"id": "foo", "context": "subject"}, ""])
        self.assertEqual(pt.GRParser.full_parsing_pipeline("{id:foo * context:they}"),
                         ["", {"id": "foo", "context": "subject"}, ""])

        # errors in typing:
        self.assertRaises(err.SyntaxPostprocessingError, lambda: pt.GRParser.full_parsing_pipeline("{foo:bar}"))
        self.assertRaises(err.SyntaxPostprocessingError, lambda: pt.GRParser.full_parsing_pipeline("{id:foo}"))
        self.assertRaises(err.SyntaxPostprocessingError, lambda: pt.GRParser.full_parsing_pipeline(
            "{context:a*context:b}"))

        # -- split text into multiple context values:
        self.assertEqual(pt.GRParser.full_parsing_pipeline("{context:they them}"),
                         ["", {"context": "subject"}, " ", {"context": "object"}, ""])
        self.assertEqual(pt.GRParser.full_parsing_pipeline("{context: they them Mr_s}"),
                         ["", {"context": "subject"}, " ", {"context": "object"}, " ", {"context": "address"}, ""])
        self.assertEqual(pt.GRParser.full_parsing_pipeline("{foo*they them}"),
                         ["", {"context": "subject", "id": "foo"}, " ", {"context": "object", "id": "foo"}, ""])
        self.assertEqual(pt.GRParser.full_parsing_pipeline("{context:they them * foo}"),
                         ["", {"context": "subject", "id": "foo"}, " ", {"context": "object", "id": "foo"}, ""])

        # -- error if section exceeds allowed amount of values:
        self.assertRaises(err.SyntaxPostprocessingError, lambda: pt.GRParser.full_parsing_pipeline("{foo bar*they}"))

        # -- conversion of context values to canonicals:
        self.assertEqual(pt.GRParser.full_parsing_pipeline("{they}"), ["", {"context": "subject"}, ""])
        self.assertEqual(pt.GRParser.full_parsing_pipeline("{<foo>  }"), ["", {"context": "<foo>"}, ""])
        with self.assertWarns(ws.NounGenderingGuessingsWarning):  # <- confirm that parsing the noun raises a warning
            self.assertEqual(pt.GRParser.full_parsing_pipeline("{maid}"),
                             ["", {"context": gn.GenderedNoun("maid")}, ""])

    def test_get_all_specified_id_values(self):
        # test for template without tags:
        self.assertEqual(pt.GRParser.get_all_specified_id_values(["woohoo"]), frozenset())

        # a. test for template with tags, but no id values:
        self.assertEqual(pt.GRParser.get_all_specified_id_values(["", {"foo": "bar"}, ""]), frozenset())
        self.assertEqual(pt.GRParser.get_all_specified_id_values(["", {"f": "b"}, "", {"b": "f"}]), frozenset())

        # b. test for tag with id value specified:
        self.assertEqual(pt.GRParser.get_all_specified_id_values(
            ["", {"id": "wuwu"}, ""]), frozenset({"wuwu"}))
        self.assertEqual(pt.GRParser.get_all_specified_id_values(
            ["", {"id": "a"}, "", {"id": "b"}, ""]), frozenset({"a", "b"}))

        # b-ii. test for template with id value, plus other sections:
        self.assertEqual(pt.GRParser.get_all_specified_id_values(
            ["", {"id": "wuwu", "b": "c"}, ""]), frozenset({"wuwu"}))
        self.assertEqual(pt.GRParser.get_all_specified_id_values(
            ["", {"id": "a", "b": "c"}, "", {"id": "b", "f": "foo"}, ""]), frozenset({"a", "b"}))

        # define input for next two tests:
        inp = ["", {"id": "a"}, "", {"id": "b", "foo": "bar"}, "", {"bar": "c"}, ""]
        inp_original = copy.deepcopy(inp)

        # a+b. test for fusion of both:
        self.assertEqual(pt.GRParser.get_all_specified_id_values(inp), frozenset({"a", "b"}))

        # make sure that the template is not modified by the method:
        self.assertEqual(inp, inp_original)

    def test_pronoun_data_contains_unspecified_ids(self):
        # test for template without tags:
        self.assertFalse(pt.GRParser.template_contains_unspecified_ids(["wuwuwu"]))

        # test for template with ids in all tags:
        self.assertFalse(pt.GRParser.template_contains_unspecified_ids(["", {"id": "i"}, ""]))
        self.assertFalse(pt.GRParser.template_contains_unspecified_ids(["", {"id": "i"}, "", {"id": "j"}, ""]))
        # for tags with other sections than just the id section:
        self.assertFalse(pt.GRParser.template_contains_unspecified_ids(["", {"id": "i", "wuwu": "k"}, ""]))
        # both:
        self.assertFalse(pt.GRParser.template_contains_unspecified_ids(
            ["", {"id": "i", "wuwu": "k"}, "", {"id": "i"}, "", {"id": "j"}, ""]))

        # test for template without id in all tags:
        self.assertTrue(pt.GRParser.template_contains_unspecified_ids(["", {"foo": "i"}, ""]))
        self.assertTrue(pt.GRParser.template_contains_unspecified_ids(["", {"foo": "i"}, "", {"bar": "jojo"}, ""]))
        # for tags with multiple sections per tag:
        self.assertTrue(pt.GRParser.template_contains_unspecified_ids(["", {"foo": "i", "bar": "jojo"}, ""]))
        # both:
        self.assertTrue(pt.GRParser.template_contains_unspecified_ids(
            ["", {"foo": "i", "bar": "jojo"}, "", {"foo": "i"}, "", {"bar": "jojo"}, ""]))

        # make sure that the input isn't modified in either case:

        for inp in (["", {"id": "i", "wuwu": "k"}, "", {"id": "i"}, "", {"id": "j"}, ""],
                    ["", {"foo": "i", "bar": "jojo"}, "", {"foo": "i"}, "", {"bar": "jojo"}, ""]):

            inp_original = copy.deepcopy(inp)
            pt.GRParser.template_contains_unspecified_ids(inp)
            self.assertEqual(inp, inp_original)


class TestReGRParser(unittest.TestCase):

    def test_unparse_gr_tag(self):
        # a. test for tag with one section with one value:
        self.assertEqual(pt.ReGRParser.unparse_gr_tag([("foo", ["bar"])]), "{foo:bar}")
        # without specified section type:
        self.assertEqual(pt.ReGRParser.unparse_gr_tag([("", ["bar"])]), "{bar}")

        # b. test for a tag with one section with multiple values:
        self.assertEqual(pt.ReGRParser.unparse_gr_tag([("foo", ["bar", "baz"])]), "{foo:bar baz}")
        # without specified section type:
        self.assertEqual(pt.ReGRParser.unparse_gr_tag([("", ["bar", "baz"])]), "{bar baz}")

        # a+b. test for a tag with multiple sections:
        self.assertEqual(pt.ReGRParser.unparse_gr_tag(
            [("foo", ["bar"]), ("", ["bar"]), ("goo", ["bar", "baz"]), ("", ["bar", "baz"])]),
            "{foo:bar*bar*goo:bar baz*bar baz}")

        # test escapement of special characters:
        self.assertEqual(pt.ReGRParser.unparse_gr_tag(
            [(":f*oo{\\", ["bar*", "bar:", "{baz}*"])]),
            "{\\:f\\*oo\\{\\\\:bar\\* bar\\: \\{baz\\}\\*}")

    def test_unparse_gr_template(self):
        # (the un-parsing of individual tags is not that much tested is this test, since it's already in the former one)

        # test for template without any tags:
        self.assertEqual(pt.ReGRParser.unparse_gr_template([""]), "")
        self.assertEqual(pt.ReGRParser.unparse_gr_template(["wuiowoi"]), "wuiowoi")

        # test for template with one tag:
        self.assertEqual(pt.ReGRParser.unparse_gr_template(
            ["wuwu ", [("foo", ["bar", "baz"])], " wowo"]),
            "wuwu {foo:bar baz} wowo")
        self.assertEqual(pt.ReGRParser.unparse_gr_template(
            ["wuwu ", [("foo", ["bar"]), ("", ["bar"]), ("goo", ["bar", "baz"]), ("", ["bar", "baz"])], " wowo"]),
            "wuwu {foo:bar*bar*goo:bar baz*bar baz} wowo")

        # test for templates with multiple tags:
        self.assertEqual(pt.ReGRParser.unparse_gr_template(
            ["wuwu ", [("foo", ["bar", "baz"])], " wowo ",
             [("foo", ["bar"]), ("", ["bar"]), ("goo", ["bar", "baz"]), ("", ["bar", "baz"])], " wowo"]),
            "wuwu {foo:bar baz} wowo {foo:bar*bar*goo:bar baz*bar baz} wowo")

        # test if special characters "\", "{", "}" in text are properly escaped, but whitespace, "*" and ":" are not:
        self.assertEqual(pt.ReGRParser.unparse_gr_template(["wuwu oo*l:ll{uu}o\\ "]), "wuwu oo*l:ll\\{uu\\}o\\\\ ")
