"""
Parser functions for gender*render templates.
"""

import copy
from typing import Tuple, Callable, List, Dict, Union, FrozenSet

from . import errors
from . import handle_context_values
from . import gender_nouns
from . import warnings

# Some helpful type hints:


ParsedTemplate = List[Union[str, List[Tuple[str, List[str]]]]]
"""A type hint describing a parsed template as it is returned by most of the methods of GRParser.
Note that not any structure build according to this constructor is valid, since some aspects cannot be described
by Python type hints."""

ParsedTemplateRefined = List[Union[str, Dict[str, Union[str, List[str], gender_nouns.GenderedNoun]]]]
"""A type similar to GRParser.ParsedTemplate that makes the sections of tags easier accessible by making them
dicts instead of lists of tuples."""

# definitions of words and word groups accepted by the finite state machine:


class Chars:
    """Helper to categorize characters."""
    escape_char = "\\"
    whitespace_chars = "\t\n \u200B"
    special_chars = ":*{}\\"
    ws = "whitespace"
    char = "non-special chars"

    @staticmethod
    def type(c: str) -> str:
        """Returns the type of character c, which determines how states in the finite state machine that describes
        gender*render syntax transition to each other.
        This is either Chars.ws (whitespace), a special character or Chars.char (anything else)."""
        if c in Chars.special_chars:
            return c
        elif c in Chars.whitespace_chars:
            return Chars.ws
        else:
            return Chars.char

    @staticmethod
    def escape_gr_string(s: str, strict: bool = True) -> str:
        """Escapes all special gender*render characters in a string, such as {, }, \\, : and *, as well as whitespace,
        with backslashs.
        if `strict` is set to False, only {, } and \\ are escaped; this may be used for strings that are supposed to go
        into gender*render templates, yet not into the inners of the tags themselves."""
        i = len(s) - 1
        while i > -1:
            if s[i] in ((Chars.special_chars + Chars.whitespace_chars) if strict else {"\\", "{", "}"}):
                s = s[:i] + "\\" + s[i:]
            i -= 1
        return s

# definitions of states of the finite state machine:


class States:
    """Combines values for all sections the finite state machine that describes the syntax can be in, as well as
    methods to handle the special escaped/unescaped versions of all states."""

    # Currently, the read character is...
    not_within_tags = "...not part of any tag"

    in_empty_section = "...in a yet empty section"
    in_not_empty_section = "...in a not anymore empty section"
    in_section_with_one_finished_word = "...in a section which already contains a finished word"

    in_empty_value_section = "...in a yet empty value section"
    in_not_empty_value_section = "...in a not empty value section"

    escaped = "...and escaped"

    @staticmethod
    def escape(state: str) -> str:
        """Converts an unescaped state to its escaped equivalent."""
        assert not States.is_escaped(state)
        return state + States.escaped

    @staticmethod
    def unescape(state: str) -> str:
        """Convert an escaped state to its unescaped equivalent."""
        assert States.is_escaped(state)
        return state[:len(state)-len(States.escaped)]

    @staticmethod
    def is_escaped(state: str) -> bool:
        """Checks is the current char is an escaped char."""
        return state.endswith(States.escaped)

    @staticmethod
    def switch_escapement(state: str) -> str:
        """Returns the escaped or unescaped state of the given state, depending on whether it is currently escaped or
        not."""
        return States.escape(state) if not States.is_escaped(state) else States.unescape(state)

# the finite state machine, but without the escaped versions of all states since these are handled separately:


class StateTransitioner:
    """Translates between states using a finite state machine.
    This does not take into account the ability to escape characters."""

    state_transitions: Dict[str, Dict[str, Tuple[str, Callable[[ParsedTemplate, str], ParsedTemplate]]]] = {
        States.not_within_tags: {
            "{": (States.in_empty_section,
                lambda r, c: r+[[("", [])]]),
            Chars.char: (States.not_within_tags,
                lambda r, c: r[:-1]+[r[-1]+c]),
            Chars.ws: (States.not_within_tags,
                lambda r, c: r[:-1]+[r[-1]+c]),
            ":": (States.not_within_tags,
                lambda r, c: r[:-1]+[r[-1]+c]),
            "*": (States.not_within_tags,
                lambda r, c: r[:-1]+[r[-1]+c])
        },
        States.in_empty_section: {
            Chars.ws: (States.in_empty_section,
                lambda r, c: r),
            Chars.char: (States.in_not_empty_section,
                lambda r, c: r[:-1]+[r[-1][:-1]+[(r[-1][-1][0]+c, r[-1][-1][1])]])
        },
        States.in_not_empty_section: {
            ":": (States.in_empty_value_section,
                lambda r, c: r),
            "*": (States.in_empty_section,
                lambda r, c: r[:-1]+[r[-1][:-1]+[("", [r[-1][-1][0]]), ("", [])]]),
            "}": (States.not_within_tags,
                lambda r, c: r[:-1]+[r[-1][:-1]+[("", [r[-1][-1][0]])], ""]),
            Chars.ws: (States.in_section_with_one_finished_word,
                lambda r, c: r),
            Chars.char: (States.in_not_empty_section,
                lambda r, c: r[:-1]+[r[-1][:-1]+[(r[-1][-1][0]+c, r[-1][-1][1])]])
        },
        States.in_section_with_one_finished_word: {
            ":": (States.in_empty_value_section,
                lambda r, c: r),
            "*": (States.in_empty_section,
                lambda r, c: r[:-1]+[r[-1][:-1]+[("", [r[-1][-1][0]]), ("", [])]]),
            "}": (States.not_within_tags,
                lambda r, c: r[:-1]+[r[-1][:-1]+[("", [r[-1][-1][0]])], ""]),
            Chars.ws: (States.in_section_with_one_finished_word,
                lambda r, c: r),
            Chars.char: (States.in_not_empty_value_section,
                lambda r, c: r[:-1]+[r[-1][:-1]+[("", [r[-1][-1][0], c])]])
        },
        States.in_empty_value_section: {
            Chars.ws: (States.in_empty_value_section,
                lambda r, c: r),
            Chars.char: (States.in_not_empty_value_section,
                lambda r, c: r[:-1]+[r[-1][:-1]+[(r[-1][-1][0], r[-1][-1][1][:-1]+[
                    ((r[-1][-1][1][-1]+c) if len(r[-1][-1][1]) > 0 else c)
                ])]])
        },
        States.in_not_empty_value_section: {
            "*": (States.in_empty_section,
                lambda r, c: r[:-1]+[r[-1][:-1]+[(r[-1][-1][0], (r[-1][-1][1]
                       if r[-1][-1][1][-1] != "" else r[-1][-1][1][:-1])), ("", [])]]),
            "}": (States.not_within_tags,
                lambda r, c: r[:-1]+[r[-1][:-1]+[(r[-1][-1][0], r[-1][-1][1]
                       if r[-1][-1][1][-1] != "" else r[-1][-1][1][:-1])]]+[""]),
            Chars.ws: (States.in_not_empty_value_section,
                lambda r, c: r[:-1] + [r[-1][:-1] + [(r[-1][-1][0], r[-1][-1][1]
                       + ([""] if r[-1][-1][1][-1] != "" else []))]]),
            Chars.char: (States.in_not_empty_value_section,
                lambda r, c: r[:-1]+[r[-1][:-1]+[(r[-1][-1][0], r[-1][-1][1][:-1]+[(r[-1][-1][1][-1]+c)])]])
        }
    }

    @staticmethod
    def transition_state(state: str, char: str) -> Tuple[str, Callable[[ParsedTemplate, str], ParsedTemplate]]:
        """For a given state s and a given character c, returns the next state s2 and a function that takes a
        list representation of the already-parsed data and c and returns a modified, extended duplicate of the data
        based on c."""
        type_of_char = Chars.type(char)
        if type_of_char in StateTransitioner.state_transitions[state]:
            return StateTransitioner.state_transitions[state][type_of_char]
        else:
            raise errors.SyntaxError("Parsing error: \"" + type_of_char + "\" may not occur if it is " + state[3:])

# define different section types:


class SectionTypes:
    """Capsules a mapping of priorities to section types and methods to assign section types to un-typed sections."""

    section_types_w_priorities = [
        ("context", 1000., True),
        ("id", 950., False)
    ]
    """All supported section types as a list of tuples in the form of (name, priority, can_have_multiple_values)"""

    @staticmethod
    def section_type_accepts_multiple_values(section_type: str) -> bool:
        """Checks whether a section type can have multiple whitespace-separated values."""
        return SectionTypes.section_type_exists(section_type) and bool(
            [i for i in range(len(SectionTypes.section_types_w_priorities))
             if SectionTypes.section_types_w_priorities[i][0] == section_type
             and SectionTypes.section_types_w_priorities[i][2] is True]
        )

    @staticmethod
    def section_type_exists(section_type: str) -> bool:
        """Checks if a section type exists."""
        return bool(
            [i for i in range(len(SectionTypes.section_types_w_priorities))
             if SectionTypes.section_types_w_priorities[i][0] == section_type]
        )

    @staticmethod
    def create_section_types_for_untyped_tag(section_types: List[str]) -> List[str]:
        """Receives a list of section types in a tag (in chronological order) and assigns section types to those
        section without a section type, in accordance with the priorities of section types and the specification.
        Returns the typed section type list.
        Raises errors if section matching can not be done, or if no context section could be found."""
        result = list()

        # get all explicitly specified section types into a set:
        already_used = set()
        if len(section_types) > len(SectionTypes.section_types_w_priorities):
            raise errors.SyntaxPostprocessingError("Tag contains more sections than there are section types.")
        for section_type in filter(lambda x: x != "", section_types):
            if section_type in already_used:
                raise errors.SyntaxPostprocessingError("Section type \"" + section_type + "\" used twice in a tag.")
            elif not SectionTypes.section_type_exists(section_type):
                raise errors.SyntaxPostprocessingError("Section type \"" + section_type + "\" does not exist.")
            else:
                already_used.add(section_type)

        # create a section priority queue without these element:
        available_sections_types = [s for s in SectionTypes.section_types_w_priorities if s[0] not in already_used]
        available_sections_types.sort(key=lambda s: s[1])

        # iterate over all declared section types from the left to the right:
        for section_type in reversed(section_types):
            if section_type == "":
                result.insert(0, available_sections_types.pop()[0])
            else:
                result.insert(0, section_type)

        # raise an error if there is no context value:
        if "context" not in result:
            raise errors.SyntaxPostprocessingError("Tag misses a \"context\"-section.")

        return result


# translate the content of gender*render templates into basic parsed lists:


class GRParser:
    """Unites several static methods of a pipeline for parsing gender*render templates from strings into a list format
    and refining this representation to the maximum extend possible without additionally seeing the corresponding
    gender*render pronoun data.

    These functions are written to be executed in the order they are called by `full_parsing_pipeline`, and may or may
    not behave as expected when called on a value that didn't go through the other functions first."""

    @staticmethod
    def parse_gr_template_from_str(template: str) -> ParsedTemplate:
        """Takes a gender*render template as a string and returns it as an easily readable list representation.
        This does only do syntactic parsing in accordance to the defining finite state machine;
        further steps in the parsing pipeline are implemented by other methods of this parser.

        The resulting output is of the following structure:
        * value of a section: represented by lists of strings
        * type of section: represented by a string
        * section: tuple of type representation and value representation
        * tag: list of section representation
        * template: list, where every uneven element represents a tag and every even element is a string

        Special characters are all unescaped in the parsed version of the template."""

        result = [""]
        s = States.not_within_tags
        line_no = 1
        char_no = 1
        # iterate over all characters:
        for i in range(len(template)):
            c = template[i]
            # increment char count for SyntaxError raising:
            if c == "\n":
                line_no += 1
                char_no = 1
            else:
                char_no += 1

            # log:
            warnings.WarningManager.raise_warning(
                "result: " + str(result) + "\n\n"
                + "c: \"" + c + "\"\n"
                + "s: " + s + "\n"
                + "char type: " + Chars.type(c),
                warnings.GRSyntaxParsingLogging)

            # do the work of the finite state machine:
            type_of_char = Chars.type(c)
            if States.is_escaped(s):
                s = States.unescape(s)
                s, processing_function = StateTransitioner.state_transitions[s][Chars.char]
                result = processing_function(result, c)
            else:
                if type_of_char == Chars.escape_char:
                    s = States.escape(s)
                else:
                    try:
                        s, processing_function = StateTransitioner.transition_state(s, c)
                        result = processing_function(result, c)
                    except errors.SyntaxError:
                        raise errors.SyntaxError(
                            "The given gender*render template has invalid syntax.",
                            ("unknown file", line_no, char_no, template.split("\n")[line_no - 1])
                        )

        # raise an error if the template ends unproperly:
        if States.is_escaped(s):
            raise errors.SyntaxError("The template ends with an unescaped escape character, please escape it.",
                                     ("unknown file", line_no, char_no, template.split("\n")[-1]))
        elif s != States.not_within_tags:
            raise errors.SyntaxError("A tag opens, but is not finished properly.",
                                     ("unknown file", line_no, char_no, template.split("\n")[-1]))

        return result

    @staticmethod
    def assign_types_to_all_sections(parsed_template: ParsedTemplate) -> ParsedTemplate:
        """Takes a parsed template (as it is created by all methods of GRParser) and assigns every section of undefined
        type a section type."""
        result = copy.deepcopy(parsed_template)
        for i in range(1, len(result), 2):
            old_section_types: List[str] = [section[0] for section in result[i]]
            new_section_types: List[str] = SectionTypes.create_section_types_for_untyped_tag(old_section_types)
            result[i] = [(new_section_types[s], result[i][s][1]) for s in range(len(new_section_types))]
        return result

    @staticmethod
    def split_tags_with_multiple_context_values(parsed_template: ParsedTemplate) -> ParsedTemplate:
        """Takes a parsed template (as it is created by all methods of GRParser) and splits every tag into a sequence of
        tags, one for every context value of the tag.
        This assumes that every section was already assigned a type by GRParser.assign_types_to_all_sections, and may
        lead to wrong results otherwise.
        The context section is left the end of the tag by this procedure."""
        result = copy.deepcopy(parsed_template)
        for i in reversed(range(1, len(result), 2)):
            tag_without_context_section = [section for section in result[i] if section[0] != "context"]
            tag_but_only_context_section = [section for section in result[i] if section[0] == "context"]

            # split tag into one tag for every context value:
            context_values = tag_but_only_context_section.pop()[1]
            sequence_of_tags = [
                (copy.deepcopy(tag_without_context_section) + [("context", [context_value])])
                for context_value in context_values
            ]
            for j in reversed(range(1, len(sequence_of_tags))):
                sequence_of_tags.insert(j, " ")
            result[i:i+1] = sequence_of_tags

        return result

    @staticmethod
    def make_sure_that_sections_dont_exceed_allowed_amount_of_values(parsed_template: ParsedTemplate) -> ParsedTemplate:
        """Takes a parsed template (as it is created by all methods of GRParser) and raises an error if any tag that
        does not allow multiple values has multiple values. This should always be used before calling
        convert_tags_to_indxable_dicts.
        Returns the given dict afterwards."""
        for i in range(len(parsed_template)):
            if i % 2:  # is a tag
                for section_type, section_values in parsed_template[i]:
                    if SectionTypes.section_type_accepts_multiple_values(section_type):
                        continue
                    elif len(section_values) > 1:
                        raise errors.SyntaxPostprocessingError("Tag no. " + str((i + 1) / 2) + " (\""
                                                               + ReGRParser.unparse_gr_tag(parsed_template[i])
                                                               + "\") has multiple values in \""
                                                               + section_type +
                                                               "\"-section even though this type of section does"
                                                               + " not support this.")
        return parsed_template

    @staticmethod
    def convert_tags_to_indexable_dicts(parsed_template: ParsedTemplate) -> ParsedTemplateRefined:
        """Takes a parsed template (as it is created by all methods of GRParser) and converts every tag from a
        representation a la "[(a, b), (c, d)]" to a representation a la "{a: b, c: d}".
        This makes the value of specific types of sections easier to access by other methods.
        Note that the result returned by this method is different in that it is not accepted by the other methods of
        GRParser, and that this method should thus be the last method in this pipeline to be used.
        Raises an error if a section has multiple values yet accepts only one."""
        result = copy.deepcopy(parsed_template)
        for i in range(len(result)):
            if i % 2:  # is a tag
                new_tag = dict()
                for section_type, section_values in result[i]:
                    if not SectionTypes.section_type_accepts_multiple_values(section_type) or section_type == "context":
                        new_tag[section_type] = section_values[0]
                    else:
                        new_tag[section_type] = section_values
                result[i] = new_tag

        return result

    @staticmethod
    def convert_context_values_to_canonicals(parsed_template: ParsedTemplateRefined) -> ParsedTemplateRefined:
        """Converts a parsed template as returned by GRParser.convert_tags_to_indexable_dicts to a parsed template
        where every context value is canonical."""
        result = copy.deepcopy(parsed_template)
        for i in range(1, len(parsed_template), 2):
            result[i]["context"] = handle_context_values.ContextValues.get_canonical(result[i]["context"])
        return result

    @staticmethod
    def full_parsing_pipeline(template: str) -> ParsedTemplateRefined:
        """Walks template through the full parsing pipeline defined by GRParser, and returns the result."""
        template = GRParser.parse_gr_template_from_str(template)
        template = GRParser.assign_types_to_all_sections(template)
        template = GRParser.split_tags_with_multiple_context_values(template)
        template = GRParser.make_sure_that_sections_dont_exceed_allowed_amount_of_values(template)
        template = GRParser.convert_tags_to_indexable_dicts(template)
        template = GRParser.convert_context_values_to_canonicals(template)
        return template

    @staticmethod
    def get_all_specified_id_values(parsed_template: ParsedTemplateRefined) -> FrozenSet[str]:
        """Returns a frozen set of all id values explicitly specified by tags in the parsed template."""
        return frozenset(
            parsed_template[i]["id"] for i in range(1, len(parsed_template), 2) if "id" in parsed_template[i]
        )

    @staticmethod
    def template_contains_unspecified_ids(parsed_template: ParsedTemplateRefined) -> bool:
        """Returns whether the parsed template contains tags with unspecified id value."""
        return bool(list(
            parsed_template[i] for i in range(1, len(parsed_template), 2) if "id" not in parsed_template[i]
        ))

# functions to reverse parsed templates for testing and simplification purposes:


class ReGRParser:
    """Bundles methods to get a valid gender*render template from ParsedTemplate."""

    @staticmethod
    def unparse_gr_tag(tag_representation: List[Tuple[str, List[str]]]) -> str:
        return "{" + "*".join([(
                            ((Chars.escape_gr_string(section[0]) + ":") if section[0] else "")
                            + " ".join([Chars.escape_gr_string(value) for value in section[1]])
                        ) for section in tag_representation]) + "}"

    @staticmethod
    def unparse_gr_template(parsed_template: ParsedTemplate) -> str:
        """Takes the result of any method of the GRParser class and returns a template (as a string) that corresponds to
        the given parsed template.
        This may be used for testing purposes or to simplify gender*render templates."""
        result = str()
        for i in range(len(parsed_template)):
            if i % 2:  # is a tag
                result += ReGRParser.unparse_gr_tag(parsed_template[i])
            else:  # is a string
                result += Chars.escape_gr_string(parsed_template[i], strict=False)
        return result

    # ToDo: This set of methods is currently abandoned; if you want to implement some functions to also convert
    #  ParsedTemplateRefined to strings, feel free to make a pull request/ issue and maybe we can add an interface for
    #  it!
