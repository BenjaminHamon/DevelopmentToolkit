import getpass

from bhamon_development_toolkit.security.credentials import Credentials
from bhamon_development_toolkit.security.credentials_provider import CredentialsProvider


class InteractiveCredentialsProvider(CredentialsProvider):


    def __init__(self, show_secrets: bool = False) -> None:
        self.show_secrets = show_secrets


    def get_credentials(self, identifier: str) -> Credentials:
        return self.prompt_for_credentials(identifier)


    def prompt_for_credentials(self, identifier: str) -> Credentials:
        input_function = input if self.show_secrets else getpass.getpass

        try:
            print("")
            print("Enter credentials for '%s'" % identifier)
            username = input_function("Username: ")
            secret = input_function("Secret: ")
            print("")
        except KeyboardInterrupt:
            print("\n")
            raise

        return Credentials(username = username, secret = secret)
