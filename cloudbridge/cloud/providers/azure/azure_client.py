import logging

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.subscriptions import SubscriptionClient
from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import BlockBlobService, PublicAccess
from azure.common import AzureMissingResourceHttpError

log = logging.getLogger(__name__)


class AzureClient(object):
    def __init__(self, config):
        self._config = config
        self.subscription_id = config.get('azure_subscription_id')
        credentials = ServicePrincipalCredentials(
            client_id=config.get('azure_client_Id'),
            secret=config.get('azure_secret'),
            tenant=config.get('azure_tenant')
        )

        self._resource_client = ResourceManagementClient(credentials, self.subscription_id)
        self._storage_client = StorageManagementClient(credentials, self.subscription_id)
        self._network_management_client = NetworkManagementClient(credentials, self.subscription_id)
        self._subscription_client = SubscriptionClient(credentials)
        self._compute_client = ComputeManagementClient(credentials, self.subscription_id)
        access_key_result = self.storage_client.storage_accounts.list_keys(self.resource_group_name,
                                                                           self.storage_account_name)
        self._block_blob_service = BlockBlobService(self.storage_account_name, access_key_result.keys[0].value)

        log.debug("azure subscription : %s", self.subscription_id)

    @property
    def resource_group_name(self):
        return self._config.get('azure_resource_group')

    @property
    def storage_account_name(self):
        return self._config.get('azure_storage_account_name')

    @property
    def block_blob_service(self):
        return self._storage_client

    @property
    def storage_client(self):
        return self._storage_client

    @property
    def subscription_client(self):
        return self._subscription_client

    @property
    def resource_client(self):
        return self._resource_client

    @property
    def compute_client(self):
        return self._compute_client

    @property
    def network_management_client(self):
        return self._network_management_client

    @property
    def blob_service(self):
        return self._block_blob_service

    def get_resource_group(self, name):
        return self.resource_client.resource_groups.get(name)

    def create_resource_group(self, name, parameters):
        return self.resource_client.resource_groups.create_or_update(name, parameters)

    def list_locations(self):
        return self.subscription_client.subscriptions.list_locations(self.subscription_id)

    def list_security_group(self):
        return self.network_management_client.network_security_groups.list(self.resource_group_name)

    def create_security_group(self, name, parameters):
        sg_create = self.network_management_client.network_security_groups.create_or_update(self.resource_group_name,
                                                                                            name, parameters)
        return sg_create.result()

    def create_security_group_rule(self, security_group, rule_name, parameters):
        security_rules_operations = self.network_management_client.security_rules
        sro = security_rules_operations.create_or_update(self.resource_group_name, security_group, rule_name,
                                                         parameters)
        result = sro.result()
        return result

    def delete_security_group_rule(self, name, security_group):
        security_rules_operations = self.network_management_client.security_rules
        sro = security_rules_operations.delete(self.resource_group_name, security_group, name)
        return sro.result()

    def get_security_group(self, name):
        return self.network_management_client.network_security_groups.get(self.resource_group_name, name)

    def delete_security_group(self, name):
        return self.network_management_client.network_security_groups.delete(self.resource_group_name, name)

    def list_containers(self):
        return self.blob_service.list_containers()

    def create_container(self, container_name):
        self.blob_service.create_container(container_name, public_access=PublicAccess.Container)
        return self.blob_service.get_container_properties(container_name)

    def get_container(self, container_name):
        return self.blob_service.get_container_properties(container_name)

    def delete_container(self, container_name):
        self.blob_service.delete_container(container_name)
        return None
    
    def list_blobs(self, container_name):
        return self.blob_service.list_blobs(container_name)

    def get_blob(self, container_name, blob_name):
        try:
            return self.blob_service.get_blob_properties(container_name, blob_name)
        except AzureMissingResourceHttpError:
            return None

    def create_blob_from_text(self, container_name, blob_name, text):
        self.blob_service.create_blob_from_text(container_name, blob_name, text)
        return None

    def create_blob_from_file(self, container_name, blob_name, file_path):
        self.blob_service.create_blob_from_path(container_name, blob_name, file_path)
        return None

    def delete_blob(self, container_name, blob_name):
        self.blob_service.delete_blob(container_name, blob_name)

    def get_blob_url(self, container_name, blob_name):
        return self.blob_service.make_blob_url(container_name, blob_name)

    def get_blob_content(self, container_name, blob_name):
        return self.blob_service.get_blob_to_text(container_name, blob_name)
