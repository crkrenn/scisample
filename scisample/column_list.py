"""
Module defining the column list object.
"""

import logging

from contextlib import suppress
from scisample.base_sampler import (BaseSampler)

LOG = logging.getLogger(__name__)


class ColumnListSampler(BaseSampler):
    """
    Class defining basic column list sampling.

    This is similar to the ``csv`` functionality of ``codepy setup``
    and ``codepy run``.  Its sampler data takes two blocks:
    ``constants`` and ``parameters``:

    .. code:: yaml

        sampler:
            type: column_list
            constants:
                X1: 20
            parameters: |
                X2       X3
                5        5
                10       10

    Entries in the ``constants`` dictionary will be added to all samples.
    Entries in the ``parameters`` block will be matched one to one.  The
    result of the above block would be:

    .. code:: python

        [{X1: 20, X2: 5, X3: 5}, {X1: 20, X2: 10, X3: 10}]
    """

    def is_valid(self):
        """
        Check if the sampler is valid.

        Checks the sampler data against the built-in schema.

        Checks that all entries in ``parameters`` have the same
        length.

        :returns: True if the schema is valid, False otherwise.
        """
        if not super(ColumnListSampler, self).is_valid():
            return False

        if 'constants' not in self.data and 'parameters' not in self.data:
            LOG.error(
                "Either constants or parameters must be included in the "
                "sampler data"
                )
            return False
        return True

    @property
    def parameters(self):
        """
        Return a of list of the parameters being generated by the
        sampler.
        """
        parameters = []
        with suppress(KeyError):
            parameters.extend(list(self.data['constants'].keys()))
        with suppress(KeyError):
            rows = self.data['parameters'].split('\n')
            headers = rows.pop(0).split()
            parameters.extend(headers)
        return parameters

    def get_samples(self):
        """
        Get samples from the sampler.

        This returns samples as a list of dictionaries, with the
        sample variables as the keys:

        .. code:: python

            [{'b': 0.89856, 'a': 1}, {'b': 0.923223, 'a': 1}, ... ]
        """
        LOG.info("Entering ColumnListSampler.get_samples()")
        if self._samples is not None:
            return self._samples

        self._samples = []

        parameter_samples = []
        with suppress(KeyError):
            rows = self.data['parameters'].split('\n')
            headers = rows.pop(0).split()
            num_samples = 0
            for row in rows:
                data = row.split()
                if data:
                    if len(data) != len(headers):
                        LOG.error(
                            "All parameters must have the " +
                            "same number of entries"
                        )
                        return False
                    sample = {}
                    for header, datum in zip(headers, data):
                        sample[header] = datum
                    parameter_samples.append(sample)
                    num_samples += 1

        for i in range(len(parameter_samples)):
            new_sample = {}

            with suppress(KeyError):
                new_sample.update(self.data['constants'])

            with suppress(KeyError):
                for key, value in parameter_samples[i].items():
                    new_sample[key] = value

            self._samples.append(new_sample)

        return self._samples
