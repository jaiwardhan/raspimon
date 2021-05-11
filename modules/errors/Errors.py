"""
jaiwardhan/Raspimon

@author: Jaiwardhan Swarnakar, 2021
Copyright 2021-present
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
	http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

from modules.comms.TelegramRelay import PiMonBot
import sys

class ErrorTypes:
    """Defines error `type`s to properly structure errors
    """
    RESOURCE_MISSING = "Resource Missing"
    UNRECOGNIZED = "Unrecognized"
    DENY_RESOLVE = "Unresolvable"

class ErrorCategories:
    """Defines error `category`ies to properly structure errors
    """
    ILLEGAL = "Illegal"
    BAD_ARGUMENT = "Bad Argument"

class Errors:
    """Error objects to properly store and format custom errors which
    can be relayed to an external channel
    """

    Types = ErrorTypes
    Categories = ErrorCategories

    def __init__(self, msg, category = ErrorCategories.ILLEGAL, error_type = ErrorTypes.RESOURCE_MISSING):
        self.category = category
        self.error_type = error_type
        self.msg = msg
    
    def relay(self):
        """Relay the error object to the external channel"""
        Errors.throw(self.category, self.error_type, self.msg)
    
    @staticmethod
    def format(category, error_type, msg):
        """Format the error attributes to an explanable string

        Args:
            category (str): The category to which this error belongs, preferably defined
                by the `ErrorCategories` class
            error_type (str): The error type to which this error tends to be in, preferably
                defined by the `ErrorTypes` class
            msg (str): The custom error explanation as sent by the thrower

        Returns:
            str: Explanable string which can be logged to sent to an external channel
        """
        return "🔥 " + getattr(Errors.Categories, category) + ": " +\
            getattr(Errors.Types, error_type) + ":: " +\
            msg
    
    @staticmethod
    def format_obj(error_obj):
        """Format the error object's attributes to an explanable string. See `Errors.format` for a better explanation

        Args:
            error_obj (Error): The error object

        Returns:
            str: Explanable string which can be logged to sent to an external channel
        """
        return "🔥 " + getattr(Errors.Categories, error_obj.category) + ": " +\
            getattr(Errors.Types, error_obj.error_type) + ":: " +\
            error_obj.msg

    @staticmethod
    def throw(category, error_type, msg):
        """Throw the `format`ted error to an external channel

        Args:
            category (str): The category to which this error belongs, preferably defined
                by the `ErrorCategories` class
            error_type (str): The error type to which this error tends to be in, preferably
                defined by the `ErrorTypes` class
            msg (str): The custom error explanation as sent by the thrower
        """
        if  msg is None or len(str(msg)) == 0 or\
            not hasattr(Errors.Categories, category) or \
            not hasattr(Errors.Types, error_type):
            return
        
        PiMonBot.send(Errors.format(category, error_type, msg))
        Errors.die(msg)
    
    @staticmethod
    def die(with_message):
        """Just die with a scream

        Args:
            with_message (str): Death note just before program termination
        """
        sys.exit(with_message)
