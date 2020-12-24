
import unittest
import threading
import warnings

import src.warnings as gr_warnings

# Some exemplary warnings for testing:


test_warning = gr_warnings.NotAWordWarning
test_warning2 = gr_warnings.NotAPersonNounWarning
test_warning_text = "warn warn warn"

# testing classes:


class TestGlobals(unittest.TestCase):
    """Tests the global warning collections."""

    def test_ENABLE_ALL_WARNINGS(self):
        # make sure len(ENABLE_ALL_WARNINGS) > 1 und alle Elements von ENABLE_ALL_WARNINGS sind Kinder von GRWarning.
        self.assertTrue(len(gr_warnings.ENABLE_ALL_WARNINGS) > 1)
        all_are_children_of_gr_warning = True
        for w in gr_warnings.ENABLE_ALL_WARNINGS:
            if not issubclass(w, gr_warnings.GRWarning):
                all_are_children_of_gr_warning = False
        self.assertTrue(all_are_children_of_gr_warning)

    def test_ENABLE_ALL_LOGGING(self):
        # make sure len(ENABLE_LOGGING) > 1 und alle Elemente von ENABLE_ALL_LOGGING sind Kinder von GRLogging.
        self.assertTrue(len(gr_warnings.ENABLE_ALL_LOGGING) > 1)
        all_are_children_of_gr_logging = True
        for w in gr_warnings.ENABLE_ALL_LOGGING:
            if not issubclass(w, gr_warnings.GRLogging):
                all_are_children_of_gr_logging = False
        self.assertTrue(all_are_children_of_gr_logging)

    def test_ENABLE_DEFAULT_WARNINGS(self):
        # make sure test_ENABLE_DEFAULT_WARNINGS has the right value.
        self.assertEqual(gr_warnings.ENABLE_ALL_WARNINGS, gr_warnings.ENABLE_DEFAULT_WARNINGS)


class TestWarningManager(unittest.TestCase):
    """Tests the test manager, especially how it performs in multi-threaded environments."""

    def setUp(self):
        """Returns the thread-id-to-warning-mapping to its initial state."""
        gr_warnings.WarningManager.warning_settings_by_thread_id = dict()

    def test_set_warning_settings(self):
        # tests if set_warning_settings actually adds a new value with the right key.
        gr_warnings.WarningManager.set_warning_settings({test_warning})
        self.assertIn(threading.get_ident(), gr_warnings.WarningManager.warning_settings_by_thread_id)
        self.assertEqual(gr_warnings.WarningManager.warning_settings_by_thread_id[threading.get_ident()],
                         {test_warning})

        # make sure setting new values under a different thread does not overwrite value:
        def set_different_value_in_different_thread():
            gr_warnings.WarningManager.set_warning_settings({test_warning2})
        threading.Thread(target=set_different_value_in_different_thread).start()
        self.assertEqual(gr_warnings.WarningManager.warning_settings_by_thread_id[threading.get_ident()],
                         {test_warning})

    def check_if_warning_is_raised(self, text, warning):
        # tests if raise_warning actually raises a warning if it is given one:
        with warnings.catch_warnings(record=True) as w:
            gr_warnings.WarningManager.raise_warning(text, warning)
            self.assertTrue(
                len(w) == 1
                and issubclass(w[-1].category, test_warning)
                and test_warning_text == str(w[-1].message)
            )

    def check_if_warning_is_not_raised(self, text, warning):
        # tests if raise_warning does not raise a warning:
        with warnings.catch_warnings(record=True) as w:
            gr_warnings.WarningManager.raise_warning(text, warning)
            self.assertEqual(len(w), 0)

    def test_raise_warning(self):
        # test if raising warnings before defining warning settings actually works, and that the values that are raised
        #  aligns with the warnings in the default settings:
        with warnings.catch_warnings(record=True) as w:
            for warning in gr_warnings.ENABLE_ALL_WARNINGS:
                gr_warnings.WarningManager.raise_warning(test_warning_text, warning)
        self.assertEqual(len(w), len(gr_warnings.ENABLE_DEFAULT_WARNINGS))

        # test if raising a warning works for enabled warnings and doesn't work for disabled warnings:
        gr_warnings.WarningManager.set_warning_settings({test_warning})
        self.check_if_warning_is_raised(test_warning_text, test_warning)
        self.check_if_warning_is_not_raised(test_warning_text, test_warning2)

        # test if raising warnings in a different (new) thread still works as expected:
        def check_if_different_thread_still_behaves_according_to_the_default_values():
            self.check_if_warning_is_raised(test_warning_text, test_warning2)
        threading.Thread(target=check_if_different_thread_still_behaves_according_to_the_default_values).start()

        # test if changing warning settings in a thread and raising a warning in it does not affect (older) threads:
        def check_if_different_thread_does_not_overwrite_ours():
            gr_warnings.WarningManager.set_warning_settings({test_warning2})
            with warnings.catch_warnings(record=True) as w:
                gr_warnings.WarningManager.raise_warning(test_warning_text, test_warning2)
        threading.Thread(target=check_if_different_thread_does_not_overwrite_ours).start()
        self.check_if_warning_is_raised(test_warning_text, test_warning)

        # test if passing None as a value for the text prints the warnings description as text:
        class TestWarning3(gr_warnings.GRWarning):
            """test test test"""
            pass
        gr_warnings.WarningManager.set_warning_settings({TestWarning3})
        with warnings.catch_warnings(record=True) as w:
            gr_warnings.WarningManager.raise_warning(None, TestWarning3)
            self.assertTrue(len(w) == 1 and str(w[-1].message) == TestWarning3.__doc__)
