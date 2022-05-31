from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

keyVaultName = "pricingappkv"

def get_secret(key_in):
    KVUri = f"https://{keyVaultName}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KVUri, credential=credential)
    return client.get_secret(key_in).value