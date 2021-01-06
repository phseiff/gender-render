"""
The interface to gender*render pronoun data representations presented to the user.
"""

from typing import Union

from . import warnings
from .parse_pronoun_data import IDPD, GRPD, GRPDParser


# a class representation for pronoun data, as defined by the spec:


class PronounData:
    """A representation for pronoun data as defined by the specification."""
    def __init__(self, pronoun_data: Union[str, GRPD, IDPD, "PronounData"], takes_file_path=False,
                 warning_settings: warnings.WarningSettingType = warnings.ENABLE_DEFAULT_WARNINGS):

        warnings.WarningManager.set_warning_settings(warning_settings)

        # read from a file into a string, if necessary:
        if takes_file_path:
            with open(pronoun_data, "r") as pd_file:
                pd = pd_file.read()
        else:
            pd = pronoun_data
        # take pronoun data from PronounData object, string or dict:
        if type(pd) is PronounData:
            self.grpd = pd.get_pd()
        else:
            if type(pd) is str:
                pd_as_dict = GRPDParser.pd_string_to_dict(pd)
            else:
                pd_as_dict = pd

            # raise warning if the wrong file format was chosen:
            if takes_file_path:
                file_format = pronoun_data.split(".")[-1].lower()
                content_format = "grpd" if GRPDParser.type_of_pd(pd_as_dict) is GRPD else "idpd"
                if file_format != content_format:
                    warnings.WarningManager.raise_warning(
                        "The file format ." + file_format + " contains " + content_format + " data. "
                        + "This kind of data should e contained in ." + content_format + " files instead.",
                        warnings.UnexpectedFileFormatWarning
                    )

            self.grpd = GRPDParser.full_parsing_pipeline(pd_as_dict)

    def get_pd(self):
        """Returns the PronounData representations actual pronoun data structure."""
        return self.grpd
