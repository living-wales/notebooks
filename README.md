# Living Wales Jupyter Notebooks

All Jupyter Noteoobks should be saved in the `notebooks` folder, and each time the main branch of this repository is updated, the 
contents of the notebooks folder is copied to the shared container in the Azure storage account. This shared container is mounted 
as read-only for each Jupyter hub users, so any changes made to this repository will be available to all users within a few 
minutes of the commit/merge.

The process of copying the contents to the shared container is handled by GitHub Actions. The action file is defined in 
`.github/workflows/main.yml` and it requires some secrets to be configured in the GitHub repository to function correctly. 

## Set-up Instructions

All the secret values used in the Action definition need to be added; this is done in 
[settings/secrets/actions](../../settings/secrets/actions). Once the secrets are defined with appropriate values, the 
synchronisation of the `notebooks` folder with the storage account container will happen automagically. 

Add the following Repository Secrets:
#### AZURE_CREDENTIALS  
The following command will create a new Contributor role within the scope of the resource group where the storage account reside; replace `<subscriptionId>` and `<resource_group_name>` with appropriate values. If not already logged in to Azure CLI, do so first with `az login`
```
az ad sp create-for-rbac --name "GitHubActions" --role contributor --scopes /subscriptions/<subscriptionId>/resourceGroups/<resource_group_name>  --sdk-auth
```
The output of this command is a json object - copy and paste the whole object into the Secret value. It should look like this:
```
{
  "clientId": "f34e...dcc3",
  "clientSecret": "~N4...SX",
  "subscriptionId": "8cb...55f",
  "tenantId": "a5f...276",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

#### AZURE_RESOURCE_GROUP
The name of the resource group (as above) as an unquoted string

#### AZURE_STORAGE_ACCOUNT
The name of the storage account as an unquoted string

#### AZURE_CONTAINER_NAME
The name of the container as an unquoted string

#### AZURE_STORAGE_KEY
One of the access keys from the storage account as an unquoted string



