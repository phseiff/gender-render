"""Custom error types, as defined by the gender*render specification."""

# SyntaxError:


class SyntaxError(SyntaxError):
    """Raised when an error occurs whilst parsing a gender*render template."""
    pass


class SyntaxPostprocessingError(SyntaxError):
    """A more specific type of SyntaxError that is raised when errors occur in template parsing outside of the rules set
    by the finite state machine."""
    pass

# InvalidPDErrors:


class InvalidPDError(Exception):
    """Raised when a piece of invalid pronoun data is given to a function that expects valid pronoun data."""
    pass

# IdResolutionErrors:


class IdResolutionError(Exception):
    """Raised when id resolution fails due to template and pronoun data not matching."""
    pass

# information in the pronoun data does not match requirements:


class MissingInformationError(Exception):
    """Raised when a piece of individual pronoun data does not contain an attribute requested by the renderer."""
    pass


class DoubledInformationError(Exception):
    """Raised when a piece of individual pronoun data contains two different properties for the same attribute."""
    pass


class InvalidInformationError(Exception):
    """Raised when an attribute in a piece of individual pronoun data has an invalid value assigned.
    This error is only used for attributes that only allow a fixed set of values."""
    pass
