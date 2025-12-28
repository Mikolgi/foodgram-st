from dotenv import load_dotenv
import requests
import os

load_dotenv()


class VaultHelper:
    """
    A helper class for interacting with Hashicorp's Vault.

    This class provides methods for retrieving secrets from Vault.
    """

    def __init__(self):
        load_dotenv()
        self._vault_address = os.getenv('VAULT_ADDR', 'http://vault.localhost')
        self._vault_token = os.getenv('VAULT_TOKEN')
        
        if not self._vault_token:
            raise ValueError("VAULT_TOKEN environment variable is not set")

    def __get_secrets(self, secret_path):
        """
        Get the secrets from Vault.

        :param secret_path: str
        :return: dict
        """
        resp = requests.get(
            url=f'{self._vault_address}/v1/secrets/data/{secret_path}',
            headers={
                "X-Vault-Token": self._vault_token
            }
        )

        if resp.status_code != 200:
            raise Exception(f"Failed to get secrets from Vault: {resp.text}")
        
        json_data = resp.json()
        return json_data['data']['data']

    def get_api_key(self, alias):
        """
        Get the API key from Vault.

        :param alias: str - 'holidays' or 'weather'
        :return: str
        """
        secrets = self.__get_secrets(secret_path='api-keys')
        key_name = f'{alias}_api_key'
        return secrets[key_name]

    def get_rabbitmq_credentials(self):
        """
        Get the RabbitMQ credentials from Vault.

        :return: dict with 'username' and 'password' keys
        """
        return self.__get_secrets(secret_path='rabbitmq')

