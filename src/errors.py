"""Custom error types, as defined by the gender*render specification.

Please note that, since gender\\*render is intended to be used on human input rather than machine-generated input
(templates are written by people, after all), the error hierarchy might change irregularly, and should not
necessarily be relied on."""

# Invalid Template:


class SyntaxError(SyntaxError):
    """Raised when an error occurs whilst parsing a gender*render template."""
    pass


class SyntaxPostprocessingError(SyntaxError):
    """A more specific type of SyntaxError that is raised when errors occur in template parsing outside of the rules set
    by the finite state machine."""
    # ToDo: Maybe actually include this in the spec? Might be contra-productive for languages without an error
    #  hierarchy.
    pass


class InvalidCapitalizationError(SyntaxPostprocessingError):
    """Raised when the capitalization of a context value or the capitalization value of a tag are invalid."""
    pass


# Invalid Pronoun Data:


class InvalidPDError(Exception):
    """Raised when a piece of invalid pronoun data is given to a function that expects valid pronoun data."""
    pass


class DoubledInformationError(InvalidPDError):
    """Raised when a piece of individual pronoun data contains two different properties for the same attribute."""
    pass


class InvalidInformationError(InvalidPDError):
    """Raised when an attribute in a piece of individual pronoun data has an invalid value assigned.
    This error is only used for attributes that only allow a fixed set of values."""
    pass

# Errors during rendering:


class RenderingError(Exception):
    """Raised when something goes wrong during the rendering process. This exception is never raised directly,
    but can be caught to catch any type of error that arises during rendering due to the exception hierarchy."""
    pass


class IdResolutionError(RenderingError):
    """Raised when id resolution fails due to template and pronoun data not matching."""
    pass


class MissingInformationError(RenderingError):
    """Raised when a piece of individual pronoun data does not contain an attribute requested by the renderer."""
