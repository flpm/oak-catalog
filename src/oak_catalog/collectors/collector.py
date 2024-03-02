"""Classes that collect data to create catalog entries."""


class Collector:
    """
    Base class for collectors.
    """

    def __init__(self):
        pass

    def collect(self):
        """
        Collect data to create catalog entries.

        Returns
        -------
        Iterator[CatalogEntry]
            The catalog entries.
        """
        raise NotImplementedError
