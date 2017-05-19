from oauthlib.oauth2 import RequestValidator
from oauth2 import SignatureMethod_HMAC_SHA1
from CampusClaxon.settings import LTI

class MyRequestValidator(RequestValidator):

    # Ordered roughly in order of appearance in the authorization grant flow

    # Pre- and post-authorization.

    def __init__(self):
        self.enforce_ssl = False
        self.allowed_signature_methods = (LTI['signature_method'],)
        self.timestamp_lifetime = 300

    @staticmethod
    def dummy_client():
        return 'dummy'

    @staticmethod
    def check_client_key(client_key):
        return True

    @staticmethod
    def check_nonce(nonce):
        return True

    @staticmethod
    def check_relms(relms):
        return True

    @staticmethod
    def check_request_token(request_token):
        return True

    @staticmethod
    def check_verifier(verifier):
        return True

    @staticmethod
    def validate_timestamp_and_nonce(client_key, timestamp, nonce, request):
        return True

    @staticmethod
    def validate_client_key(client_key, request):
        if client_key == LTI['key']:
            return True
        else:
            return False

    @staticmethod
    def get_client_secret(client_key, request):
        if client_key == LTI['key']:
            return LTI['secret']
        else:
            return 'dummy'
