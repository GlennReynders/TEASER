# Created November 2016
# Ina De Jaeger (KU Leuven, EnergyVille)

"""This module includes IDEAS calculation class
"""

import scipy.io
import teaser.logic.utilities as utilities
import numpy as np
import warnings
import os


class IDEAS(object):
    """IDEAS Class

    This class holds functions to sort and partly rewrite zone and building
    attributes specific for IDEAS simulation. (Currently, not in use)

    Parameters
    ----------

    parent: Building()
        The parent class of this object, the Building the attributes are
        calculated for. (default: None)

    """

    def __init__(self, parent):

        self.parent = parent
        self.version = "1.0.0"