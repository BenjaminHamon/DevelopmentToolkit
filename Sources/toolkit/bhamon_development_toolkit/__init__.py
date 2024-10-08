__product__ = None
__copyright__ = None
__version__ = None
__date__ = None


try:
    import bhamon_development_toolkit.__metadata__ # type: ignore

    # pylint: disable = no-member
    __product__ = bhamon_development_toolkit.__metadata__.__product__
    __copyright__ = bhamon_development_toolkit.__metadata__.__copyright__
    __version__ = bhamon_development_toolkit.__metadata__.__version__
    __date__ = bhamon_development_toolkit.__metadata__.__date__
    # pylint: enable = no-member

except ImportError:
    pass
