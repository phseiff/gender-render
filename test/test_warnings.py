
import unittest
import threading

import src.warnings as gr_warnings


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
        gr_warnings.WarningManager.warning_settings_by_thread_id = set()

    def test_set_warning_settings(self):
        # tests if set_warning_settings actually adds a new value with the right key.
        test_warning = gr_warnings.NotAWordWarning
        gr_warnings.WarningManager.set_warning_settings({test_warning})
        self.assertIn(threading.get_ident(), gr_warnings.WarningManager.warning_settings_by_thread_id)
        self.assertEqual(gr_warnings.WarningManager.warning_settings_by_thread_id[threading.get_ident()],
                         {test_warning})

        # make sure that setting new values under a different thread does not overwrite value:
        # ToDo

    def test_raise_warning(self):
        # test if raising a warning
        pass
