'''
Created on 01.02.2010

@author: michi
'''
class ConfigurationError(UserWarning):
    pass
class DuplicateIdentifierError(Exception):
    pass
class UserAbortError(UserWarning):
    pass
class UserInteractionRequiredError(UserWarning):
    pass