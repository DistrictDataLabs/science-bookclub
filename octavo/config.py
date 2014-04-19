# octavo.config
# Loads configuration data from a YAML file.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Mar 30 20:45:40 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: config.py [] benjamin@bengfort.com $

"""
Loads configuration data from a YAML file.
"""

##########################################################################
## Imports
##########################################################################

import os
import yaml

##########################################################################
## Settings Base Class
##########################################################################

class Settings(object):

    CONF_PATHS = []                                 # Search path for configuration files

    @classmethod
    def load(klass):
        """
        Instantiates the settings by attempting to load the configuration
        from YAML files specified by the CONF_PATHS variable. This should
        be the main entry point for accessing settings.
        """
        settings = klass()
        for path in klass.CONF_PATHS:
            if os.path.exists(path):
                with open(path, 'r') as conf:
                    settings.configure(yaml.load(conf))
        return settings

    def configure(self, conf=None):
        """
        Allows updating of the settings via a dictionary of settings or
        another settings object. Generally speaking, this method is used
        to configure the object from JSON or YAML.
        """
        if not conf: return                         # Don't do anything with empty conf
        self.__dict__.update(conf)                  # Update internal dict with new data


    def get(self, key, default=None):
        """
        Fetches a key from the settings without raising a KeyError and if
        the key doesn't exist on the config, it returns a default instead.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key):
        """
        Main settings access method. This performs a case insensitive
        lookup of the key on the class, but filters methods and anything
        that starts with an underscore.
        """
        key = key.lower()                                   # Case insensitive lookup
        if not key.startswith('_') and hasattr(self, key):  # Ignore _vars and ensure attr exists
            attr = getattr(self, key)
            if not callable(attr):                          # Ignore any methods
                return attr
        raise KeyError("%s has no setting '%s'" % (self.__class__.__name__, key))

    def __str__(self):
        """
        Pretty print the configuration
        """
        s = ""
        for param in self.__dict__.items():
            if param[0].startswith('_'): continue
            s += "%s: %s\n" % param
        return s

##########################################################################
## Octavo Settings
##########################################################################

class OctavoSettings(Settings):

    # Search path for configuration files
    CONF_PATHS = [
        '/etc/octavo/octavo.yaml',                 # The global configuration
        os.path.expandvars('$HOME/.octavo.yaml'),  # User specific configuration
        os.path.abspath('conf/octavo.yaml'),       # Local directory configuration
        os.path.abspath('octavo.yaml'),            # Local directory configuration
    ]

    def __init__(self):
        self.debug                = False
        self.htdocs               = os.path.abspath("fixtures/htdocs/")
        self.database             = os.path.abspath("fixtures/octavo.db")
        self.model_pickle         = os.path.abspath("fixtures/reccod.pickle")
        self.goodreads_access_key = os.environ.get("GOODREADS_ACCESS_KEY", None)
        self.goodreads_secret_key = os.environ.get("GOODREADS_SECRET_KEY", None)

##########################################################################
## On Import, Load Settings
##########################################################################

settings = OctavoSettings.load()

if __name__ == '__main__':
    print settings
