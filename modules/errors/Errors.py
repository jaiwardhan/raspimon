
from modules.comms.TelegramRelay import PiMonBot
import sys

class ErrorTypes:
    RESOURCE_MISSING = "Resource Missing"
    UNRECOGNIZED = "Unrecognized"
    DENY_RESOLVE = "Unresolvable"

class ErrorCategories:
    ILLEGAL = "Illegal"
    BAD_ARGUMENT = "Bad Argument"

class Errors:
    Types = ErrorTypes
    Categories = ErrorCategories

    def __init__(self, msg, category = ErrorCategories.ILLEGAL, error_type = ErrorTypes.RESOURCE_MISSING):
        self.category = category
        self.error_type = error_type
        self.msg = msg
    
    def relay(self):
        Errors.throw(self.category, self.error_type, self.msg)
    
    @staticmethod
    def format(category, error_type, msg):
        return "🔥 " + getattr(Errors.Categories, category) + ": " +\
            getattr(Errors.Types, error_type) + ":: " +\
            msg
    
    @staticmethod
    def format_obj(error_obj):
        return "🔥 " + getattr(Errors.Categories, error_obj.category) + ": " +\
            getattr(Errors.Types, error_obj.error_type) + ":: " +\
            error_obj.msg

    @staticmethod
    def throw(category, error_type, msg):
        if  msg is None or len(str(msg)) == 0 or\
            not hasattr(Errors.Categories, category) or \
            not hasattr(Errors.Types, error_type):
            return
        
        PiMonBot.send(Errors.format(category, error_type, msg))
        Errors.die(msg)
    
    @staticmethod
    def die(with_message):
        sys.exit(with_message)
