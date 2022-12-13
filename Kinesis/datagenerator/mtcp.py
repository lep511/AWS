"""Make boto3 automatically check the shared credentials file for updates.

In some situations, the ~/.aws/credentials file may be periodically updated. For
example, this is the case with the "AWS managed temporary credentials" which are
provided to AWS Cloud9 environments. (See
<https://docs.aws.amazon.com/cloud9/latest/user-guide/how-cloud9-with-iam.html#auth-and-access-control-temporary-managed-credentials>.)

Example usage of this module is:

import boto3
from managed_temporary_credentials_provider import ManagedTempCredentialsProvider

mtcp = ManagedTempCredentialsProvider()

mtcp.register_default()
s3 = boto3.resource("s3")  # Now the credentials will automatically refresh.

s3 = mtcp.boto3_session.resource("s3")  # The same as before, but more explicit.
"""

from datetime import timedelta
from typing import Optional

import boto3
from botocore.credentials import (
    CredentialProvider,
    CredentialResolver,
    DeferredRefreshableCredentials,
    RefreshableCredentials,
    SharedCredentialProvider,
    _local_now,
)
from botocore.session import Session as BCSession
from botocore.session import get_session as get_bc_session


class ManagedTempCredentialsProvider(CredentialProvider):
    """Provides "AWS managed temporary credentials"."""

    METHOD = "managed-temp-creds"
    CANONICAL_NAME: Optional[str] = None

    creds: Optional[RefreshableCredentials]
    shared_credential_provider: SharedCredentialProvider
    refresh_after: timedelta
    botocore_session: BCSession
    boto3_session: boto3.Session

    def __init__(
        self,
        shared_credential_provider: Optional[SharedCredentialProvider] = None,
        refresh_after: timedelta = timedelta(minutes=2),
        botocore_session: BCSession = get_bc_session(),
        deferred: bool = False,
    ):
        self.refresh_after = refresh_after
        self.botocore_session = botocore_session

        if shared_credential_provider is None:
            # Use a default SharedCredentialProvider if none was given.
            shared_credential_provider = _get_shared_credential_provider(
                botocore_session
            )
        self.shared_credential_provider = shared_credential_provider

        if deferred:
            self.creds = DeferredRefreshableCredentials(
                method=self.METHOD, refresh_using=self._refresher
            )
        else:
            new_creds = self.shared_credential_provider.load()
            if new_creds:
                mapping = self._build_mapping(new_creds, expiry_as_str=False)
                self.creds = RefreshableCredentials(
                    method=self.METHOD,
                    refresh_using=self._refresher,
                    **mapping,
                )
            else:
                self.creds = None

        self._register_provider(botocore_session)

        self.boto3_session = boto3.Session(botocore_session=botocore_session)

    def _register_provider(self, bc_session: BCSession) -> None:
        """Register self with the botocore Session's credential resolver."""
        credential_resolver = _get_credential_resolver(bc_session)
        credential_resolver.insert_before(SharedCredentialProvider.METHOD, self)

    def register_default(self) -> None:
        """Replace the boto3 default session with a new one with self registered."""
        new_bc_session = get_bc_session()
        self._register_provider(new_bc_session)
        boto3.setup_default_session(botocore_session=new_bc_session)

    def _refresher(self) -> Optional[dict]:
        """Perform the refresh required by RefreshableCredentials."""
        new_creds = self.shared_credential_provider.load()
        if not new_creds:
            return None
        return self._build_mapping(new_creds)

    def _build_mapping(self, new_creds, expiry_as_str=True) -> dict:
        """Convert a credentials object into the expected dictionary format."""
        expiry_time = _local_now() + self.refresh_after
        if expiry_as_str:
            expiry_time = expiry_time.isoformat()
        return {
            "access_key": new_creds.access_key,
            "secret_key": new_creds.secret_key,
            "token": new_creds.token,
            "expiry_time": expiry_time,
        }

    def load(self) -> Optional[RefreshableCredentials]:
        """Get our credentials as per the CredentialProvider interface."""
        return self.creds


def _get_credential_resolver(bc_session: BCSession) -> CredentialResolver:
    """Get the credential resolver from a botocore Session."""
    return bc_session.get_component("credential_provider")


def _get_shared_credential_provider(
    bc_session: BCSession,
) -> SharedCredentialProvider:
    """Get SharedCredentialProvider from a botocore Session's credential resolver."""
    credential_resolver = _get_credential_resolver(bc_session)
    return credential_resolver.get_provider(SharedCredentialProvider.METHOD)
