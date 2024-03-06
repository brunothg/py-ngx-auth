class Authenticator:
    def authenticate(self, username, password) -> bool:
        """Authenticate against username and password.

        Returns True if the username and password are correct or False if the username and password are incorrect"""
        pass


class DenyAuthenticator(Authenticator):
    def authenticate(self, username, password) -> bool:
        return False


class AllowAuthenticator(Authenticator):
    def authenticate(self, username, password) -> bool:
        return True
