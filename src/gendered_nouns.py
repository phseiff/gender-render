"""Functions to gender nouns with gender bias correctly."""

import requests
import json
import warnings as builtin_warnings

from . import warnings

# functions to check for the validity of (gendered) words/nouns:

try:
    import nltk
    try:
        nltk.data.find("corpora/words")
        nltk.data.find("corpora/wordnet")
    except LookupError:
        nltk.download('words')
        nltk.download('wordnet')
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

# a pipeline for creating files that describe differently gendered versions of gendered nouns:


class GenderNounDataHandler:
    """Bundles several static methods to handle and create data that describes the differently gendered versions of
    gendered nouns.
    These methods form a pipeline used for creating a full linked graph of gendered nouns.
    All methods of the pipeline print extensive logs, and may or may not modify their input in-place."""

    @staticmethod
    def load_from_web() -> dict:
        """Creates a JSON object describing the differently gendered versions of every gendered noun.

        The data used for this is taken from https://github.com/ecmonsen/gendered_words
        (which is not by me; see the repository for the license)."""

        grammatical_genders = {"m": "male", "f": "female", "n": "neutral"}

        # load from the web, in a completely wrong format that we have yet to change:
        raw_json = json.loads(requests.get(
            "https://raw.githubusercontent.com/ecmonsen/gendered_words/master/gendered_words.json").text)

        # change the format:
        result = dict()
        for word in raw_json:
            if "wordnet_senseno" in word:
                result[word["word"]] = {"gender_map": dict()}
                if "gender_map" in word:
                    for short, long in grammatical_genders.items():
                        if short in word["gender_map"]:
                            result[word["word"]]["gender_map"][long] = word["gender_map"][short][0]["word"]
                if word["gender"] == "o":
                    print("Found an \"other\"-word! It's \"" + word["word"] + "\".")
                    result[word["word"]]["gender"] = "neutral"
                else:
                    result[word["word"]]["gender"] = grammatical_genders[word["gender"]]
            else:
                print("\"" + word["word"] + "\" ignored because it is not part of wordnet and therefore not a hyponym "
                      + "for a person.")

        print(len(result), "words found.")
        return result

    @staticmethod
    def remove_words_that_are_not_nouns(graph: dict) -> dict:
        """Removes all elements that are not nouns from the graph.
        Returns the result."""

        grammatical_genders = ["male", "female", "neutral"]

        count = 0
        for word_name, word_data in list(graph.items()):
            is_noun = is_a_noun(word_name)
            for grammatical_gender in grammatical_genders:
                if grammatical_gender in word_data["gender_map"]:
                    is_noun = is_noun or is_a_noun(word_data["gender_map"][grammatical_gender])
            if not is_noun:
                print("Deleting \"" + word_name + "\", since it is not a noun!")
                count += 1
                del graph[word_name]

        print(count, "words deleted.")
        return graph

    @staticmethod
    def make_sure_all_referenced_words_exist(graph: dict) -> dict:
        """Returns a version of the graph where every word linked as a differently gendered version of a word exists."""

        count = 0
        for word_name, word_data in list(graph.items()):
            for gender_name, link_name in word_data["gender_map"].items():
                if link_name not in graph:
                    print("\"" + word_name + "\" lists \"" + link_name + "\" as its " + gender_name + " version, but \""
                          + link_name + "\" does not exist in the word data file.")
                    count += 1
                    graph[link_name] = {"gender": gender_name, "gender_map": {word_data["gender"]: word_name}}
                # # Commented out, since it is already covered by create_extra_links_to_gender_ambiguous_words():
                # if graph[link_name]["gender"] != gender_name:
                #     print("\"" + link_name + "\" is \"" + word_name + "\"s " + gender_name + "s version, but is not "
                #           + gender_name + ".")

        print(count, "new words created.")
        return graph

    @staticmethod
    def make_all_links_two_sided(graph: dict) -> dict:
        """Returns a version of the graph where every word linked to links back to the word linking to it, if this words
        gender is not yet in its gender mapping.
        This also goes for triangles where a links to b and c, but b and c are not linked."""

        count = 0
        words_we_already_visited = set()
        for word_name, word_data in graph.items():
            # check if we already visited this word:
            word_is_first_word_of_group = True
            for gender_name, link_name in list(word_data["gender_map"].items()):
                if link_name in words_we_already_visited:
                    word_is_first_word_of_group = False
            words_we_already_visited.add(word_name)
            # if we did not visit this word yet:
            if word_is_first_word_of_group:
                # create group of all words that are linked to this word (including those that are once removed):
                link_group = {word_name}
                for link_name in word_data["gender_map"].values():
                    link_group.add(link_name)
                for link_name in list(link_group):
                    for link_name2 in graph[link_name]["gender_map"].values():
                        link_group.add(link_name2)
                # links them with each other:
                for link_name in link_group:
                    for link_name2 in link_group:
                        if link_name != link_name2:
                            if graph[link_name2]["gender"] not in graph[link_name]["gender_map"]:
                                graph[link_name]["gender_map"][graph[link_name2]["gender"]] = link_name2
                                print("\"" + link_name + "\" is indirectly linked to \"" + link_name2 + "\", which is "
                                      + graph[link_name2]["gender"], " but \"" + link_name + "\" has no "
                                      + graph[link_name2]["gender"] + " version.")
                                count += 1
            else:
                continue

        print(count, "links created.")
        return graph

    @staticmethod
    def create_extra_links_to_gender_ambiguous_words(graph: dict) -> dict:
        """There may be some words A with gender x, that list another word B as their gender-y-version, but don't have
        any gender-z-version, and word B is listet as gender z for some reason.
        This method returns a version of the given graph where A links to B as its gender-z-version."""

        count = 0
        for word_name, world_data in graph.items():
            for gender_name, link_name in list(world_data["gender_map"].items()):
                if graph[link_name]["gender"] not in world_data["gender_map"]:
                    world_data["gender_map"][graph[link_name]["gender"]] = link_name
                    print("\"" + word_name + "\" does not have a " + graph[link_name]["gender"] + " version, but the "
                          + "word it links to as its " + gender_name + " version is " + graph[link_name]["gender"]
                          + ".")
                    count += 1

        print(count, "links created.")
        return graph

    @staticmethod
    def create_gendered_versions_for_words_that_end_with_gender_indicators(graph: dict) -> dict:
        """Some words end on "-man" or "-woman", or similar things like "boy" or "maid", but don't have a male/female/
        neutral version. This method returns a version of the graph where every word of these has a male, female as well
        as neutral version."""

        # ToDo: better suggestions regarding the maid/maiden/boy/girl-stuff are welcome!
        gender_indicator_tuples_table = [
            ("start", [("female", "female"),   ("male", "male"),       ("neutral", "")]),

            ("end",   [("female", "woman"),    ("male", "man"),        ("neutral", "person")]),
            ("end",   [("female", "girl"),     ("male", "boy"),        ("neutral", "person")]),
            ("end",   [("female", "maiden"),   ("male", "gentleman"),  ("neutral", "gentleperson")]),
            ("end",   [("female", "maid"),     ("male", "manservant"), ("neutral", "servant")]),
            ("end",   [("female", "aunt"),     ("male", "uncle"),      ("neutral", "auncle")]),
            ("end",   [("female", "daughter"), ("male", "son"),        ("neutral", "child")]),
            ("end",   [("female", "mother"),   ("male", "father"),     ("neutral", "parent")]),
            ("end",   [("female", "wife"),     ("male", "husband"),    ("neutral", "spouse")]),
            ("end",   [("female", "niece"),    ("male", "nephew"),     ("neutral", "nibling")]),
            ("end",   [("female", "female"),   ("male", "male"),       ("neutral", "person")]),
            ("end",   [("female", "sister"),   ("male", "brother"),    ("neutral", "sibling")]),

            ("start", [("female", "woman"),    ("male", "man"),        ("neutral", "person")]),
            ("start", [("female", "girl"),     ("male", "boy"),        ("neutral", "person")]),
            ("start", [("female", "maiden"),   ("male", "gentleman"),  ("neutral", "gentleperson")]),
            ("start", [("female", "maid"),     ("male", "manservant"), ("neutral", "servant")]),
            ("start", [("female", "aunt"),     ("male", "uncle"),      ("neutral", "auncle")]),
            ("start", [("female", "daughter"), ("male", "son"),        ("neutral", "child")]),
            ("start", [("female", "mother"),   ("male", "father"),     ("neutral", "parent")]),
            ("start", [("female", "wife"),     ("male", "husband"),    ("neutral", "spouse")]),
            ("start", [("female", "niece"),    ("male", "nephew"),     ("neutral", "nibling")]),
            ("start", [("female", "female"),   ("male", "male"),       ("neutral", "person")]),
            ("start", [("female", "sister"),   ("male", "brother"),    ("neutral", "sibling")])
        ]

        words_created = 0
        links_created = 0
        for word_name, word_data in list(graph.items()):
            for end_or_start, gender_indicator_tuples in gender_indicator_tuples_table:
                created_corresponding_gendered_versions = False
                for gender_name, gender_indicator in gender_indicator_tuples:
                    if (((end_or_start == "end" and word_name.endswith(gender_indicator))
                            or (end_or_start == "start" and word_name.startswith(gender_indicator)))
                            and gender_indicator):
                        if gender_name != "neutral":
                            other_gender_indicator_tuples = [
                                t for t in gender_indicator_tuples if t != (gender_name, gender_indicator)]
                            for other_gender_name, other_gender_indicator in other_gender_indicator_tuples:
                                if other_gender_name not in set(word_data["gender_map"].keys()) | {word_data["gender"]}:
                                    if end_or_start == "end":
                                        new_gendered_version = (word_name[:-len(gender_indicator)]
                                                                + other_gender_indicator)
                                    else:
                                        new_gendered_version = (other_gender_indicator
                                                                + word_name[len(gender_indicator):])
                                    print("\"" + word_name + "\" ends with \"-" + gender_indicator
                                          + "\", but it has no " + other_gender_name + " version. ", end="")
                                    word_data["gender_map"][other_gender_name] = new_gendered_version
                                    links_created += 1
                                    if new_gendered_version not in graph:
                                        print("Creating one as \"" + new_gendered_version + "\"!")
                                        words_created += 1
                                        graph[new_gendered_version] = {
                                            "gender": other_gender_name,
                                            "gender_map": dict(),
                                            "warning": ("\"" + new_gendered_version
                                                        + " was automatically generated as the " + other_gender_name
                                                        + " version of \"" + word_name + "\" due to the ending of said "
                                                        + "word.")
                                        }
                                    else:
                                        print("")
                        created_corresponding_gendered_versions = True
                        break
                if created_corresponding_gendered_versions:
                    break

        print(words_created, "new words created.")
        print(links_created, "new links created.")
        return graph

    @staticmethod
    def find_words_with_no_neutral_form(graph: dict) -> dict:
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
                    print("\"" + word_name + "\" is neither neutral, nor does it link to a neutral version.")
                    count += 1
                    if word_data["gender"] == "male":
                        word_data["gender_map"]["neutral"] = word_name,
                        word_data["warning"] = ("\"" + word_name + "\" does not have an explicit, human-picked "
                                                + "neutral version, and since it is male, it's automatically used as "
                                                + "own neutral version. This is done because lots of words in the "
                                                + "database are wrongly marked as male even though they are actually "
                                                + "neutral.")
                        count_male += 1
                    elif "male" in word_data["gender_map"]:
                        word_data["gender_map"]["neutral"] = word_data["gender_map"]["male"]
                        word_data["warning"] = ("\"" + word_name + "\" does not have an explicit, human-picked "
                                                + "neutral version, and since it has a male version, this version is "
                                                + "automatically used as its neutral version. This is done because "
                                                + "lots of words in the  database are wrongly marked as male even "
                                                + "though they are actually neutral.")
                        count_used_male += 1
                    else:
                        word_data["gender_map"]["neutral"] = word_name
                        word_data["warning"] = ("\"" + word_name + "\" neither has a male nor a female version, so "
                                                + "it is used as its own neutral version.")
                        count_used_female += 1
                    print(word_data["warning"])

        print(count, "instances found.")
        print(count_male, "instances where male words where used as their own neutral version,")
        print(count_used_male, "instances where a male version of a word was used as its neutral version,")
        print(count_used_female, "instances where a female word was used as its own neutral version.")

        return graph

    @staticmethod
    def create_full_graph_from_web() -> dict:
        """A pipeline that combines all methods of this method collection to pull a graph of gendered words from the web
        and automatically fill all holes this graph has left open."""

        graph = GenderNounDataHandler.load_from_web()
        print("")
        graph = GenderNounDataHandler.remove_words_that_are_not_nouns(graph)

        for method in (
                GenderNounDataHandler.make_sure_all_referenced_words_exist,
                GenderNounDataHandler.create_extra_links_to_gender_ambiguous_words,
                GenderNounDataHandler.create_gendered_versions_for_words_that_end_with_gender_indicators,
        ):
            print("")
            graph = method(graph)
            print("")
            graph = GenderNounDataHandler.make_all_links_two_sided(graph)

        print("")
        GenderNounDataHandler.find_words_with_no_neutral_form(graph)
        return graph


# the final dict:

GENDER_DICT: dict = GenderNounDataHandler.create_full_graph_from_web()


# Representation of a not-yet correctly gendered noun:

class GenderedNoun:
    """A representation of a gendered noun, with methods to get gendered equivalents of it."""

    def __init__(self, word: str):
        """Generates an object to get gendered versions of the given noun for different genders."""

        self.word = word

        # raise warnings if the word is not a word/ noun/ person noun:
        if not is_a_word(word):
            warnings.WarningManager.raise_warning("\"" + word + "\" is not a known word, so gender*render might not be "
                                                  + "able to gender it correctly.", warnings.NotAWordWarning)
        elif not is_a_noun(word):
            warnings.WarningManager.raise_warning("\"" + word + "\" is not a known noun, so gender*render might not be "
                                                  + "able to gender it correctly.", warnings.NotAWordWarning)
        elif not is_a_person_noun(word):
            warnings.WarningManager.raise_warning("\"" + word + "\" is not a known word for a profession or person, so "
                                                  + "gender*render might not be able to gender it correctly.",
                                                  warnings.NotAWordWarning)
        elif "warning" in GENDER_DICT[self.word]:
            warnings.WarningManager.raise_warning(GENDER_DICT[self.word]["warning"],
                                                  warnings.NounGenderingGuessingsWarning)

    def render_noun(self, gender: str) -> str:
        """Returns the correctly gendered version of itself as a string. g must be either "male", "female" or
        "neutral".
        Capitalisation of the first letter is identical between out- and input."""
        if self.word[0].isupper():  # ToDo: Maybe add support for all-caps-writing?
            uppercase = True
        else:
            uppercase = False
        if self.word in GENDER_DICT:
            if GENDER_DICT[self.word]["gender"] == gender:
                return self.word
            else:
                gender_map = GENDER_DICT[self.word.lower()]["gender_map"]
                if gender not in gender_map:
                    gender = "neural"
                result = gender_map[gender]
                if uppercase:
                    return result[0].upper() + result[1:]
                else:
                    return result
        else:
            return self.word
