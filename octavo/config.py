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
    """
    A class that stores static properties as default settings vars and
    loads settings via a search path, looking for a YAML file.

    Subclasses should provide defaults for the various configurations as
    directly set class level properties. Note, however, that ANY directive
    set in a configuration file (whether or not it has a default) will be
    added to the configuration.

    Example:

        class MySettings(Settings):

            mysetting = True
            logpath   = "/var/log/myapp.log"
            appname   = "MyApp"

    The configuration is then loaded via the classmethod `load`:

        settings = MySettings.load()

    Access to properties is done two ways:

        settings['mysetting']
        settings.get('mysetting', True)

    Note: None settings are not allowed!
    """

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
        if isinstance(conf, Settings):              # Convert another Settings obj to a dict
            conf = dict(conf.options())

        # Check values for nested settings
        keys = conf.keys()                          # Only evaluate passed in keys
        for key in keys:
            opt = self.get(key, None)               # Check the current property in settings
            if isinstance(opt, Settings):           # Configure nested settings directly
                opt.configure(conf.pop(key))        # Ensure to remove the setting
        self.__dict__.update(conf)                  # Update internal dict with new data

    def options(self):
        """
        Returns an iterable of sorted options in order to loop through all
        the configuration directives specified in the class.
        """
        # Get all the properties of this class
        keys = self.__class__.__dict__.copy()
        keys.update(self.__dict__)
        keys = keys.keys()
        keys.sort()

        for opt in keys:
            val = self.get(opt)
            if val is not None:
                yield opt, val

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
        for opt, val in self.options():
            r = repr(val)
            r = " ".join(r.split())
            wlen = 76-max(len(opt),10)
            if len(r) > wlen:
                r = r[:wlen-3]+"..."
            s += "%-10s = %s\n" % (opt, r)
        return s[:-1]

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


    debug                = False
    htdocs               = os.path.abspath("fixtures/htdocs/")
    database             = os.path.abspath("fixtures/octavo.db")
    model_pickle         = os.path.abspath("fixtures/reccod.pickle")
    goodreads_access_key = os.environ.get("GOODREADS_ACCESS_KEY", None)
    goodreads_secret_key = os.environ.get("GOODREADS_SECRET_KEY", None)

##########################################################################
## On Import, Load Settings
##########################################################################

settings = OctavoSettings.load()

if __name__ == '__main__':
    print settings
