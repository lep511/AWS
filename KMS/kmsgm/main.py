import boto3
from pprint import pprint
from botocore.exceptions import ClientError
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class KMSManager:
    def __init__(self, kms_client):
        self.kms_client = kms_client
        self.created_keys = []
        self.actual_key = None

    # ################# Create grant #################
    def create_grant(self, key_id, principal):
        """
        Creates a grant for a key that lets a principal generate a symmetric data
        encryption key.

        :param key_id: The ARN or ID of the key.
        :param principal: The ARN of the principal to grant permissions to.
        :return: The grant that is created.
        """
        try:
            grant = self.kms_client.create_grant(
                KeyId=key_id,
                GranteePrincipal=principal,
                Operations=["GenerateDataKey"],
            )
        except ClientError as err:
            logger.error(
                "Couldn't create a grant on key %s. %s",
                key_id,
                err.response["Error"]["Message"],
            )
        else:
            print(f"Grant created on key {key_id}.")
            return grant

    # ################# Create key #################
    def create_key(self, key_desc="Key management demo key"):
        """
        Creates a key (or multiple keys) with a user-provided description.
        :param key_desc: The description of the key.
        """
        try:
            key = self.kms_client.create_key(Description=key_desc)["KeyMetadata"]
        except ClientError as err:
            logging.error(
                "Couldn't create your key. %s",
                err.response["Error"]["Message"],
            )
            raise
        else:
            print(f"Key created: {key['KeyId']}")
            self.actual_state = key["KeyState"]
            self.created_keys.append(key["KeyId"])
            self.actual_key = key["KeyId"]

    def select_key(self, key_id):
        """
        Selects a key for use in subsequent operations.

        :param key_id: The ARN or ID of the key to select.
        """
        # Check if the key exists
        try:
            key = self.kms_client.describe_key(KeyId=key_id)
        except ClientError as err:
            logger.error(
                "Couldn't select key %s. %s",
                key_id,
                err.response["Error"]["Message"],
            )
        else:
            print(f"Key {key_id} selected.")
            self.actual_key = key_id
            self.actual_state = key["KeyMetadata"]["KeyState"]
    
    def create_alias(self, alias, key_id=None):
        """
        Creates an alias for the specified key.

        :param alias: The alias to give the key.
        :param key_id: The ARN or ID of a key to give an alias.
        :return: The alias given to the key.
        """
        if key_id is None:
            if self.actual_key is None:
                logger.error("No key selected.")
                return
            key_id = self.actual_key
            
        try:
            self.kms_client.create_alias(AliasName=alias, TargetKeyId=key_id)
        except ClientError as err:
            logger.error(
                "Couldn't create alias %s. %s",
                alias,
                err.response["Error"]["Message"],
            )
        else:
            print(f"Created alias {alias} for key {key_id}.")
    
    

    def delete_alias(self, alias):
        """
        Deletes an alias.
        
        :param alias: The alias to delete.
        """
        try:
            self.kms_client.delete_alias(AliasName=alias)
        except ClientError as err:
            logger.error(
                "Couldn't delete alias %s. %s",
                alias,
                err.response["Error"]["Message"],
            )
        else:
            print(f"Deleted alias {alias}.")


    def describe_key(self, key_id=None):
        """
        Describes a key.
        
        :param key_id: (Optional) The ARN or ID of the key to describe.
        """
        if key_id is None:
            if self.actual_key is None:
                logger.error("No key selected.")
                return
            key_id = self.actual_key
            
        try:
            key = self.kms_client.describe_key(KeyId=key_id)["KeyMetadata"]
        except ClientError as err:
            logging.error(
                "Couldn't get key '%s'. %s",
                key_id,
                err.response["Error"]["Message"],
            )
        else:
            print(f"Got key {key_id}:")
            pprint(key)


    @property
    def actual_state(self):
        """
        Gets the state of a key.
        """
        if self.actual_key is None:
            logger.error("No key selected.")
            return
        
        try:
            response = self.kms_client.describe_key(KeyId=self.actual_key)
            response = response["KeyMetadata"]["KeyState"]
            
        except ClientError as err:
            logger.error(
                "Couldn't get state of key %s. %s",
                self.actual_key,
                err.response["Error"]["Message"],
            )
        else:
            return response
        
        
    @actual_state.setter
    def actual_state(self, value):
        """
        Sets the state of a key to enabled or disabled.
        
        :param value: The state to set the key to. Acceptable values are:
          - "Enabled"
          - "Disabled"
        """
        
        if self.actual_key is None:
            logger.error("No key selected.")
            return
        
        if value not in ("Enabled", "Disabled"):
            logger.error(f"Invalid state value {value}. Must be 'Enabled' or 'Disabled'.")
            return
        
        actual_state = self.kms_client.describe_key(KeyId=self.actual_key)["KeyMetadata"]["KeyState"]
        
        if actual_state == value:
            print(f"Key {self.actual_key} is already {value}.")
            return
        else:
            try:
                if value == "Enabled":
                    self.kms_client.enable_key(KeyId=self.actual_key)
                else:
                    self.kms_client.disable_key(KeyId=self.actual_key)
            except ClientError as err:
                logger.error(
                    "Couldn't set key %s to %s. %s",
                    self.actual_key,
                    value,
                    err.response["Error"]["Message"],
                )
            else:
                print(f"Key {self.actual_key} set to {value}.")


    def encrypt(self, raw_text, key_id=None):
        """
        Encrypts text by using the specified key.

        :param text: The text to encrypt.
        :param key_id: The ARN or ID of the key to use for encryption.
        :return: The encrypted version of the text.
        """
        if key_id is None:
            if self.actual_key is None:
                logger.error("No key selected.")
                return
            key_id = self.actual_key
        
        try:
            cipher_text = self.kms_client.encrypt(
                KeyId=key_id, Plaintext=raw_text.encode()
            )["CiphertextBlob"]
        except ClientError as err:
            logger.error(
                "Couldn't encrypt text. Here's why: %s",
                err.response["Error"]["Message"],
            )
        else:
            return cipher_text


    def decrypt(self, cipher_text, key_id=None):
        """
        Decrypts text previously encrypted with a key.

        :param cipher_text: The encrypted text to decrypt.
        :param key_id: The ARN or ID of the key used to decrypt the data.
        """
        if key_id is None:
            if self.actual_key is None:
                logger.error("No key selected.")
                return
            key_id = self.actual_key
        
        try:
            text = self.kms_client.decrypt(
                KeyId=key_id, CiphertextBlob=cipher_text
            )["Plaintext"]
        except ClientError as err:
            logger.error(
                "Couldn't decrypt your ciphertext. %s",
                err.response["Error"]["Message"],
            )
        else:
            return text.decode()