
class Authenticator:
    def get_name(self) -> str:
        """Name of the authenticator"""
        return type(self).__name__

    def authenticate(self, username: str, password: str, parameters: dict[str, list[str]]) -> bool:
        """Authenticate against username and password.

        Returns True if the username and password are correct or False if the username and password are incorrect"""
        pass


class DenyAuthenticator(Authenticator):
    def authenticate(self, *args, **kwargs) -> bool:
        return False


class AllowAuthenticator(Authenticator):
    def authenticate(self, *args, **kwargs) -> bool:
        return True


_AUTHENTICATORS: list[Authenticator] = []


def register_authenticator(authenticator: Authenticator):
    _AUTHENTICATORS.append(authenticator)


def get_authenticators() -> list[Authenticator]:
    return _AUTHENTICATORS
