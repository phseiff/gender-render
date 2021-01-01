"""
Functions to gender nouns with gender bias correctly.

Please note that you need to have `nltk` installed for this to work completely, e.g. to include all types of warnings.
"""

import requests
import json
import copy
import warnings as builtin_warnings
import os
from typing import Set, Optional, Dict, List, Callable, Tuple, Union
try:
    from typing_extensions import TypedDict, Literal
except ImportError:
    TypedDict = dict
    Literal = None

from . import warnings

# make some type definitions for the data we read from the web:


if Literal:
    OriginalDataGender = Literal["f", "m", "n", "o"]
else:
    OriginalDataGender = str


class OriginalDataGenderedVersionInfo(TypedDict):
    parts_of_speech: Optional[str]
    word: str


class OriginalDataGenderMapping(TypedDict):
    f: Optional[List[OriginalDataGenderedVersionInfo]]
    m: Optional[List[OriginalDataGenderedVersionInfo]]
    n: Optional[List[OriginalDataGenderedVersionInfo]]
    h: Optional[List[OriginalDataGenderedVersionInfo]]


class OriginalDataWord(TypedDict):
    word: str
    wordnet_senseno: Optional[str]
    gender: OriginalDataGender
    gender_map: Optional[OriginalDataGenderMapping]


OriginalGenderNounData = List[OriginalDataWord]

# make some type definitions for the data we create:


if Literal:
    GeneratedDataGender = Literal["female", "male", "neutral"]
else:
    GeneratedDataGender = str


class GeneratedDataGenderMapping(TypedDict):
    neutral: Optional[str]
    male: Optional[str]
    female: Optional[str]


class GeneratedDataWord(TypedDict):
    gender: str
    gender_map: GeneratedDataGenderMapping
    warning: Optional[Set[str]]


GeneratedGenderNounData = Dict[str, GeneratedDataWord]

# functions to check for the validity of (gendered) words/nouns:

try:
    import nltk
    try:
        nltk.data.find("corpora/words")
        nltk.data.find("corpora/wordnet")
    except LookupError:
        builtin_warnings.warn("nltk corpus (words and/or wordnet) not found; downloading it since it is small.")
        nltk.download('words', quiet=True)
        nltk.download('wordnet', quiet=True)
    from nltk.corpus import wordnet as wn
    person_synsets = set(wn.synsets("person")) | set(wn.synsets("people"))
    english_person_nouns = (
        set([w.lower() for p in person_synsets for s in p.closure(lambda s: s.hyponyms()) for w in s.lemma_names()]))
    english_nouns = set(w.name().split(".")[0].lower() for w in wn.all_synsets("n")) | english_person_nouns
    english_vocab = set(w.lower() for w in nltk.corpus.words.words()) | english_nouns

    def is_a_word(word: str) -> bool:
        """Checks whether the given word is a valid english word."""
        return set(word.lower().split("_")).issubset(english_vocab) or word.lower() in english_vocab

    def is_a_noun(word: str) -> bool:
        """Checks whether the given word is a valid english noun."""
        return set(word.lower().split("_")).issubset(english_nouns) or word.lower() in english_nouns

    def is_a_person_noun(word: str) -> bool:
        """Checks whether the given word is a valid english person noun."""
        return set(word.lower().split("_")).issubset(english_person_nouns) or word.lower() in english_person_nouns
        # ^ this function is not used anymore, but remains for purposes of testing, completeness and developement

except ImportError:
    builtin_warnings.warn("The nltk-module is not installed. Some types of helpful hints and warnings may not be "
                          + "raised, but otherwise, this is not an issue.")

    def is_a_word(word: str) -> bool:
        """Checks whether the given word is a valid english word."""
        return True

    def is_a_noun(word: str) -> bool:
        """Checks whether the given word is a valid english noun."""
        return True

    def is_a_person_noun(word: str) -> bool:
        """Checks whether the given word is a valid english person noun."""
        return True

# a helper function for logging:


def lwarn(*text, sep=" ", end="\n"):
    """Prints the given text, but only if the "BuildingGenderedNounDataLogging"-warning is enabled.
    The name "lwarn" is supposed to stand for "log warning"."""
    warnings.WarningManager.raise_warning(sep.join([str(t) for t in text]) + end,
                                          warnings.BuildingGenderedNounDataLogging)

# a pipeline for creating files that describe differently gendered versions of gendered nouns:


class GenderNounDataHandler:
    """Bundles several static methods to handle and create data that describes the differently gendered versions of
    gendered nouns.
    These methods form a pipeline used for creating a full linked graph of gendered nouns.
    All methods of the pipeline print extensive logs if the corresponding "warning" is enabled, and may or may not
    modify their input in-place.
    Please note that this pipeline is tested only in environments with nltk installed."""

    @staticmethod
    def load_from_web() -> GeneratedGenderNounData:
        """Creates a JSON object describing the differently gendered versions of every gendered noun.
        Word with no wordnet_senseno-attribute (that are not from wordnet) are ignored, and words with "other" as gender
        are re-gendered as "neutral".

        The data used for this is taken from https://github.com/ecmonsen/gendered_words
        (which is not by me; see the repository for the license)."""

        grammatical_genders = {"m": "male", "f": "female", "n": "neutral"}

        # load from the web, in a completely wrong format that we have yet to change:
        raw_json: OriginalGenderNounData = json.loads(requests.get(
            "https://raw.githubusercontent.com/phseiff/gendered_words/master/gendered_words.json").text)

        # change the format:
        result = dict()
        for word in raw_json:
            if "wordnet_senseno" in word:
                result[word["word"]] = {"gender_map": dict()}
                if "gender_map" in word:
                    for short, long in grammatical_genders.items():
                        if short in word["gender_map"]:
                            result[word["word"]]["gender_map"][long] = word["gender_map"][short][0]["word"].replace(
                                " ", "_")
                if word["gender"] == "o":
                    lwarn("Found an \"other\"-word! It's \"" + word["word"] + "\".")
                    result[word["word"]]["gender"] = "neutral"
                else:
                    result[word["word"]]["gender"] = grammatical_genders[word["gender"]]
            else:
                lwarn("\"" + word["word"] + "\" ignored because it is not part of wordnet and therefore not a hyponym "
                      + "for a person.")

        lwarn(len(result), "words found.")
        return result

    @staticmethod
    def load_from_disk(file_name: str) -> GeneratedGenderNounData:
        """Loads the gendered nouns from a piece of json data contained in the given file.
        Returns it as a dictionary, with the only change being that the `warnings`-attribute of every noun is converted
        from a list to a set.
        This assumes the data in the given file to be of the same type as the data used throughout all the other methods
        of this class, NOT the format of the repository from which `load_from_web` loads its data."""
        with open(file_name, "r") as f:
            code = f.read()
        code_as_a_dict = json.loads(code)
        for word_data in code_as_a_dict.values():
            if "warning" in word_data:
                word_data["warning"] = set(word_data["warning"])
        return code_as_a_dict

    @staticmethod
    def save_to_disk(graph: GeneratedGenderNounData, file_name: str) -> None:
        """Saves the given gendered nouns data to the given file as json. The data is saved without any modifications,
        except for the `warnings`-attribute of all noun data, which is converted from a set to a list to be compatible
        with standard json format.
        This assumes the given data to be of the same type as the data used throughout all the other methods of this
        class, NOT the format of the repository from which `load_from_web` loads its data.
        The data saved with this method can be read again with `load_from_disk`, so that `save_to_disk(data, file_name)`
        implies `load_from_disk(file_name) == data`.
        This method is guaranteed to not change the given data in-place."""
        graph_copy: dict = copy.deepcopy(graph)
        for word_data in graph_copy.values():
            if "warning" in word_data:
                word_data["warning"] = list(word_data["warning"])
                word_data["warning"].sort()
        with open(file_name, "w") as f:
            json.dump(graph_copy, f, indent=4, sort_keys=True)

    @staticmethod
    def remove_words_that_are_not_nouns(graph: GeneratedGenderNounData) -> GeneratedGenderNounData:
        """Removes all elements that are not nouns from the graph. Words that are not nouns, but whose gendered versions
        contain nouns for some reason, are not purged by this.
        Returns the result.
        This step should usually do nothing, since all words that are not nouns should already be filtered out when
        the data is read via load_from_web, but this uses an undocumented feature of the online data set it uses, so
        this function ensures that changes of that feature don't break this code.

        This step may or may not change the given object in-place."""

        grammatical_genders = ["male", "female", "neutral"]

        count = 0
        for word_name, word_data in list(graph.items()):
            is_noun = is_a_noun(word_name)
            for grammatical_gender in grammatical_genders:
                if grammatical_gender in word_data["gender_map"]:
                    is_noun = is_noun or is_a_noun(word_data["gender_map"][grammatical_gender])
            if not is_noun:
                lwarn("Deleting \"" + word_name + "\", since it is not a noun!")
                count += 1
                del graph[word_name]

        lwarn(count, "words deleted.")
        return graph

    @staticmethod
    def make_sure_all_referenced_words_exist(graph: GeneratedGenderNounData) -> GeneratedGenderNounData:
        """Returns a version of the graph where every word linked as a differently gendered version of a word exists."""

        count = 0
        for word_name, word_data in list(graph.items()):
            for gender_name, link_name in word_data["gender_map"].items():
                if link_name not in graph:
                    lwarn("\"" + word_name + "\" lists \"" + link_name + "\" as its " + gender_name + " version, but \""
                          + link_name + "\" does not exist in the word data file.")
                    count += 1
                    graph[link_name] = {"gender": gender_name, "gender_map": {word_data["gender"]: word_name}}
                # # Commented out, since it is already covered by create_extra_links_to_gender_ambiguous_words():
                # if graph[link_name]["gender"] != gender_name:
                #     lwarn("\"" + link_name + "\" is \"" + word_name + "\"s " + gender_name + "s version, but is not "
                #           + gender_name + ".")

        lwarn(count, "new words created.")
        return graph

    @staticmethod
    def choose_better_word(option1, option2, log=False):
        """There are cases where a word has two different gendered versions for the same gender;
        for example, "foremother" and "ancestress" are both female words for an ancestor. In these cases, the "better"
        one will be chosen according to this pipeline.
        This is relevant for `make_all_links_two_sided`, for example (see docstring).

        If `log` is set, having to resort to alphabetical decisions is logged."""

        # ToDo: Add further rules to this, or better yet, make manual (no automated data!) PRs to
        #  https://github.com/phseiff/gendered-words to clear up all these unnecessary unclearnesses.
        bad_things_in_order_of_badness: List[Callable[[str], int]] = [
            # the sooner the lambda, the worse it is:
            lambda word: len([c for c in word if c == "_"]),
            lambda word: int(word.endswith("man") or word.endswith("woman")),
            lambda word: int(word.endswith("person")),
            lambda word: int(word.endswith("mother") or word.endswith("father")),
            lambda word: int(word.endswith("parent"))
        ]
        for badness_meter in bad_things_in_order_of_badness:
            if badness_meter(option1) > badness_meter(option2):
                return option2
            elif badness_meter(option2) > badness_meter(option1):
                return option1
        # otherwise, return the alphabetically first one:
        if log:
            lwarn("Had to alphabetically decide between", option1, "and", option2)
        return sorted([option1, option2])[0]

    @staticmethod
    def make_all_links_two_sided(graph: GeneratedGenderNounData, log_clashs=False)\
            -> GeneratedGenderNounData:
        """Returns a version of the graph where every word linked to links back to the word linking to it, if this words
        gender is not yet in its gender mapping.
        This also goes for triangles where a links to b and c, but b and c are not linked.

        If `log_clashs` is set to True, clashes are logged (these are cases where there are multiple versions available
        for the gendered version of a word). This should only be enabled before
        `create_gendered_versions_for_words_that_end_with_gender_indicators` is called on the data for the first time,
        since afterwards, multiple words might be connected that wheren't conntected before. One example would be that
        "wonder_woman" and "wonder_girl" are both considered female, and both will get "wonder_person" assigned as their
        neutral version by `create_gendered_versions_for_words_that_end_with_gender_indicators`. This is not an issue
        since one of them already links to "wonder_boy", and the other one to "wonder_man" from the beginning, but
        they will still be considered clashing by the algorithm, so calling `make_all_links_two_sided` with
        `log_clashs` set to True after applying `create_gendered_versions_for_words_that_end_with_gender_indicators` to
         the data will create logs for two words that don't clash more than linguistically necessary.

         If `infect_warnings` isn't explicitely set to False, all warnings added to a word are "passed" to every word
         it's linked to."""

        count = 0

        # makes sure we do not report a clash twice.
        already_reported_clashes: Set[str] = set()

        def assign_value_or_use_old_one(gender_dict, gender, value):
            """Assigns a gendered version (`value`) to the given `gender` in the `gender_dict`.
            If there is already a value for the given gender, a decision is made whether to replace the old value in the
            gender dict with the newfound alternative one, and we then log the decision if `log_clashs` is set, and
            collect information required to build a warning to attach to the word to indicate that there was an
            algorithmic choose between two options."""
            if gender in gender_dict and gender_dict[gender] != value:
                # log the clash if it wasn't logged yet:
                clash_report = value + " clashes with " + gender_dict[gender]
                if log_clashs and clash_report not in already_reported_clashes:
                    lwarn(clash_report)
                    already_reported_clashes.add(clash_report)

                # choose the better of both options (keep the old word or rather use the new one):
                chosen_option = GenderNounDataHandler.choose_better_word(value, gender_dict[gender], log=log_clashs)
            else:
                chosen_option = value

            gender_dict[gender] = chosen_option
            gender_dict_alts[gender] |= {chosen_option, value}

        def get_all_connected_words(word_name, data: Union[Set[str], None] = None):
            """Returns a set of all words that are indirectly or directly linked to the given word."""
            if not data:
                data = {word_name}
            for link_name in graph[word_name]["gender_map"].values():
                if link_name not in data:
                    data.add(link_name)
                    get_all_connected_words(link_name, data)
                if link_name in link_groups:
                    data |= link_groups[link_name]
            return data

        link_groups: Dict[str, Set[str]] = dict()
        words_we_already_visited: Set[str] = set()
        # first iteration is to make FULL links groups of connected words before we start linking words to each other:
        for word_name, word_data in graph.items():
            if word_name not in words_we_already_visited:

                # create group of all words that are linked to this word (including those that are once removed):
                link_group = get_all_connected_words(word_name)
                for link_name in link_group:
                    if link_name in link_groups:
                        link_groups[link_name] |= link_group
                    else:
                        link_groups[link_name] = link_group

                # add these words to the visited words now:
                words_we_already_visited |= link_group

        # second iteration is to actually do the linking:
        words_we_already_visited: Set[str] = set()
        for word_name in graph.keys():
            # if we did not visit this word yet:
            if word_name not in words_we_already_visited:
                link_group = link_groups[word_name]
                words_we_already_visited |= link_group

                # create a gender-dict for all of them:
                genders_we_are_very_sure_about: Set[GeneratedDataGender] = set()
                gender_dict: Dict[GeneratedDataGender, str] = dict()
                gender_dict_alts: Dict[GeneratedDataGender, Set[str]] = {"female": set(), "male": set(),
                                                                         "neutral": set()}
                for link_name in link_group:
                    # add gender of the individual...
                    gender = graph[link_name]["gender"]
                    if gender in genders_we_are_very_sure_about:
                        assign_value_or_use_old_one(gender_dict, gender, link_name)
                    else:
                        gender_dict_alts[gender] = {link_name}
                        gender_dict[gender] = link_name
                    genders_we_are_very_sure_about.add(gender)

                    # ...as well as genders it specifies in its gender_map, but only if we couldn't find these otherwise
                    for gender, link_name2 in graph[link_name]["gender_map"].items():
                        if gender not in genders_we_are_very_sure_about:
                            assign_value_or_use_old_one(gender_dict, gender, link_name2)

                # link words with each other, so each word gets the full gender dict to call its own,
                # but only for genders it does not have in its own original gender dict yet, so manual links in the
                # already given data take precedence:
                for link_name in link_group:
                    for gender, link_name2 in gender_dict.items():
                        if gender not in graph[link_name]["gender_map"] and gender != graph[link_name]["gender"]:
                            graph[link_name]["gender_map"][gender] = link_name2
                            lwarn("\"" + link_name + "\" is (indirectly) linked to \"" + link_name2
                                  + "\", which is " + graph[link_name2]["gender"], " but \"" + link_name
                                  + "\" has no " + graph[link_name2]["gender"] + " version.")
                            count += 1

                            # if the newly added link was chosen between two possible words algorithmically, add this as
                            # a warning:
                            if gender_dict_alts[gender] != {link_name2}:
                                if "warning" not in graph[link_name]:
                                    graph[link_name]["warning"] = set()
                                alt_values = sorted(list(gender_dict_alts[gender]))
                                alt_values_str = ", ".join(alt_values[:-1]) + " and " + alt_values[-1]
                                new_warning = (alt_values_str + " would've all been good values for the " + gender + " "
                                               + "version of \"" + link_name + "\", but \"" + link_name2
                                               + "\" was automatically chosen based on an algorithm.")
                                lwarn(new_warning)
                                graph[link_name]["warning"].add(new_warning)

                # infect linked words with the warnings of the words they're linked to:
                link_group_warnings = set()
                for link_name in link_group:
                    if "warning" in graph[link_name]:
                        link_group_warnings |= graph[link_name]["warning"]
                if link_group_warnings:
                    for link_name in link_group:
                        if "warning" not in graph[link_name]:
                            graph[link_name]["warning"] = set()
                        graph[link_name]["warning"] |= link_group_warnings

        lwarn(count, "links created.")
        return graph

    @staticmethod
    def create_extra_links_to_gender_ambiguous_words(graph: GeneratedGenderNounData) -> GeneratedGenderNounData:
        """There may be some words A with gender x, that list another word B as their gender-y-version, but don't have
        any gender-z-version, and word B is listet as gender z for some reason.
        This method returns a version of the given graph where A links to B as its gender-z-version."""

        count = 0
        for word_name, word_data in graph.items():
            for gender_name, link_name in list(word_data["gender_map"].items()):
                if graph[link_name]["gender"] not in word_data["gender_map"]:
                    if graph[link_name]["gender"] != word_data["gender"]:
                        word_data["gender_map"][graph[link_name]["gender"]] = link_name
                        lwarn("\"" + word_name + "\" does not have a " + graph[link_name]["gender"] + " version, but a "
                              + "word it links to as its " + gender_name + " version is " + graph[link_name]["gender"]
                              + ".")
                        count += 1

        lwarn(count, "links created.")
        return graph

    @staticmethod
    def create_gendered_versions_for_words_that_end_with_gender_indicators(graph: GeneratedGenderNounData)\
            -> GeneratedGenderNounData:
        """Some words end on "-man" or "-woman", or similar things like "boy" or "maid", but don't have a male/female/
        neutral version. This method returns a version of the graph where every word of these has a male, female as well
        as neutral version. It also ensures that the resulting word doesn't end with "_" due to having its end or
        beginning removed, and that it doesn't create "empty" words."""

        # ToDo: better suggestions regarding the maid/maiden/boy/girl-stuff are welcome!
        # ToDo: running replacement strategies like this when creating a tag with a GenderedNoun-object for an unknown
        #  noun might be a good idea... this would, however, require figuring out a words gender, so the table we have
        #  here would have to be accessible outside this function.
        #  Feel free to submit a pull request for this, or an issue if you see this fitting!
        gender_indicator_tuples_table = [
            ("start", [("female", "female"),   ("male", "male"),       ("neutral", "")]),

            ("end",   [("female", "woman"),    ("male", "man"),        ("neutral", "person")]),
            ("end",   [("female", "girl"),     ("male", "boy"),        ("neutral", "bean")]),
            ("end",   [("female", "maiden"),   ("male", "gentleman"),  ("neutral", "gentleperson")]),
            ("end",   [("female", "maid"),     ("male", "manservant"), ("neutral", "servant")]),  # or butler? domestic?
            ("end",   [("female", "aunt"),     ("male", "uncle"),      ("neutral", "auncle")]),
            ("end",   [("female", "daughter"), ("male", "son"),        ("neutral", "child")]),
            ("end",   [("female", "mother"),   ("male", "father"),     ("neutral", "parent")]),
            ("end",   [("female", "wife"),     ("male", "husband"),    ("neutral", "spouse")]),
            ("end",   [("female", "niece"),    ("male", "nephew"),     ("neutral", "nibling")]),
            ("end",   [("female", "female"),   ("male", "male"),       ("neutral", "person")]),
            ("end",   [("female", "sister"),   ("male", "brother"),    ("neutral", "sibling")]),
            ("end",   [("female", "queen"),    ("male", "king"),       ("neutral", "monarch")]),

            ("start", [("female", "woman"),    ("male", "man"),        ("neutral", "person")]),
            ("start", [("female", "girl"),     ("male", "boy"),        ("neutral", "bean")]),
            ("start", [("female", "maiden"),   ("male", "gentleman"),  ("neutral", "gentleperson")]),
            ("start", [("female", "maid"),     ("male", "manservant"), ("neutral", "servant")]),
            ("start", [("female", "aunt"),     ("male", "uncle"),      ("neutral", "auncle")]),
            ("start", [("female", "daughter"), ("male", "son"),        ("neutral", "child")]),
            ("start", [("female", "mother"),   ("male", "father"),     ("neutral", "parent")]),
            ("start", [("female", "wife"),     ("male", "husband"),    ("neutral", "spouse")]),
            ("start", [("female", "niece"),    ("male", "nephew"),     ("neutral", "nibling")]),
            ("start", [("female", "female"),   ("male", "male"),       ("neutral", "person")]),
            ("start", [("female", "sister"),   ("male", "brother"),    ("neutral", "sibling")]),
            ("start", [("female", "queen"),    ("male", "king"),       ("neutral", "monarch")])
        ]

        words_created = 0
        links_created = 0
        for word_name, word_data in list(graph.items()):
            for end_or_start, gender_indicator_tuples in gender_indicator_tuples_table:
                created_corresponding_gendered_versions = False
                for gender, gender_indicator in gender_indicator_tuples:
                    if (((end_or_start == "end" and word_name.endswith(gender_indicator))
                            or (end_or_start == "start" and word_name.startswith(gender_indicator)))
                            and gender_indicator):
                        not_applicable = False
                        if gender != "neutral":
                            other_gender_indicator_tuples = [
                                t for t in gender_indicator_tuples if t != (gender, gender_indicator)]
                            for other_gender, other_gender_indicator in other_gender_indicator_tuples:
                                if other_gender not in set(word_data["gender_map"].keys()) | {word_data["gender"]}:
                                    # figure out the potential new word:
                                    if end_or_start == "end":
                                        new_gendered_version = (word_name[:-len(gender_indicator)]
                                                                + other_gender_indicator)
                                    else:
                                        new_gendered_version = (other_gender_indicator
                                                                + word_name[len(gender_indicator):])
                                    new_gendered_version = new_gendered_version.lstrip("_").rstrip("_")
                                    if new_gendered_version == "":
                                        not_applicable = True
                                        continue
                                    # create the new word or link to it:
                                    lwarn("\"" + word_name + "\" ends with \"-" + gender_indicator
                                          + "\", but it has no " + other_gender + " version. ", end="")
                                    word_data["gender_map"][other_gender] = new_gendered_version
                                    links_created += 1
                                    if new_gendered_version not in graph:
                                        lwarn("Creating one as \"" + new_gendered_version + "\"!")
                                        words_created += 1
                                        graph[new_gendered_version] = {
                                            "gender": other_gender,
                                            "gender_map": dict(),
                                            "warning": {"\"" + new_gendered_version
                                                        + "\" was automatically generated as the " + other_gender
                                                        + " version of a word due to the "
                                                        + ("ending" if end_or_start == "end" else "beginning")
                                                        + " of said " + "word."}
                                        }
                                    else:
                                        lwarn("Linking to \"" + new_gendered_version + "\".")
                                    # Add a new warning that a link was created between those two:
                                    if "warning" not in word_data:
                                        word_data["warning"] = set()
                                    word_data["warning"].add("\"" + new_gendered_version
                                                             + "\" was automatically linked to \"" + word_name
                                                             + "\" as its " + gender + " version due to the "
                                                             + ("ending" if end_or_start == "end" else "beginning")
                                                             + " of said " + "word.")

                        if not not_applicable:
                            created_corresponding_gendered_versions = True
                            break
                if created_corresponding_gendered_versions:
                    break

        lwarn(words_created, "new words created.")
        lwarn(links_created, "new links created.")
        return graph

    @staticmethod
    def find_words_with_no_neutral_form(graph: GeneratedGenderNounData) -> GeneratedGenderNounData:
        """Informs about every word that does not have a neutral version, and uses this word as its own neutral version.
        Gives each of these words a neutral form by using the male version of the word by default and the female version
        if there is no male one."""

        count_male = 0
        count_used_male = 0
        count_used_female = 0
        count = 0
        for word_name, word_data in list(graph.items()):
            if word_data["gender"] != "neutral":
                if "neutral" not in word_data["gender_map"]:
                    lwarn("\"" + word_name + "\" is neither neutral, nor does it link to a neutral version.")
                    count += 1
                    if word_data["gender"] == "male":
                        word_data["gender_map"]["neutral"] = word_name
                        if "warning" not in word_data:
                            word_data["warning"] = set()
                        word_data["warning"].add("\"" + word_name + "\" does not have an explicit, human-picked "
                                                 + "neutral version, and since it is male, it's automatically used as "
                                                 + "own neutral version. This is done because lots of words in the "
                                                 + "database are wrongly marked as male even though they are actually "
                                                 + "neutral.")
                        count_male += 1
                    elif "male" in word_data["gender_map"]:
                        word_data["gender_map"]["neutral"] = word_data["gender_map"]["male"]
                        if "warning" not in word_data:
                            word_data["warning"] = set()
                        word_data["warning"].add("\"" + word_name + "\" does not have an explicit, human-picked "
                                                 + "neutral version, and since it has a male version, this version is "
                                                 + "automatically used as its neutral version. This is done because "
                                                 + "lots of words in the  database are wrongly marked as male even "
                                                 + "though they are actually neutral.")
                        count_used_male += 1
                    else:
                        if "warning" not in word_data:
                            word_data["warning"] = set()
                        word_data["gender_map"]["neutral"] = word_name
                        word_data["warning"].add("\"" + word_name + "\" neither has a male nor a female version, so "
                                                 + "it is used as its own neutral version.")
                        count_used_female += 1
                    lwarn(word_data["warning"])

        lwarn(count, "instances found.")
        lwarn(count_male, "instances where male words where used as their own neutral version,")
        lwarn(count_used_male, "instances where a male version of a word was used as its neutral version,")
        lwarn(count_used_female, "instances where a female word was used as its own neutral version.")

        return graph

    @staticmethod
    def create_full_graph_from_web() -> GeneratedGenderNounData:
        """A pipeline that combines all methods of this method collection to pull a graph of gendered words from the web
        and automatically fill all holes this graph has left open."""

        graph = GenderNounDataHandler.load_from_web()
        lwarn("")
        graph = GenderNounDataHandler.remove_words_that_are_not_nouns(graph)

        lwarn("")
        graph = GenderNounDataHandler.make_sure_all_referenced_words_exist(graph)
        lwarn("")
        graph = GenderNounDataHandler.make_all_links_two_sided(graph)

        lwarn("")
        graph = GenderNounDataHandler.create_extra_links_to_gender_ambiguous_words(graph)
        lwarn("")
        graph = GenderNounDataHandler.make_all_links_two_sided(graph, log_clashs=True)

        lwarn("")
        graph = GenderNounDataHandler.create_gendered_versions_for_words_that_end_with_gender_indicators(graph)
        lwarn("")
        graph = GenderNounDataHandler.make_all_links_two_sided(graph)

        lwarn("")
        graph = GenderNounDataHandler.find_words_with_no_neutral_form(graph)
        return graph


# the final dict:

save_as = os.path.join(__file__.rsplit(os.sep, 1)[0], "gendered-nouns.gdn")
try:
    GENDER_DICT: GeneratedGenderNounData = GenderNounDataHandler.load_from_disk(save_as)
except FileNotFoundError:
    warnings.WarningManager.raise_warning(None, warnings.GenderedNounsBuildFromWebWarning)
    g = GenderNounDataHandler.create_full_graph_from_web()
    GenderNounDataHandler.save_to_disk(g, save_as)
    GENDER_DICT: GeneratedGenderNounData = GenderNounDataHandler.load_from_disk(save_as)


# Representation of a not-yet correctly gendered noun:

class GenderedNoun:
    """A representation of a gendered noun, with methods to get gendered equivalents of it."""

    def __init__(self, word: str):
        """Generates an object to get gendered versions of the given noun for different genders."""

        # save the full word, but lookup the word in lowercase:
        self.word = word
        word = word.lower()
        # ToDo: Maye warn if the word has upper-case letters after the first one? If so, what kind of warning?

        # raise warnings if the word is not a word/ noun/ person noun:
        if word not in GENDER_DICT:
            if not is_a_word(word):
                warnings.WarningManager.raise_warning("\"" + word + "\" is not a known word, so gender*render might not"
                                                      + " be able to gender it correctly.", warnings.NotAWordWarning)
            elif not is_a_noun(word):
                warnings.WarningManager.raise_warning("\"" + word + "\" is not a known noun, so gender*render might not"
                                                      + " be able to gender it correctly.", warnings.NotANounWarning)
            else:
                warnings.WarningManager.raise_warning("\"" + word + "\" is not a hyponym for person, so gender*render "
                                                      + "might not be able to gender it correctly.",
                                                      warnings.NotAPersonNounWarning)
        elif "warning" in GENDER_DICT[word]:
            warnings.WarningManager.raise_warning("warnings for \"" + word + "\":\n"
                                                  + "\n".join(list(GENDER_DICT[word]["warning"])),
                                                  warnings.NounGenderingGuessingsWarning)
            # ToDo: Maybe only print those warnings that contain `"\"" + word + "\""` in them? This would require
            #  reviewing all warnings attached to words by this modules code, to be sure this actually prints all
            #  relevant warnings, as well as injecting some trivial code here and generalyl discussign this idea in an
            #  issue.
            #  See also the comment in test/test_gender_nouns in test_create_full_graph_from_web.

    def render_noun(self, gender: GeneratedDataGender) -> str:
        """Returns the correctly gendered version of itself as a string. g must be either "male", "female" or
        "neutral".
        Capitalisation of the first letter is identical between out- and input."""
        # remember if the first letter of the word is uppercase:
        if self.word[0].isupper():  # ToDo: Maybe add support for all-caps-writing? What about words with "_"in them?
            uppercase = True
        else:
            uppercase = False

        # return the correctly gendered version of the word:
        if self.word.lower() in GENDER_DICT:
            word = self.word.lower()
            word_data = GENDER_DICT[word]
            # look for the neutral version if there is no version of the given gender:
            if gender not in set(word_data["gender_map"].keys()) | {word_data["gender"]}:
                gender = "neutral"
            # return the word if it is the right gender:
            if GENDER_DICT[word]["gender"] == gender:
                result = word
            # otherwise, return the correctly gendered version from the gender_map:
            else:
                result = word_data["gender_map"][gender]
            # make the first letter of the result uppercase in case we had to lowercase it before:
            if uppercase:
                result = result[0].upper() + result[1:]
        else:
            result = self.word
        return result.replace("_", " ")

    def __eq__(self, other) -> bool:
        """Checks whether two GenderedNoun-representations are identical, based on what noun they represent."""
        if isinstance(other, self.__class__):
            return self.word == other.word
        else:
            return False
