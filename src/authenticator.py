import subprocess
import pam


class Authenticator:
    def get_name(self) -> str:
        """Name of the authenticator"""
        return type(self).__name__

    def authenticate(self, username: str, password: str, parameters: dict[str, list[str]]) -> bool:
        """Authenticate against username and password.

        Returns True if the username and password are correct or False if the username and password are incorrect"""
        pass


_AUTHENTICATORS: list[Authenticator] = []


def register_authenticator(authenticator: Authenticator):
    _AUTHENTICATORS.append(authenticator)


def get_authenticators() -> list[Authenticator]:
    return _AUTHENTICATORS


class DenyAuthenticator(Authenticator):
    def authenticate(self, *args, **kwargs) -> bool:
        return False


register_authenticator(DenyAuthenticator())


class AllowAuthenticator(Authenticator):
    def authenticate(self, *args, **kwargs) -> bool:
        return True


register_authenticator(AllowAuthenticator())


class ScriptAuthenticator(Authenticator):
    def authenticate(self, username: str, password: str, parameters: dict[str, list[str]]) -> bool:
        script = next(iter(parameters.get('script') or []), None)
        if script is None:
            return False
        arg_map = parameters.copy()
        arg_map['username'] = [username]
        arg_map['password'] = [password]
        args = []
        for arg_key in arg_map:
            for arg_value in arg_map[arg_key]:
                args.append(arg_key)
                args.append(arg_value)
        result = subprocess.run(args, shell=True, executable=script)
        return result.returncode == 0


register_authenticator(ScriptAuthenticator())


class PamAuthenticator(Authenticator):
    def authenticate(self, username: str, password: str, parameters: dict[str, list[str]]) -> bool:
        service = next(iter(parameters.get('service') or []), None)
        if service is None:
            return False
        return pam.authenticate(username=username, password=password, service=service)


register_authenticator(PamAuthenticator())
