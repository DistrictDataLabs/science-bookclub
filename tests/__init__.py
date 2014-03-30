# tests
# Test Package for the Science-Bookclub
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Mar 30 18:18:28 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: __init__.py [] benjamin@bengfort.com $

"""
Test Package for the Science-Bookclub
"""

##########################################################################
## Imports
##########################################################################

import unittest

##########################################################################
## Initialization Test Case
##########################################################################

class InitializationTest(unittest.TestCase):
    """
    Tests that ensure the test package will intialize
    """

    def test_initialization(self):
        """
        Assert the world is sane, 2+2=4
        """
        self.assertEqual(2+2, 4)

    def test_import(self):
        """
        Check that we can import the library
        """
        try:
            import octavo
        except ImportError:
            self.fail("Could not import the octavo library.")
