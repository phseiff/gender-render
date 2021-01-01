
import unittest
import os
import shutil
import warnings
import sys
import logging
import copy
import importlib
import requests
import json
from test import check_type
from deepdiff import DeepDiff
import typing_extensions

import src
import src.gender_nouns as gn
import src.warnings as ws
import src.errors as err
from src.gender_nouns import GenderNounDataHandler

"""# disable logging:
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger()
initial_handler = logger.handlers[0]
f = open("/tmp/debug", "w")
lh = logging.StreamHandler(f)
logger.addHandler(lh)
logger.removeHandler(initial_handler)"""


class TestImportOfTypingModule(unittest.TestCase):
    # the import of the typing_extensions-module in addition to the typing-module, in cases where it is installed, is
    # only relevant for testing, so we need to check if src.gender_nouns initializes correctly without typing_extensions
    # available.

    def test_initializes_correctly_without_typing_extensions(self) -> None:
        # hide typing_extensions module:
        self.__typing_extensions = sys.modules["typing_extensions"]
        sys.modules["typing_extensions"] = None

        # make sure src.gender_nouns can initialize correctly without it:
        importlib.reload(sys.modules["src.gender_nouns"])

        # un-hide it and reload the src.gender_nouns:
        sys.modules["typing_extensions"] = self.__typing_extensions
        importlib.reload(sys.modules["src.gender_nouns"])


class TestHelperFunctionsWithoutNLTKInstalled(unittest.TestCase):

    def setUp(self) -> None:
        # make sure nltk is not installed for the test:
        self.__nltk = sys.modules["nltk"]
        sys.modules["nltk"] = None
        with self.assertWarns(UserWarning) as warning:
            importlib.reload(sys.modules["src.gender_nouns"])
        self.assertTrue("The nltk-module is not installed" in str(warning.warning))

    def tearDown(self) -> None:
        # make sure nltk is installed for further tests:
        sys.modules["nltk"] = self.__nltk
        importlib.reload(sys.modules["src.gender_nouns"])

    def test_is_a_word(self):
        # returns True for everything:
        self.assertTrue(src.gender_nouns.is_a_word("wuwuwu"))
        self.assertTrue(src.gender_nouns.is_a_word("swiping"))

    def test_is_a_noun(self):
        # returns True for everything:
        self.assertTrue(src.gender_nouns.is_a_noun("wuwuwu"))
        self.assertTrue(src.gender_nouns.is_a_noun("carpet"))

    def test_is_a_person_noun(self):
        # returns True for everything:
        self.assertTrue(src.gender_nouns.is_a_person_noun("wuwuwu"))
        self.assertTrue(src.gender_nouns.is_a_person_noun("carpeter"))


class TestHelperFunctionsWithNLTKInstalled(unittest.TestCase):

    def test_is_a_word(self):
        # returns True for every word, be it a verb, a noun or a person noun, but not for fake nouns:
        fkt = src.gender_nouns.is_a_word
        self.assertFalse(fkt("wuwuwu"))
        self.assertTrue(fkt("eat"))
        self.assertTrue(fkt("candle"))
        self.assertTrue(fkt("carpenter"))

    def test_is_a_noun(self):
        # returns True for every noun, including person nouns, but not for verbs or fake words:
        fkt = src.gender_nouns.is_a_noun
        self.assertFalse(fkt("wuwuwu"))
        self.assertFalse(fkt("eat"))
        self.assertTrue(fkt("candle"))
        self.assertTrue(fkt("carpenter"))

    def test_is_a_person_noun(self):
        # returns True person nouns, but not for other nouns, words or fake words:
        fkt = src.gender_nouns.is_a_person_noun
        self.assertFalse(fkt("wuwuwu"))
        self.assertFalse(fkt("eat"))
        self.assertFalse(fkt("candle"))
        self.assertTrue(fkt("carpenter"))


class TestCreateNewNounData(unittest.TestCase):

    def test_create_noun_data(self):
        # test if noun data is correctly generated when the `gender-nouns.gdn`-file is missing and has to be rebuild
        # on initialization.
        # the outcome should be identical to what it contained before it was deleted, and also, to the result of the
        # render pipeline.

        # create copy and reload module:
        old_gender_dict = copy.deepcopy(gn.GENDER_DICT)
        pipeline_output = GenderNounDataHandler.create_full_graph_from_web()
        os.remove("src/gendered-nouns.gdn")
        with self.assertWarns(ws.GenderedNounsBuildFromWebWarning):
            importlib.reload(sys.modules["src.gender_nouns"])

        # check for equality:
        self.assertEqual(old_gender_dict, pipeline_output)
        self.assertEqual(old_gender_dict, gn.GENDER_DICT)
        self.assertEqual(pipeline_output, gn.GENDER_DICT)


class TestInstallWordnetCorpusIfItIsNotPresent(unittest.TestCase):

    def test_install_wordnet(self):
        # make sure nltk is installed, but wordnet is not:
        import nltk
        path_to_wordnet = nltk.data.find("corpora/wordnet")
        shutil.rmtree(path_to_wordnet)
        os.remove(os.path.join(path_to_wordnet + ".zip"))
        with warnings.catch_warnings(record=True):
            for m in sys.modules:
                if m.rsplit(".", 1)[0] == "nltk":
                    importlib.reload(sys.modules[m])

        # test if properly installed
        with self.assertWarns(UserWarning) as warning:
            importlib.reload(sys.modules["src.gender_nouns"])
        self.assertTrue("nltk corpus (words and/or wordnet) not found" in str(warning.warning))

        # should not raise an error, cause nltk should be reinstalled:
        import nltk
        nltk.data.find("corpora/wordnet")


def test_lwarn(self):
    # tests if it raises the warning properly:
    with self.assertWarns(ws.BuildingGenderedNounDataLogging) as warning:
        gn.lwarn("wuwuwu")
    self.assertTrue("wuwuwu" in str(warning.warning))


class TestGenderNounDataHandler(unittest.TestCase):
    # most of the tests from this test class may break if the online data changes drastically;
    # this is not a problem, though, since they also check for the online data to stay unchanged in the relevant
    # aspects, so tracking down the source of the wrong negative and changing the tests accordingly shouldn't be much of
    # a problem.

    def test_type_checks(self):
        # test our type check helper function, which we will heavily rely on in this testing set, using the types
        # defined in src.gender_nouns:

        # base case 1: all values defined, all of the right type:
        self.assertTrue(check_type.is_instance({"parts_of_speech": "wuwu", "word": "fufu"},
                                               gn.OriginalDataGenderedVersionInfo))
        # base case 2: all values defined, some of the wrong type:
        self.assertFalse(check_type.is_instance({"parts_of_speech": ["wuwu"], "word": "fufu"},
                                                gn.OriginalDataGenderedVersionInfo))
        # base case 3: non-vital value missing:
        self.assertTrue(check_type.is_instance({"word": "fufu"},
                                               gn.OriginalDataGenderedVersionInfo))
        # base case 4: vital value missing:
        self.assertFalse(check_type.is_instance({"parts_of_speech": "wuwu"},
                                                gn.OriginalDataGenderedVersionInfo))
        # base case 5: non-specified value:
        self.assertFalse(check_type.is_instance({"parts_of_speech": "wuwu", "word": "fufu", "fufu": True},
                                                gn.OriginalDataGenderedVersionInfo))
        # iteration case 1: nestled TypedDict is valid:
        self.assertTrue(check_type.is_instance({"gender": "neutral", "gender_map": {"neutral": "wuwu"}},
                                               gn.GeneratedDataWord))
        # iteration case 2: nestled TypeDict is invalid:
        self.assertFalse(check_type.is_instance({"gender": "neutral", "gender_map": {"neutral": "wuwu", "foo": "bar"}},
                                                gn.GeneratedDataWord))

        # also check for Literal checking
        self.assertTrue(check_type.is_instance(1, typing_extensions.Literal[1, 2, 3]))
        self.assertFalse(check_type.is_instance(1, typing_extensions.Literal[2, 3]))

    def test_load_from_web(self):
        # we will not test the completeness of the dataset that this is based on, since we know it is incomplete, but
        # rather, whether the returned data appears to really be derived from the original, and have the right format.

        # make sure the type checks we wrote for TypedDict-typing actually work:

        # blueprint:
        json_original: gn.OriginalGenderNounData = json.loads(requests.get(
            "https://raw.githubusercontent.com/phseiff/gendered_words/master/gendered_words.json").text)
        # type check:
        self.assertTrue(check_type.is_instance(json_original, gn.OriginalGenderNounData))

        # the real thing:
        with warnings.catch_warnings(record=True) as w:
            json_generated = GenderNounDataHandler.load_from_web()
        # type check:
        self.assertTrue(check_type.is_instance(json_generated, gn.GeneratedGenderNounData))

        # make sure that all other values are there:
        for i in range(len(json_original)):
            word_data = json_original[i]
            if i < len(json_original) - 1 and json_original[i+1]["word"] == json_original[i]["word"]:
                # continue the loop if the word is part of the json data more than once, since only the last occurance
                # is counted:
                continue
            # make sure that words without a senseno are removed - unless we already had the same word in the data, in
            # which case they are not removed -> this test might lead to false negatives in the future:
            if "wordnet_senseno" not in word_data:
                if not (i > 0 and json_original[i - 1]["word"] == word_data["word"]
                        and "wordnet_senseno" in json_original[i - 1]):
                    self.assertNotIn(word_data["word"], json_generated)
                continue
            # make sure that words tagged as "other" are re-gendered as neutral:
            if word_data["gender"] == "o":
                self.assertEqual(json_generated[word_data["word"]]["gender"], "neutral")
            else:
                # and other words keep their gender:
                self.assertEqual(json_generated[word_data["word"]]["gender"][0], word_data["gender"])
            # if word is in the new json data, check further:
            if word_data["word"] in json_generated:
                # check that artificially added nouns that didn't come from wordnet aren't present anymore:
                self.assertIn("wordnet_senseno", word_data)
                # make sure we have an equally sized gender mapping:
                original_gender_map = word_data["gender_map"] if "gender_map" in word_data else {}
                generated_gender_map = json_generated[word_data["word"]]["gender_map"]
                self.assertEqual(len(generated_gender_map), len(original_gender_map))
                # make sure that both gender mappings are identical:
                for gender, mapped_word in generated_gender_map.items():
                    # make sure each linked gender is in the original json as well as the new:
                    self.assertIn(gender[0], original_gender_map)
                    # make sure their values are identical:
                    self.assertEqual(generated_gender_map[gender],
                                     original_gender_map[gender[0]][0]["word"].replace(" ", "_"))

        # make some simple exemplary tests to show this for some examples:

        # hermaphrodite got re-gendered as neutral:
        self.assertIn({"word": "hermaphrodite", "wordnet_senseno": "hermaphrodite.n.01", "gender": "o"},
                      json_original)
        self.assertEqual(json_generated["hermaphrodite"], {"gender": "neutral", "gender_map": {}})

        # heroine (as a word with a full gender map) was handled correctly:
        self.assertIn({"word": "heroine", "wordnet_senseno": "heroine.n.02", "gender": "f",
                       "gender_map": {"m": [{"parts_of_speech": "*", "word": "hero"}]}}, json_original)
        self.assertEqual(json_generated["heroine"], {"gender": "female", "gender_map": {"male": "hero"}})

        # reenactor (as a word with no gender map) is handled correctly (i.e. empty rather than no
        # gender map):
        self.assertIn({"word": "reenactor", "wordnet_senseno": "reenactor.n.01", "gender": "n"}, json_original)
        self.assertEqual(json_generated["reenactor"], {"gender": "neutral", "gender_map": {}})

        # women (as a word with no wordnet equivalent) is handles correctly (i.e. removed):
        self.assertIn({"word": "women", "gender": "f", "gender_map": {"m": [{"parts_of_speech": "*", "word": "men"}]}},
                      json_original)
        self.assertNotIn("women", json_generated)

        # great_grandson has its female version great_granddaughter listed with underscored rather than whitespace:
        self.assertIn({"word": "great_grandson", "wordnet_senseno": "great_grandson.n.01", "gender": "m",
                       "gender_map": {"f": [{"parts_of_speech": "*", "word": "great granddaughter"}]}},
                      json_original)
        self.assertEqual(json_generated["great_grandson"],
                         {"gender": "male", "gender_map": {"female": "great_granddaughter"}})

    def test_load_from_disk(self):
        # test for dict with warning:

        # save a file to disk to test it:
        inp = {"wuwu": {"warning": ["warning1", "warning2"]}}
        out = {"wuwu": {"warning": {"warning1", "warning2"}}}
        with open("test.gdn", "w") as test_file:
            test_file.write(json.dumps(inp))
        # test if it loads as expected:
        self.assertEqual(GenderNounDataHandler.load_from_disk("test.gdn"), out)

        # test for dict without warning:

        # save a file to disk to test it:
        inp = {"wuwu": {"fufu": "wawa"}}
        out = inp
        with open("test.gdn", "w") as test_file:
            test_file.write(json.dumps(inp))
        # test if it loads directly:
        self.assertEqual(GenderNounDataHandler.load_from_disk("test.gdn"), out)

        # test for a mixture:

        # save a file to disk to test it:
        inp = {"wuwu": {"warning": ["warning1", "warning2"]}, "wawa": {"fufu": "wawa"}}
        out = {"wuwu": {"warning": {"warning1", "warning2"}}, "wawa": {"fufu": "wawa"}}
        with open("test.gdn", "w") as test_file:
            test_file.write(json.dumps(inp))
        # test if it loads as expected:
        self.assertEqual(GenderNounDataHandler.load_from_disk("test.gdn"), out)

        # finally delete the file:
        os.remove("test.gdn")

    def test_save_to_disk(self):
        # test for dict with warning:

        # save a file to disk to test it:
        data_in_file = {"wuwu": {"warning": ["warning1", "warning2"]}}
        data_loaded = {"wuwu": {"warning": {"warning1", "warning2"}}}
        GenderNounDataHandler.save_to_disk(data_loaded, "test.gdn")
        with open("test.gdn", "r") as test_file:
            self.assertEqual(json.loads(test_file.read()), data_in_file)

        # test for dict without warning:

        # save a file to disk to test it:
        data_in_file = {"wuwu": {"fufu": "wawa"}}
        data_loaded = data_in_file
        GenderNounDataHandler.save_to_disk(data_loaded, "test.gdn")
        with open("test.gdn", "r") as test_file:
            self.assertEqual(json.loads(test_file.read()), data_in_file)

        # test for a mixture:

        # save a file to disk to test it:
        data_in_file = {"wuwu": {"warning": ["warning1", "warning2"]}, "wawa": {"fufu": "wawa"}}
        data_loaded = {"wuwu": {"warning": {"warning1", "warning2"}}, "wawa": {"fufu": "wawa"}}
        GenderNounDataHandler.save_to_disk(data_loaded, "test.gdn")
        with open("test.gdn", "r") as test_file:
            self.assertEqual(json.loads(test_file.read()), data_in_file)

        # finally delete the file:
        os.remove("test.gdn")

    def test_save_and_load(self):
        # test for dict with warning:

        # save a file to disk to test it:
        data = {"wuwu": {"warning": {"warning1", "warning2"}}}
        GenderNounDataHandler.save_to_disk(data, "test.gdn")
        self.assertEqual(data, GenderNounDataHandler.load_from_disk("test.gdn"))

        # test for dict without warning:

        # save a file to disk to test it:
        data = {"wuwu": {"fufu": "wawa"}}
        GenderNounDataHandler.save_to_disk(data, "test.gdn")
        self.assertEqual(data, GenderNounDataHandler.load_from_disk("test.gdn"))

        # test for words with underscores:
        data = {"fu_fu": {"wawa": "wuwu"}}
        GenderNounDataHandler.save_to_disk(data, "test.gdn")
        self.assertEqual(data, GenderNounDataHandler.load_from_disk("test.gdn"))

        # test for a mixture:

        # save a file to disk to test it:
        data = {"wuwu": {"warning": {"warning1", "warning2"}}, "wa_wa": {"fufu": "wawa"}}
        GenderNounDataHandler.save_to_disk(data, "test.gdn")
        self.assertEqual(data, GenderNounDataHandler.load_from_disk("test.gdn"))

        # finally delete the file:
        os.remove("test.gdn")

    def test_remove_words_that_are_not_nouns(self):
        # keep the dict as it is if all words are nouns:
        self.assertEqual(GenderNounDataHandler.remove_words_that_are_not_nouns(
            {"carpenter": {"gender": "neutral", "gender_map": {}}, "food": {"gender": "neutral", "gender_map": {}}}),
            {"carpenter": {"gender": "neutral", "gender_map": {}}, "food": {"gender": "neutral", "gender_map": {}}})

        # remove words that are not nouns:
        self.assertEqual(GenderNounDataHandler.remove_words_that_are_not_nouns(
            {"carpenter": {"gender": "neutral", "gender_map": {}}, "eat": {"gender": "neutral", "gender_map": {}}}),
            {"carpenter": {"gender": "neutral", "gender_map": {}}})

        # but keep those that are linked to nouns with their gender dict:
        self.assertEqual(GenderNounDataHandler.remove_words_that_are_not_nouns(
            {"carpenter": {"gender": "neutral", "gender_map": {}}, "eat": {"gender": "neutral",
                                                                           "gender_map": {"male": "carpenter"}}}),
            {"carpenter": {"gender": "neutral", "gender_map": {}}, "eat": {"gender": "neutral",
                                                                           "gender_map": {"male": "carpenter"}}})

    def test_make_sure_all_referenced_words_exist(self):
        # keep a dict that does not reference non-existing words as-is:
        self.assertEqual(GenderNounDataHandler.make_sure_all_referenced_words_exist(
            {"carpenter": {"gender": "neutral", "gender_map": {}}}),
            {"carpenter": {"gender": "neutral", "gender_map": {}}})

        # create non-existent, yet referenced words:
        self.assertEqual(GenderNounDataHandler.make_sure_all_referenced_words_exist(
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}}}),
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {"neutral": "carpenter"}}})

    def test_choose_better_word(self):
        # This is merely a helper function to determine which words of two words are more "precise", but we will test it
        #  anyways:

        # test if all pairs of ranking work:
        self.assertEqual(GenderNounDataHandler.choose_better_word("long_word_w_underscores", "police_woman"),
                         "police_woman")

        self.assertEqual(GenderNounDataHandler.choose_better_word("police_woman", "police_person"),
                         "police_person")
        self.assertEqual(GenderNounDataHandler.choose_better_word("police_man", "police_person"),
                         "police_person")

        self.assertEqual(GenderNounDataHandler.choose_better_word("police_person", "police_mother"),
                         "police_mother")
        self.assertEqual(GenderNounDataHandler.choose_better_word("police_person", "police_father"),
                         "police_father")

        self.assertEqual(GenderNounDataHandler.choose_better_word("police_parent", "police_mother"),
                         "police_parent")
        self.assertEqual(GenderNounDataHandler.choose_better_word("police_parent", "police_father"),
                         "police_parent")

        # test if words with height quality distance compare correctly as well:
        self.assertEqual(GenderNounDataHandler.choose_better_word("police_person", "police_parent"),
                         "police_parent")
        self.assertEqual(GenderNounDataHandler.choose_better_word("police_mother", "wuwuwu"),
                         "wuwuwu")

        # test if words of whom none fits into the hard-coded categories are decided alphabetically:
        self.assertEqual(GenderNounDataHandler.choose_better_word("wuwuwu", "aiaiaiaiaiaiai"),
                         "aiaiaiaiaiaiai")
        self.assertEqual(GenderNounDataHandler.choose_better_word("police_matron", "poioioice_matron"),
                         "poioioice_matron")

    def test_make_all_links_two_sided(self):
        # keep a dict where all links are two-sided (A <-> B C):
        self.assertEqual(GenderNounDataHandler.make_all_links_two_sided(
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {"neutral": "carpenter"}},
             "carpenter_man": {"gender": "male", "gender_map": {}}}),
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {"neutral": "carpenter"}},
             "carpenter_man": {"gender": "male", "gender_map": {}}})

        # change {A->B C} to {A<->B C}:
        self.assertEqual(GenderNounDataHandler.make_all_links_two_sided(
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {}},
             "carpenter_man": {"gender": "male", "gender_map": {}}}),
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {"neutral": "carpenter"}},
             "carpenter_man": {"gender": "male", "gender_map": {}}})

        # the result for the following tests:
        triangle_result = {
            "carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress", "male": "carpenter_man"}},
             "carpentress": {"gender": "female", "gender_map": {"male": "carpenter_man", "neutral": "carpenter"}},
             "carpenter_man": {"gender": "male", "gender_map": {"female": "carpentress", "neutral": "carpenter"}}}

        # Triangle tests for V-shaped triangles (A and B are somewhat linked and B and C, but not C and A):

        # change {A->B<-C} to {A<->B<->C<->A}:
        self.assertEqual(GenderNounDataHandler.make_all_links_two_sided(
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {}},
             "carpenter_man": {"gender": "male", "gender_map": {"female": "carpentress"}}}),
            triangle_result)

        # chance {A<-B->C} to {A<->B<->C<->A}:
        self.assertEqual(GenderNounDataHandler.make_all_links_two_sided(
            {"carpenter": {"gender": "neutral", "gender_map": {}},
             "carpentress": {"gender": "female", "gender_map": {"male": "carpenter_man", "neutral": "carpenter"}},
             "carpenter_man": {"gender": "male", "gender_map": {}}}),
            triangle_result)

        # change {A<->B<-C} to {A<->B<->C<->A}:
        self.assertEqual(GenderNounDataHandler.make_all_links_two_sided(
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {"neutral": "carpenter"}},
             "carpenter_man": {"gender": "male", "gender_map": {"female": "carpentress"}}}),
            triangle_result)

        # chance {A<->B->C} to {A<->B<->C<->A}:
        self.assertEqual(GenderNounDataHandler.make_all_links_two_sided(
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {"male": "carpenter_man", "neutral": "carpenter"}},
             "carpenter_man": {"gender": "male", "gender_map": {}}}),
            triangle_result)

        # chance {A<->B<->C} to {A<->B<->C<->A}:
        self.assertEqual(GenderNounDataHandler.make_all_links_two_sided(
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {"male": "carpenter_man", "neutral": "carpenter"}},
             "carpenter_man": {"gender": "male", "gender_map": {"female": "carpentress"}}}),
            triangle_result)

        # change {A->B->C} to {A<->B<->C<->A}:
        self.assertEqual(GenderNounDataHandler.make_all_links_two_sided(
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {"male": "carpenter_man"}},
             "carpenter_man": {"gender": "male", "gender_map": {}}}),
            triangle_result)

        # Now come the same tests again, but this time for triangles with three sides rather than V-shaped triangles:

        # change {A->B<-C->A} to {A<->B<->C<->A}:
        self.assertEqual(GenderNounDataHandler.make_all_links_two_sided(
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {}},
             "carpenter_man": {"gender": "male", "gender_map": {"female": "carpentress", "neutral": "carpenter"}}}),
            triangle_result)

        # change {A<->B<-C->A} to {A<->B<->C<->A}:
        self.assertEqual(GenderNounDataHandler.make_all_links_two_sided(
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {"neutral": "carpenter"}},
             "carpenter_man": {"gender": "male", "gender_map": {"female": "carpentress", "neutral": "carpenter"}}}),
            triangle_result)

        # chance {A<->B->C->A} to {A<->B<->C<->A}:
        self.assertEqual(GenderNounDataHandler.make_all_links_two_sided(
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {"male": "carpenter_man", "neutral": "carpenter"}},
             "carpenter_man": {"gender": "male", "gender_map": {"neutral": "carpenter"}}}),
            triangle_result)

        # chance {A<->B<->C->A} to {A<->B<->C<->A}:
        self.assertEqual(GenderNounDataHandler.make_all_links_two_sided(
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {"male": "carpenter_man", "neutral": "carpenter"}},
             "carpenter_man": {"gender": "male", "gender_map": {"female": "carpentress", "neutral": "carpenter"}}}),
            triangle_result)

        # change {A->B->C->A} to {A<->B<->C<->A}:
        self.assertEqual(GenderNounDataHandler.make_all_links_two_sided(
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {"male": "carpenter_man"}},
             "carpenter_man": {"gender": "male", "gender_map": {"neutral": "carpenter"}}}),
            triangle_result)

        # indirect gender information (given by links):
        self.assertEqual(GenderNounDataHandler.make_all_links_two_sided(
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {"male": "carpenter_man", "neutral": "carpenter"}},
             "carpenter_man": {"gender": "neutral", "gender_map": {}}}),

            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress", "male": "carpenter_man"}},
             "carpentress": {"gender": "female", "gender_map": {"male": "carpenter_man", "neutral": "carpenter"}},
             "carpenter_man": {"gender": "neutral", "gender_map": {"male": "carpenter_man", "female": "carpentress"}}})

        # direct gender information (given by `gender`-attrib) takes precedence over indirect gender information (given
        # by links):
        self.assertEqual(GenderNounDataHandler.make_all_links_two_sided(  # ↓ unusual gendering in links
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpenter"}},
             "carpentress": {"gender": "female", "gender_map": {"male": "carpenter_man", "neutral": "carpenter"}},
             "carpenter_man": {"gender": "male", "gender_map": {"neutral": "carpenter"}}}),

            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpenter", "male": "carpenter_man"}},
             "carpentress": {"gender": "female", "gender_map": {"male": "carpenter_man", "neutral": "carpenter"}},
             "carpenter_man": {"gender": "male", "gender_map": {"neutral": "carpenter", "female": "carpentress"}}}
        )  # does not affect newly build links, since explicit gender information takes precedence over it ↑

        # having to make decisions between two words based on `choose_better_word`:
        self.assertEqual(self.rmv_all_warn(GenderNounDataHandler.make_all_links_two_sided(
            {"bachelor": {"gender": "male", "gender_map": {}},
             "bachelor_girl": {"gender": "female", "gender_map": {"male": "bachelor"}},
             "bachelorette": {"gender": "female", "gender_map": {"male": "bachelor"}}})),

            {"bachelor": {"gender": "male", "gender_map": {"female": "bachelorette"}},
             "bachelor_girl": {"gender": "female", "gender_map": {"male": "bachelor"}},
             "bachelorette": {"gender": "female", "gender_map": {"male": "bachelor"}}})

    def test_create_extra_links_to_gender_ambiguous_words(self):
        # test for fine input:
        self.assertEqual(GenderNounDataHandler.create_extra_links_to_gender_ambiguous_words(
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {"neutral": "carpenter"}}}),

            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {"neutral": "carpenter"}}})

        # test for improvable input:
        self.assertEqual(GenderNounDataHandler.create_extra_links_to_gender_ambiguous_words(
            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {"male": "carpenter"}}}),

            {"carpenter": {"gender": "neutral", "gender_map": {"female": "carpentress"}},
             "carpentress": {"gender": "female", "gender_map": {"neutral": "carpenter", "male": "carpenter"}}})

    def rmv_warn(self, graph: gn.GeneratedGenderNounData, words: list) -> gn.GeneratedGenderNounData:
        # this function takes a list of words and removes the warning from all words on this list in the graph.
        # if any of these words don't have warnings, it raises an error.
        for word in words:
            self.assertIn("warning", graph[word])
            del graph[word]["warning"]
        return graph

    def rmv_all_warn(self, graph: gn.GeneratedGenderNounData) -> gn.GeneratedGenderNounData:
        # this function takes a gendered-noun-graph, removes all warnings from it and asserts that every word had one.
        self.rmv_warn(graph, list(graph.keys()))
        return graph

    def test_create_gendered_versions_for_words_that_end_with_gender_indicators(self):
        GNDH = GenderNounDataHandler
        # test for words that END with an indicator:
        self.assertEqual(self.rmv_all_warn(GNDH.create_gendered_versions_for_words_that_end_with_gender_indicators(
            {"brides_woman": {"gender": "female", "gender_map": {}}})),

            {"brides_woman": {"gender": "female", "gender_map": {"male": "brides_man", "neutral": "brides_person"}},
             "brides_man": {"gender": "male", "gender_map": {}},
             "brides_person": {"gender": "neutral", "gender_map": {}}})

        # test for words that START with an indicator, and a scenario where some of the potential words already exist:
        self.assertEqual(self.rmv_warn(GNDH.create_gendered_versions_for_words_that_end_with_gender_indicators(
            {"sister_sledge": {"gender": "female", "gender_map": {"neutral": "sib_sledge"}},
             "sib_sledge": {"gender": "neutral", "gender_map": {"female": "sister_sledge"}}}),
            ["sister_sledge", "brother_sledge"]),

            {"sister_sledge": {"gender": "female", "gender_map": {"male": "brother_sledge", "neutral": "sib_sledge"}},
             "brother_sledge": {"gender": "male", "gender_map": {}},
             "sib_sledge": {"gender": "neutral", "gender_map": {"female": "sister_sledge"}}})

        # test for a neutral word (doesn't create new versions):
        self.assertEqual(GNDH.create_gendered_versions_for_words_that_end_with_gender_indicators(
            {"brides_person": {"gender": "neutral", "gender_map": {}}}),
            {"brides_person": {"gender": "neutral", "gender_map": {}}})

        # test if words that allow multiple replacement strategies always take the top one:
        self.assertEqual(self.rmv_all_warn(GNDH.create_gendered_versions_for_words_that_end_with_gender_indicators(
            {"sister_woman": {"gender": "female", "gender_map": {}}})),

            {"sister_woman": {"gender": "female", "gender_map": {"male": "sister_man", "neutral": "sister_person"}},
             "sister_person": {"gender": "neutral", "gender_map": {}},
             "sister_man": {"gender": "male", "gender_map": {}}})

        # test if leading and/or trailing underscores in resulting words are trimmed:
        self.assertEqual(self.rmv_all_warn(GNDH.create_gendered_versions_for_words_that_end_with_gender_indicators(
            {"female_worker": {"gender": "female", "gender_map": {}}})),

            {"female_worker": {"gender": "female", "gender_map": {"male": "male_worker", "neutral": "worker"}},
             "worker": {"gender": "neutral", "gender_map": {}},
             "male_worker": {"gender": "male", "gender_map": {}}})

        # test if empty resulting words are properly refrained to use:
        self.assertEqual(self.rmv_all_warn(GNDH.create_gendered_versions_for_words_that_end_with_gender_indicators(
            {"male": {"gender": "male", "gender_map": {}}})),

            {"male": {"gender": "male", "gender_map": {"female": "female", "neutral": "person"}},
             "female": {"gender": "female", "gender_map": {}},
             "person": {"gender": "neutral", "gender_map": {}}})

    def test_find_words_with_no_neutral_form(self):
        GNDH = GenderNounDataHandler
        # test for word that is already neutral:
        self.assertEqual(GNDH.find_words_with_no_neutral_form(
            {"foo": {"gender": "neutral", "gender_map": {}}}),

            {"foo": {"gender": "neutral", "gender_map": {}}})

        # test for word that already has a neutral version:
        self.assertEqual(GNDH.find_words_with_no_neutral_form(
            {"foo": {"gender": "male", "gender_map": {"neutral": "bar"}}}),

            {"foo": {"gender": "male", "gender_map": {"neutral": "bar"}}})

        # test for word that is male:
        self.assertEqual(self.rmv_all_warn(GNDH.find_words_with_no_neutral_form(
            {"foo": {"gender": "male", "gender_map": {}}})),

            {"foo": {"gender": "male", "gender_map": {"neutral": "foo"}}})

        # ! extra: same case, but word already has a warning, so we can get full branch coverage because we can skip
        #  adding a new one:
        self.assertEqual(self.rmv_all_warn(GNDH.find_words_with_no_neutral_form(
            {"foo": {"gender": "male", "gender_map": {}, "warning": {"wuwu"}}})),

            {"foo": {"gender": "male", "gender_map": {"neutral": "foo"}}})

        # test for word that is female, but has a male version:
        self.assertEqual(self.rmv_all_warn(GNDH.find_words_with_no_neutral_form(
            {"foo": {"gender": "female", "gender_map": {"male": "bar"}}})),

            {"foo": {"gender": "female", "gender_map": {"male": "bar", "neutral": "bar"}}})

        # ! extra: same case, but word already has a warning, so we can get full branch coverage because we can skip
        #  adding a new one:
        self.assertEqual(self.rmv_all_warn(GNDH.find_words_with_no_neutral_form(
            {"foo": {"gender": "female", "gender_map": {"male": "bar"}, "warning": {"wuwu"}}})),

            {"foo": {"gender": "female", "gender_map": {"male": "bar", "neutral": "bar"}}})

        # test for word that is female, and has no male or neutral version:
        self.assertEqual(self.rmv_all_warn(GNDH.find_words_with_no_neutral_form(
            {"foo": {"gender": "female", "gender_map": {}}})),

            {"foo": {"gender": "female", "gender_map": {"neutral": "foo"}}})

        # ! extra: same case, but word already has a warning, so we can get full branch coverage because we can skip
        #  adding a new one:
        self.assertEqual(self.rmv_all_warn(GNDH.find_words_with_no_neutral_form(
            {"foo": {"gender": "female", "gender_map": {}, "warning": {"wuwu"}}})),

            {"foo": {"gender": "female", "gender_map": {"neutral": "foo"}}})

    def test_create_full_graph_from_web(self):
        GNDH = GenderNounDataHandler
        out = GNDH.create_full_graph_from_web()
        inp = copy.deepcopy(out)

        # test if the result has the right format:
        self.assertTrue(check_type.is_instance(out, gn.GeneratedGenderNounData))

        # test if every resulting word has a neutral form or is neutral:
        for word_data in out.values():
            self.assertTrue(word_data["gender"] == "neutral" or "neutral" in word_data["gender_map"])

        # test if calling the relevant methods anything (to be sure we already did all we can)
        # (this does not include `remove_words_that_are_not_nouns`, though, since this is destined to fail due to
        # `create_gendered_versions_for_words_that_end_with_gender_indicators`):

        # self.assertEqual(out, GNDH.make_all_links_two_sided(inp))
        # ToDo: ^ this is commented out since it is not called one last time in the pipeline; maybe just do so for the
        #  sake of completeness? If the change in NounGenderingGuessingsWarning-raising proposed in
        #  GenderedNoun.__init__ is implemented, we should definitely change this and un-comment this test.
        self.assertEqual(out, GNDH.make_sure_all_referenced_words_exist(inp))
        self.assertEqual(out, GNDH.create_extra_links_to_gender_ambiguous_words(inp))
        # self.assertEqual(out, GNDH.create_gendered_versions_for_words_that_end_with_gender_indicators(inp))
        # ^ this is also impossible to test, since running multiple tests ruins words that
        # ToDo: Maybe do something about this as well? There is no reason for this at the moment, though, and it should
        #  be preevaluated if it is even possible and/or desirable
        self.assertEqual(out, GNDH.find_words_with_no_neutral_form(inp))


class TestGenderedNoun(unittest.TestCase):

    def test__init__(self):
        # (after every test, we do one rendering of the word to be sure that the rendering itself raises no warning, and
        # the word string is correctly attached to the object in any case).

        # test for a word with no warnings attached, that is a hyponym
        with warnings.catch_warnings(record=True) as w:
            n = gn.GenderedNoun("newsreader")
            self.assertEqual(w, [])
        with warnings.catch_warnings(record=True) as w:
            n.render_noun("neutral")
            self.assertEqual(w, [])

        # test for word which isn't a word, actually:
        with self.assertWarns(ws.NotAWordWarning):
            n = gn.GenderedNoun("wuwuwu")
        with warnings.catch_warnings(record=True) as w:
            n.render_noun("neutral")
            self.assertEqual(w, [])

        # test for word that is a word, but isn't a noun:
        with self.assertWarns(ws.NotANounWarning):
            n = gn.GenderedNoun("eat")
        with warnings.catch_warnings(record=True) as w:
            n.render_noun("neutral")
            self.assertEqual(w, [])

        # test for word that is a word, but isn't a hyponym:
        with self.assertWarns(ws.NotAPersonNounWarning):
            n = gn.GenderedNoun("chair")
        with warnings.catch_warnings(record=True) as w:
            n.render_noun("neutral")
            self.assertEqual(w, [])

        # test for word that isn't a hyponym as defined by wordnet, but is still part of our dataset
        #  (this naturally raises a NounGenderingGuessingsWarning, but doesn't raise a NotAPersonNounWarning):
        with self.assertWarns(ws.NounGenderingGuessingsWarning):
            n = gn.GenderedNoun("wonder_person")
        with warnings.catch_warnings(record=True) as w:
            n.render_noun("neutral")
            self.assertEqual(w, [])

        # test for a hyponym with warnings attached:
        with self.assertWarns(ws.NounGenderingGuessingsWarning):
            n = gn.GenderedNoun("brother")
        with warnings.catch_warnings(record=True) as w:
            n.render_noun("neutral")
            self.assertEqual(w, [])

        # make sure the word is saved in the right uppercase/lowercase form, but warnings are risen based on its
        # lowercase form:
        with warnings.catch_warnings(record=True) as w:
            n = gn.GenderedNoun("Bigot")
            self.assertEqual(w, [])
        self.assertEqual(n.word, "Bigot")

    def test_render_noun(self):
        with warnings.catch_warnings(record=True) as w:
            # every test case refers to a specific type of lookup-scenario; and every test case has ana additional test
            # case for the scenario that the resulting word contains underscores attached, as well as one for the
            # scenario that the given word is uppercase:

            # test for a non-existent version of a neutral word (careerist is neutral and has no male version, so it
            # should instead give us itself):
            self.assertEqual(set(gn.GENDER_DICT["careerist"]["gender_map"].keys()), set())
            self.assertEqual(gn.GENDER_DICT["careerist"]["gender"], "neutral")
            self.assertEqual(gn.GenderedNoun("careerist").render_noun("male"), "careerist")
            # correctly replace underscores with whitespace in this scenario:
            self.assertEqual(gn.GenderedNoun("big_spender").render_noun("male"), "big spender")
            # uppercase:
            self.assertEqual(gn.GenderedNoun("Careerist").render_noun("male"), "Careerist")

            # test for non-existent version of word with neutral version ("townee" is male, has a neutral version, but
            # no female version, so if we request the female version of it, we should get its neutral version):
            self.assertEqual(set(gn.GENDER_DICT["townee"]["gender_map"].keys()), {"neutral"})
            self.assertEqual(gn.GENDER_DICT["townee"]["gender"], "male")
            self.assertEqual(gn.GenderedNoun("townee").render_noun("female"), "townee")
            # correctly replace underscores with whitespace in this scenario:
            self.assertEqual(gn.GenderedNoun("closet_queen").render_noun("female"), "closet monarch")
            # uppercase:
            self.assertEqual(gn.GenderedNoun("Townee").render_noun("female"), "Townee")

            # test for word that is already the right gender (tests for both neutral as well as non-neutral gender):
            self.assertEqual(gn.GENDER_DICT["townsman"]["gender"], "male")
            self.assertEqual(gn.GenderedNoun("townsman").render_noun("male"), "townsman")
            # correctly replace underscores with whitespace in this scenario:
            self.assertEqual(gn.GenderedNoun("sea_scout").render_noun("female"), "sea scout")
            # uppercase:
            self.assertEqual(gn.GenderedNoun("Townsman").render_noun("male"), "Townsman")

            self.assertEqual(gn.GENDER_DICT["tourist"]["gender"], "neutral")
            self.assertEqual(gn.GenderedNoun("tourist").render_noun("neutral"), "tourist")
            # correctly replace underscores with whitespace in this scenario:
            self.assertEqual(gn.GenderedNoun("second_cousin").render_noun("female"), "second cousin")
            # uppercase:
            self.assertEqual(gn.GenderedNoun("Tourist").render_noun("neutral"), "Tourist")

            # return correctly gendered version for words from the gender_map, if word is not the gender it requests and
            #  has the gender in its gender map (test for requesting a non-neutral as well as the neutral version):
            self.assertEqual(set(gn.GENDER_DICT["big_brother"]["gender_map"].keys()), {"male", "female"})
            self.assertEqual(gn.GENDER_DICT["big_brother"]["gender"], "neutral")
            self.assertEqual(gn.GenderedNoun("big_brother").render_noun("female"), "big sister")
            # correctly replace underscores with whitespace in this scenario:
            self.assertEqual(gn.GenderedNoun("ring_girl").render_noun("male"), "ring boy")
            # uppercase:
            self.assertEqual(gn.GenderedNoun("Big_brother").render_noun("female"), "Big sister")

            self.assertEqual(set(gn.GENDER_DICT["black_man"]["gender_map"].keys()), {"female", "neutral"})
            self.assertEqual(gn.GENDER_DICT["black_man"]["gender"], "male")
            self.assertEqual(gn.GenderedNoun("black_man").render_noun("neutral"), "black person")
            # correctly replace underscores with whitespace in this scenario:
            self.assertEqual(gn.GenderedNoun("ring_girl").render_noun("neutral"), "ring bean")
            # uppercase:
            self.assertEqual(gn.GenderedNoun("Black_man").render_noun("neutral"), "Black person")
