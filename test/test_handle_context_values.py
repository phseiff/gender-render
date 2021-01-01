
import unittest
from test import check_type
from typing import List, Dict, Set
import warnings

import src.warnings as ws
import src.errors as err
import src.gender_nouns as gn
from src.handle_context_values import ContextValues


class TestContextValues(unittest.TestCase):

    def test_var_properties(self):
        # test if this value really is a list of lists of strings, as described by the documentation.
        self.assertTrue(check_type.is_instance(ContextValues.properties, List[List[str]]))

        # make sure no element happens to be in two lists:
        full_list = [prop for l in ContextValues.properties for prop in l]
        full_list_without_doubles = set(full_list)
        self.assertEqual(len(full_list), len(full_list_without_doubles))

    def test_var_properties_to_canonical_property(self):
        # this tests if the initialization of this property done by `initialize()` is done correctly.

        # test if attribute is not empty:
        self.assertNotEqual(ContextValues.properties_to_canonical_property, dict())

        # first, a type check:
        self.assertTrue(check_type.is_instance(ContextValues.properties_to_canonical_property, Dict[str, str]))

        # test if the length aligns with length of `properties`:
        all_properties = [prop for l in ContextValues.properties for prop in l]
        self.assertEqual(len(ContextValues.properties_to_canonical_property), len(all_properties))

        # test if the key values align with the values in `properties`:
        key_values = list(ContextValues.properties_to_canonical_property.keys())
        key_values.sort()
        all_properties.sort()
        self.assertEqual(all_properties, key_values)

        # second, let's check if every value pair corresponds to a value pair in `properties`:
        for not_canonical, canonical in ContextValues.properties_to_canonical_property.items():
            found = False
            for c, *non_c in ContextValues.properties:
                if c == canonical:
                    found = True
                    break
            self.assertTrue(found)
            self.assertTrue(not_canonical in non_c + [c])

        # make sure the values of `properties_to_canonical_property` are equal to the leading elements of the lists in
        #  `properties`:
        canonicals_according_to_properties_list = set(canonical for canonical, *_ in ContextValues.properties)
        canonicals_according_to_properties_dict = set(ContextValues.properties_to_canonical_property.values())
        self.assertEqual(canonicals_according_to_properties_list, canonicals_according_to_properties_dict)

    def test_var_canonical_properties_that_map_directly_between_template_and_pronoun_data(self):
        # type check
        self.assertTrue(check_type.is_instance(
            ContextValues.canonical_properties_that_directly_map_between_template_and_pronoun_data, List[str]))

        # test if these canonicals are a subset of the canonicals in `properties`:
        canonicals_according_to_properties_list = set(canonical for canonical, *_ in ContextValues.properties)
        canonical_subset = set(ContextValues.canonical_properties_that_directly_map_between_template_and_pronoun_data)
        self.assertTrue(canonical_subset.issubset(canonicals_according_to_properties_list))
        # and also test if they are in accordance to the canonicals defined by `properties_to_canonical_properties`:
        canonicals_according_to_properties_dict = set(ContextValues.properties_to_canonical_property.values())
        self.assertTrue(canonical_subset.issubset(canonicals_according_to_properties_dict))

        # test if the canonicals that supposedly map directly between template and pronoun dict are all canonicals
        #  but gender-addressing and gender-nouns:
        self.assertEqual(set(ContextValues.canonical_properties_that_directly_map_between_template_and_pronoun_data),
                         canonicals_according_to_properties_dict - {"gender-addressing", "gender-nouns"})

    def test_var_properties_that_allow_only_some_values_in_pd(self):
        # type check:
        self.assertTrue(check_type.is_instance(
            ContextValues.properties_that_allow_only_some_values_in_pd, Dict[str, Set]))

        # test if keys are a subset of keys properties:
        canonicals_according_to_properties_list = set(canonical for canonical, *_ in ContextValues.properties)
        canonicals_according_to_properties_dict = set(ContextValues.properties_to_canonical_property.values())
        keys = set(ContextValues.properties_that_allow_only_some_values_in_pd.keys())
        self.assertTrue(keys.issubset(canonicals_according_to_properties_list))
        self.assertTrue(keys.issubset(canonicals_according_to_properties_dict))

    def test_var_default_values(self):
        # type check:
        self.assertTrue(check_type.is_instance(ContextValues.default_values, Dict[str, str]))

        # test if keys are a subset of keys properties
        #  - copied from `test_var_properties_that_allow_only_some_values_in_pd`:
        canonicals_according_to_properties_list = set(canonical for canonical, *_ in ContextValues.properties)
        canonicals_according_to_properties_dict = set(ContextValues.properties_to_canonical_property.values())
        keys = set(ContextValues.properties_that_allow_only_some_values_in_pd.keys())
        self.assertTrue(keys.issubset(canonicals_according_to_properties_list))
        self.assertTrue(keys.issubset(canonicals_according_to_properties_dict))

    def test_get_value(self):
        with warnings.catch_warnings(record=True) as w:
            # value is defined, can be returned:
            self.assertEqual(ContextValues.get_value({"foo": {"subject": "they"}}, "foo", "subject"), "they")
            # also works between canonical custom properties:
            self.assertEqual(ContextValues.get_value({"foo": {"<bar>": "they"}}, "foo", "<bar>"), "they")

            # does not raise a warning:
            self.assertEqual(w, [])

            # value is not defined, but has a standard value:
            self.assertEqual(ContextValues.get_value({"foo": {}, "bar": {}}, "foo", "gender-addressing"), "t")
            self.assertEqual(ContextValues.get_value({"foo": {}, "bar": {}}, "foo", "gender-nouns"), "neutral")
            self.assertEqual(len(w), 2)
            for prop, default_value in ContextValues.default_values.items():
                self.assertEqual(ContextValues.get_value({"foo": {}, "bar": {}}, "foo", prop), default_value)

            # raises DefaultValueUsedWarning warnings (identical warnings are not listed in w):
            self.assertEqual(len(w), len(ContextValues.default_values))
            for raised_warning in w:
                self.assertTrue(issubclass(raised_warning.category, ws.DefaultValueUsedWarning))

        # error if value has no default value and is not defined:
        self.assertRaises(err.MissingInformationError, lambda: ContextValues.get_value({"foo": {}}, "foo", "subject"))

    def test_value_is_allowed(self):
        # test for explicitly allowed values for properties with limited allowed values:
        self.assertTrue(ContextValues.value_is_allowed("gender-nouns", "male"))
        self.assertTrue(ContextValues.value_is_allowed("gender-nouns", "female"))
        self.assertTrue(ContextValues.value_is_allowed("gender-addressing", "t"))
        self.assertTrue(ContextValues.value_is_allowed("gender-addressing", "true"))
        for property_name, allowed_values in ContextValues.properties_that_allow_only_some_values_in_pd.items():
            for allowed_value in allowed_values:
                self.assertTrue(ContextValues.value_is_allowed(property_name, allowed_value))

        # test for explicitly disallowed values for properties with limited allowed values:
        self.assertFalse(ContextValues.value_is_allowed("gender-nouns", "waaaawawawawa"))
        self.assertFalse(ContextValues.value_is_allowed("gender-addressing", "wuwuwu"))

        # test for custom properties:
        self.assertTrue(ContextValues.value_is_allowed("wuwu", "wawa"))
        self.assertTrue(ContextValues.value_is_allowed("<wuwu>", "wawa"))
        self.assertTrue(ContextValues.value_is_allowed("_wuwu", "wawa"))

        # test for values without restrictions:
        self.assertTrue(ContextValues.value_is_allowed("subject", "they"))
        self.assertTrue(ContextValues.value_is_allowed("subject", "wawa"))
        self.assertTrue(ContextValues.value_is_allowed("they", "they"))
        self.assertTrue(ContextValues.value_is_allowed("they", "wawa"))

    def test_initialize(self):
        # there are almost no tests for this one, since all it does is initialize `properties_to_canonical_property`,
        #  which was already tested (see above).
        # We will test, however, if the result after calling `initialize()` for a second time equals the original value.
        original_value = ContextValues.properties_to_canonical_property
        ContextValues.initialize()
        self.assertEqual(original_value, ContextValues.properties_to_canonical_property)
        # fix an issue we have with code coverage due to `initialize` not taking any arguments:
        initialize_fkt = ContextValues.initialize
        ContextValues.initialize = initialize_fkt

    def test_property_maps_directly_between_template_and_pronoun_data(self):
        # return True for all non-custom properties that map directly:
        self.assertTrue(ContextValues.property_maps_directly_between_template_and_pronoun_data("subject"))
        self.assertTrue(ContextValues.property_maps_directly_between_template_and_pronoun_data("address"))

        # return True for canonical custom properties:
        self.assertTrue(ContextValues.property_maps_directly_between_template_and_pronoun_data("<wuwu>"))
        self.assertTrue(ContextValues.property_maps_directly_between_template_and_pronoun_data("<fufufu>"))

        # return False for properties that do not map:
        self.assertFalse(ContextValues.property_maps_directly_between_template_and_pronoun_data("gender-addressing"))
        self.assertFalse(ContextValues.property_maps_directly_between_template_and_pronoun_data("gender-nouns"))

        # return False for unknown properties (for example nouns):
        self.assertFalse(ContextValues.property_maps_directly_between_template_and_pronoun_data("wuwuwu"))
        self.assertFalse(ContextValues.property_maps_directly_between_template_and_pronoun_data("carpenter"))

    def test_is_a_custom_value(self):
        # return False for canonical non-custom properties:
        self.assertFalse(ContextValues.is_a_custom_value("subject"))
        self.assertFalse(ContextValues.is_a_custom_value("gender-addressing"))

        # return False for non-canonical non-custom properties:
        self.assertFalse(ContextValues.is_a_custom_value("they"))
        self.assertFalse(ContextValues.is_a_custom_value("them"))

        # return True for custom properties:
        self.assertTrue(ContextValues.is_a_custom_value("wuwu"))
        self.assertTrue(ContextValues.is_a_custom_value("_wuwu"))
        self.assertTrue(ContextValues.is_a_custom_value("<wuwu>"))
        self.assertTrue(ContextValues.is_a_custom_value("carpenter"))  # <- also works for gendered nouns

    def test_uses_special_custom_value_syntax(self):
        # return False for known as well as unknown values (also, nouns) with non-custom-value-syntax:
        self.assertFalse(ContextValues.uses_special_custom_value_syntax("subject"))
        self.assertFalse(ContextValues.uses_special_custom_value_syntax("they"))
        self.assertFalse(ContextValues.uses_special_custom_value_syntax("wuwu"))
        self.assertFalse(ContextValues.uses_special_custom_value_syntax("carpenter"))

        # return True for values with custom-value-syntax:
        self.assertTrue(ContextValues.uses_special_custom_value_syntax("_wuwuwu"))
        self.assertTrue(ContextValues.uses_special_custom_value_syntax("<wuwuwu>"))

    def test_is_a_custom_property_defined_in_a_tag(self):
        # return False for known as well as unknown values (also, nouns) with non-custom-value-syntax:
        self.assertFalse(ContextValues.uses_special_custom_value_syntax("subject"))
        self.assertFalse(ContextValues.uses_special_custom_value_syntax("they"))
        self.assertFalse(ContextValues.uses_special_custom_value_syntax("wuwu"))
        self.assertFalse(ContextValues.uses_special_custom_value_syntax("carpenter"))

        # return True for values with custom-value-syntax:
        self.assertTrue(ContextValues.uses_special_custom_value_syntax("<wuwuwu>"))

    def test_get_canonical_of_custom_property(self):
        # custom properties not named after nouns:
        self.assertEqual(ContextValues.get_canonical_of_custom_property("wuwuwu"), "<wuwuwu>")
        self.assertEqual(ContextValues.get_canonical_of_custom_property("_wuwuwu"), "<wuwuwu>")
        self.assertEqual(ContextValues.get_canonical_of_custom_property("<wuwuwu>"), "<wuwuwu>")

        # custom properties named after nouns:
        self.assertEqual(ContextValues.get_canonical_of_custom_property("carpenter"), "<carpenter>")
        self.assertEqual(ContextValues.get_canonical_of_custom_property("_carpenter"), "<carpenter>")
        self.assertEqual(ContextValues.get_canonical_of_custom_property("<carpenter>"), "<carpenter>")

    def test_get_canonical(self):
        # -- for is_from_tag=True:

        # non-canonical properties:
        self.assertEqual(ContextValues.get_canonical("they"), "subject")
        self.assertEqual(ContextValues.get_canonical("them"), "object")
        # canonical properties:
        self.assertEqual(ContextValues.get_canonical("subject"), "subject")
        self.assertEqual(ContextValues.get_canonical("gender-addressing"), "gender-addressing")

        # for a noun:
        with warnings.catch_warnings(record=True):
            self.assertEqual(ContextValues.get_canonical("wuwu"), gn.GenderedNoun("wuwu"))
            self.assertEqual(ContextValues.get_canonical("_wuwu"), gn.GenderedNoun("_wuwu"))
            self.assertEqual(ContextValues.get_canonical("carpenter"), gn.GenderedNoun("carpenter"))
            self.assertEqual(ContextValues.get_canonical("_carpenter"), gn.GenderedNoun("_carpenter"))

        # for a custom property with special syntax:
        self.assertEqual(ContextValues.get_canonical("<wuwu>"), "<wuwu>")
        self.assertEqual(ContextValues.get_canonical("<carpenter>"), "<carpenter>")

        # -- for is_from_tag=False:

        # non-canonical properties:
        self.assertEqual(ContextValues.get_canonical("they", is_from_tag=False), "subject")
        self.assertEqual(ContextValues.get_canonical("them", is_from_tag=False), "object")
        # canonical properties:
        self.assertEqual(ContextValues.get_canonical("subject", is_from_tag=False), "subject")
        self.assertEqual(ContextValues.get_canonical("gender-addressing", is_from_tag=False), "gender-addressing")

        # for a custom property with special syntax:
        self.assertEqual(ContextValues.get_canonical("wuwu", is_from_tag=False), "<wuwu>")
        self.assertEqual(ContextValues.get_canonical("_wuwu", is_from_tag=False), "<wuwu>")
        self.assertEqual(ContextValues.get_canonical("<wuwu>", is_from_tag=False), "<wuwu>")
        self.assertEqual(ContextValues.get_canonical("carpenter", is_from_tag=False), "<carpenter>")
        self.assertEqual(ContextValues.get_canonical("_carpenter", is_from_tag=False), "<carpenter>")
        self.assertEqual(ContextValues.get_canonical("<carpenter>", is_from_tag=False), "<carpenter>")
