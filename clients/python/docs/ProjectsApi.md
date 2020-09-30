# stencila.hub.ProjectsApi

All URIs are relative to *https://hub.stenci.la/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**projects_agents_create**](ProjectsApi.md#projects_agents_create) | **POST** /projects/{project}/agents/ | Create an object.
[**projects_agents_delete**](ProjectsApi.md#projects_agents_delete) | **DELETE** /projects/{project}/agents/{agent}/ | Destroy an object.
[**projects_agents_list**](ProjectsApi.md#projects_agents_list) | **GET** /projects/{project}/agents/ | List objects.
[**projects_agents_partial_update**](ProjectsApi.md#projects_agents_partial_update) | **PATCH** /projects/{project}/agents/{agent}/ | Update an object.
[**projects_agents_read**](ProjectsApi.md#projects_agents_read) | **GET** /projects/{project}/agents/{agent}/ | Retrieve an object.
[**projects_convert**](ProjectsApi.md#projects_convert) | **POST** /projects/{project}/files/{file}!convert | Convert a file to another format.
[**projects_create**](ProjectsApi.md#projects_create) | **POST** /projects/ | Create a project.
[**projects_delete**](ProjectsApi.md#projects_delete) | **DELETE** /projects/{project}/ | Destroy a project.
[**projects_files_delete**](ProjectsApi.md#projects_files_delete) | **DELETE** /projects/{project}/files/{file} | Destroy an object.
[**projects_files_list**](ProjectsApi.md#projects_files_list) | **GET** /projects/{project}/files/ | List objects.
[**projects_files_read**](ProjectsApi.md#projects_files_read) | **GET** /projects/{project}/files/{file} | Retrieve an object.
[**projects_history**](ProjectsApi.md#projects_history) | **GET** /projects/{project}/files/{file}!history | Get the a file&#39;s history.
[**projects_jobs_cancel**](ProjectsApi.md#projects_jobs_cancel) | **PATCH** /projects/{project}/jobs/{job}/cancel/ | Cancel a job.
[**projects_jobs_connect_create**](ProjectsApi.md#projects_jobs_connect_create) | **POST** /projects/{project}/jobs/{job}/connect/{path}/ | Connect to a job.
[**projects_jobs_connect_read**](ProjectsApi.md#projects_jobs_connect_read) | **GET** /projects/{project}/jobs/{job}/connect/{path}/ | Connect to a job.
[**projects_jobs_create**](ProjectsApi.md#projects_jobs_create) | **POST** /projects/{project}/jobs/ | Create an object.
[**projects_jobs_execute**](ProjectsApi.md#projects_jobs_execute) | **POST** /projects/{project}/jobs/execute/ | Create an execute job.
[**projects_jobs_list**](ProjectsApi.md#projects_jobs_list) | **GET** /projects/{project}/jobs/ | List objects.
[**projects_jobs_partial_update**](ProjectsApi.md#projects_jobs_partial_update) | **PATCH** /projects/{project}/jobs/{job}/ | Update an object.
[**projects_jobs_read**](ProjectsApi.md#projects_jobs_read) | **GET** /projects/{project}/jobs/{job}/ | Retrieve an object.
[**projects_list**](ProjectsApi.md#projects_list) | **GET** /projects/ | List projects.
[**projects_partial_update**](ProjectsApi.md#projects_partial_update) | **PATCH** /projects/{project}/ | Update a project.
[**projects_pull**](ProjectsApi.md#projects_pull) | **POST** /projects/{project}/pull/ | Pull the project.
[**projects_read**](ProjectsApi.md#projects_read) | **GET** /projects/{project}/ | Retrieve a project.
[**projects_snapshots_archive**](ProjectsApi.md#projects_snapshots_archive) | **GET** /projects/{project}/snapshots/{snapshot}/archive/ | Retrieve an archive for a project snapshot.
[**projects_snapshots_create**](ProjectsApi.md#projects_snapshots_create) | **POST** /projects/{project}/snapshots/ | Create an object.
[**projects_snapshots_delete**](ProjectsApi.md#projects_snapshots_delete) | **DELETE** /projects/{project}/snapshots/{snapshot}/ | Destroy an object.
[**projects_snapshots_files**](ProjectsApi.md#projects_snapshots_files) | **GET** /projects/{project}/snapshots/{snapshot}/files/{path}/ | Retrieve a file within a snapshot of the project.
[**projects_snapshots_list**](ProjectsApi.md#projects_snapshots_list) | **GET** /projects/{project}/snapshots/ | List objects.
[**projects_snapshots_read**](ProjectsApi.md#projects_snapshots_read) | **GET** /projects/{project}/snapshots/{snapshot}/ | Retrieve an object.
[**projects_snapshots_session**](ProjectsApi.md#projects_snapshots_session) | **POST** /projects/{project}/snapshots/{snapshot}/session/ | Get a session with the snapshot as the working directory.
[**projects_sources_create**](ProjectsApi.md#projects_sources_create) | **POST** /projects/{project}/sources/ | Create a project source.
[**projects_sources_delete**](ProjectsApi.md#projects_sources_delete) | **DELETE** /projects/{project}/sources/{source}/ | Destroy a project source.
[**projects_sources_list**](ProjectsApi.md#projects_sources_list) | **GET** /projects/{project}/sources/ | List a project&#39;s sources.
[**projects_sources_open**](ProjectsApi.md#projects_sources_open) | **GET** /projects/{project}/sources/{source}/open/{path}/ | Open a project source, or a file within it.
[**projects_sources_partial_update**](ProjectsApi.md#projects_sources_partial_update) | **PATCH** /projects/{project}/sources/{source}/ | Update a project source.
[**projects_sources_pull**](ProjectsApi.md#projects_sources_pull) | **POST** /projects/{project}/sources/{source}/pull/ | Pull a project source.
[**projects_sources_read**](ProjectsApi.md#projects_sources_read) | **GET** /projects/{project}/sources/{source}/ | Retrieve a project source.


# **projects_agents_create**
> projects_agents_create(project)

Create an object.

Returns data for the new object.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    try:
        api_instance.projects_agents_create(project)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_agents_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_agents_delete**
> projects_agents_delete(agent, project)

Destroy an object.

Returns an empty response.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    agent = 'agent_example' # str | 
    project = 'project_example' # str | 
    try:
        api_instance.projects_agents_delete(agent, project)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_agents_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agent** | **str**|  | 
 **project** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_agents_list**
> InlineResponse2009 projects_agents_list(project, limit=limit, offset=offset)

List objects.

Returns a list of objects.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    limit = 56 # int | Number of results to return per page. (optional)
    offset = 56 # int | The initial index from which to return the results. (optional)
    try:
        api_response = api_instance.projects_agents_list(project, limit=limit, offset=offset)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_agents_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 
 **limit** | **int**| Number of results to return per page. | [optional] 
 **offset** | **int**| The initial index from which to return the results. | [optional] 

### Return type

[**InlineResponse2009**](InlineResponse2009.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_agents_partial_update**
> ProjectAgentUpdate projects_agents_partial_update(agent, project, data)

Update an object.

Returns data for the updated object.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    agent = 'agent_example' # str | 
    project = 'project_example' # str | 
    data = stencila.hub.ProjectAgentUpdate() # ProjectAgentUpdate | 
    try:
        api_response = api_instance.projects_agents_partial_update(agent, project, data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_agents_partial_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agent** | **str**|  | 
 **project** | **str**|  | 
 **data** | [**ProjectAgentUpdate**](ProjectAgentUpdate.md)|  | 

### Return type

[**ProjectAgentUpdate**](ProjectAgentUpdate.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_agents_read**
> ProjectAgent projects_agents_read(agent, project)

Retrieve an object.

Returns data for the object.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    agent = 'agent_example' # str | 
    project = 'project_example' # str | 
    try:
        api_response = api_instance.projects_agents_read(agent, project)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_agents_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agent** | **str**|  | 
 **project** | **str**|  | 

### Return type

[**ProjectAgent**](ProjectAgent.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_convert**
> File projects_convert(file, project, data)

Convert a file to another format.

Confirms that the destination path and other options are correct, creates a job and redirects to it.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    file = 'file_example' # str | 
    project = 'project_example' # str | 
    data = '/path/to/file' # File | 
    try:
        api_response = api_instance.projects_convert(file, project, data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_convert: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **str**|  | 
 **project** | **str**|  | 
 **data** | [**File**](File.md)|  | 

### Return type

[**File**](File.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_create**
> ProjectCreate projects_create(data)

Create a project.

Receives details of the project. Returns details of the new project.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    data = stencila.hub.ProjectCreate() # ProjectCreate | 
    try:
        api_response = api_instance.projects_create(data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **data** | [**ProjectCreate**](ProjectCreate.md)|  | 

### Return type

[**ProjectCreate**](ProjectCreate.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_delete**
> projects_delete(project)

Destroy a project.

Returns an empty response on success.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    try:
        api_instance.projects_delete(project)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_files_delete**
> projects_files_delete(file, project)

Destroy an object.

Returns an empty response.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    file = 'file_example' # str | 
    project = 'project_example' # str | 
    try:
        api_instance.projects_files_delete(file, project)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_files_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **str**|  | 
 **project** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_files_list**
> InlineResponse20010 projects_files_list(project, limit=limit, offset=offset)

List objects.

Returns a list of objects.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    limit = 56 # int | Number of results to return per page. (optional)
    offset = 56 # int | The initial index from which to return the results. (optional)
    try:
        api_response = api_instance.projects_files_list(project, limit=limit, offset=offset)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_files_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 
 **limit** | **int**| Number of results to return per page. | [optional] 
 **offset** | **int**| The initial index from which to return the results. | [optional] 

### Return type

[**InlineResponse20010**](InlineResponse20010.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_files_read**
> File projects_files_read(file, project)

Retrieve an object.

Returns data for the object.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    file = 'file_example' # str | 
    project = 'project_example' # str | 
    try:
        api_response = api_instance.projects_files_read(file, project)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_files_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **str**|  | 
 **project** | **str**|  | 

### Return type

[**File**](File.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_history**
> File projects_history(file, project)

Get the a file's history.

Returns a paginated history of the file

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    file = 'file_example' # str | 
    project = 'project_example' # str | 
    try:
        api_response = api_instance.projects_history(file, project)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_history: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **str**|  | 
 **project** | **str**|  | 

### Return type

[**File**](File.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_jobs_cancel**
> Job projects_jobs_cancel(job, project, data)

Cancel a job.

If the job is cancellable, it will be cancelled and it's status set to `REVOKED`.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    job = 'job_example' # str | 
    project = 'project_example' # str | 
    data = stencila.hub.Job() # Job | 
    try:
        api_response = api_instance.projects_jobs_cancel(job, project, data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_jobs_cancel: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job** | **str**|  | 
 **project** | **str**|  | 
 **data** | [**Job**](Job.md)|  | 

### Return type

[**Job**](Job.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_jobs_connect_create**
> Job projects_jobs_connect_create(job, path, project, data)

Connect to a job.

Redirects to the internal URL so that users can connect to the job and run methods inside of it, Russian doll style.  This request it proxied through the `router`. This view first checks that the user has permission to edit the job.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    job = 'job_example' # str | 
    path = 'path_example' # str | 
    project = 'project_example' # str | 
    data = stencila.hub.Job() # Job | 
    try:
        api_response = api_instance.projects_jobs_connect_create(job, path, project, data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_jobs_connect_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job** | **str**|  | 
 **path** | **str**|  | 
 **project** | **str**|  | 
 **data** | [**Job**](Job.md)|  | 

### Return type

[**Job**](Job.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_jobs_connect_read**
> Job projects_jobs_connect_read(job, path, project)

Connect to a job.

Redirects to the internal URL so that users can connect to the job and run methods inside of it, Russian doll style.  This request it proxied through the `router`. This view first checks that the user has permission to edit the job.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    job = 'job_example' # str | 
    path = 'path_example' # str | 
    project = 'project_example' # str | 
    try:
        api_response = api_instance.projects_jobs_connect_read(job, path, project)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_jobs_connect_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job** | **str**|  | 
 **path** | **str**|  | 
 **project** | **str**|  | 

### Return type

[**Job**](Job.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_jobs_create**
> projects_jobs_create(project)

Create an object.

Returns data for the new object.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    try:
        api_instance.projects_jobs_create(project)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_jobs_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_jobs_execute**
> projects_jobs_execute(project)

Create an execute job.

Receives the `node` to execute as the request body. Returns the executed `node`.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    try:
        api_instance.projects_jobs_execute(project)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_jobs_execute: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_jobs_list**
> InlineResponse20011 projects_jobs_list(project, limit=limit, offset=offset)

List objects.

Returns a list of objects.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    limit = 56 # int | Number of results to return per page. (optional)
    offset = 56 # int | The initial index from which to return the results. (optional)
    try:
        api_response = api_instance.projects_jobs_list(project, limit=limit, offset=offset)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_jobs_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 
 **limit** | **int**| Number of results to return per page. | [optional] 
 **offset** | **int**| The initial index from which to return the results. | [optional] 

### Return type

[**InlineResponse20011**](InlineResponse20011.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_jobs_partial_update**
> Job projects_jobs_partial_update(job, project, data)

Update an object.

Returns data for the updated object.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    job = 'job_example' # str | 
    project = 'project_example' # str | 
    data = stencila.hub.Job() # Job | 
    try:
        api_response = api_instance.projects_jobs_partial_update(job, project, data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_jobs_partial_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job** | **str**|  | 
 **project** | **str**|  | 
 **data** | [**Job**](Job.md)|  | 

### Return type

[**Job**](Job.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_jobs_read**
> Job projects_jobs_read(job, project)

Retrieve an object.

Returns data for the object.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    job = 'job_example' # str | 
    project = 'project_example' # str | 
    try:
        api_response = api_instance.projects_jobs_read(job, project)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_jobs_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job** | **str**|  | 
 **project** | **str**|  | 

### Return type

[**Job**](Job.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_list**
> InlineResponse2008 projects_list(limit=limit, offset=offset, account=account, role=role, public=public, search=search, source=source)

List projects.

Returns a list of projects that are accessible to the user, including those that are public and those that the user is a member of (i.e. has a project role for).  The returned list can be filtered using query parameters, `account`, `role`, `public`, `search`, `source`. The `role` filter applies to the currently authenticated user, and as such has no effected for unauthenticated requests. Roles can be specified as a comma separated list e.g. `role=author,manager,owner` or using to the `+` operator to indicate the minimum required role e.g. `role=author+` (equivalent to the previous example).  For example, to list all projects for which the authenticated user is a member and which uses a particular Google Doc as a source:      GET /projects?role=member&source=gdoc://1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    limit = 56 # int | Number of results to return per page. (optional)
    offset = 56 # int | The initial index from which to return the results. (optional)
    account = 56 # int | The integer of the id of the account that the project belongs to. (optional)
    role = 'role_example' # str | The role that the currently authenticated user has on the project e.g. \"editor\", \"owner\" (for any role, use \"member\") (optional)
    public = True # bool | Whether or not the project is public. (optional)
    search = 'search_example' # str | A string to search for in the project `name`, `title` or `description`. (optional)
    source = 'source_example' # str | The address of a project source e.g. `github://<org>/<repo>`, `gdoc://<id>`. (optional)
    try:
        api_response = api_instance.projects_list(limit=limit, offset=offset, account=account, role=role, public=public, search=search, source=source)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| Number of results to return per page. | [optional] 
 **offset** | **int**| The initial index from which to return the results. | [optional] 
 **account** | **int**| The integer of the id of the account that the project belongs to. | [optional] 
 **role** | **str**| The role that the currently authenticated user has on the project e.g. \&quot;editor\&quot;, \&quot;owner\&quot; (for any role, use \&quot;member\&quot;) | [optional] 
 **public** | **bool**| Whether or not the project is public. | [optional] 
 **search** | **str**| A string to search for in the project &#x60;name&#x60;, &#x60;title&#x60; or &#x60;description&#x60;. | [optional] 
 **source** | **str**| The address of a project source e.g. &#x60;github://&lt;org&gt;/&lt;repo&gt;&#x60;, &#x60;gdoc://&lt;id&gt;&#x60;. | [optional] 

### Return type

[**InlineResponse2008**](InlineResponse2008.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_partial_update**
> ProjectUpdate projects_partial_update(project, data)

Update a project.

Receives details of the project. Returns updated details of the project.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    data = stencila.hub.ProjectUpdate() # ProjectUpdate | 
    try:
        api_response = api_instance.projects_partial_update(project, data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_partial_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 
 **data** | [**ProjectUpdate**](ProjectUpdate.md)|  | 

### Return type

[**ProjectUpdate**](ProjectUpdate.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_pull**
> projects_pull(project)

Pull the project.

Creates a pull job and redirects to it.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    try:
        api_instance.projects_pull(project)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_pull: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_read**
> Project projects_read(project)

Retrieve a project.

Returns details of the project.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    try:
        api_response = api_instance.projects_read(project)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 

### Return type

[**Project**](Project.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_snapshots_archive**
> Snapshot projects_snapshots_archive(project, snapshot)

Retrieve an archive for a project snapshot.

The user should have read access to the project. Returns a redirect to the URL of the archive.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    snapshot = 'snapshot_example' # str | 
    try:
        api_response = api_instance.projects_snapshots_archive(project, snapshot)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_snapshots_archive: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 
 **snapshot** | **str**|  | 

### Return type

[**Snapshot**](Snapshot.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_snapshots_create**
> Snapshot projects_snapshots_create(project, data)

Create an object.

Returns data for the new object.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    data = stencila.hub.Snapshot() # Snapshot | 
    try:
        api_response = api_instance.projects_snapshots_create(project, data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_snapshots_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 
 **data** | [**Snapshot**](Snapshot.md)|  | 

### Return type

[**Snapshot**](Snapshot.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_snapshots_delete**
> projects_snapshots_delete(project, snapshot)

Destroy an object.

Returns an empty response.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    snapshot = 'snapshot_example' # str | 
    try:
        api_instance.projects_snapshots_delete(project, snapshot)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_snapshots_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 
 **snapshot** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_snapshots_files**
> Snapshot projects_snapshots_files(path, project, snapshot)

Retrieve a file within a snapshot of the project.

For `index.html` will add necessary headers and if necessary inject content required to connect to a session. For other files redirects to the URL for the file (which may be in a remote storage bucket for example).  For security reasons, this function will be deprecated in favour of getting content from the account subdomain.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    path = 'path_example' # str | 
    project = 'project_example' # str | 
    snapshot = 'snapshot_example' # str | 
    try:
        api_response = api_instance.projects_snapshots_files(path, project, snapshot)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_snapshots_files: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **path** | **str**|  | 
 **project** | **str**|  | 
 **snapshot** | **str**|  | 

### Return type

[**Snapshot**](Snapshot.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_snapshots_list**
> InlineResponse20012 projects_snapshots_list(project, limit=limit, offset=offset)

List objects.

Returns a list of objects.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    limit = 56 # int | Number of results to return per page. (optional)
    offset = 56 # int | The initial index from which to return the results. (optional)
    try:
        api_response = api_instance.projects_snapshots_list(project, limit=limit, offset=offset)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_snapshots_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 
 **limit** | **int**| Number of results to return per page. | [optional] 
 **offset** | **int**| The initial index from which to return the results. | [optional] 

### Return type

[**InlineResponse20012**](InlineResponse20012.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_snapshots_read**
> Snapshot projects_snapshots_read(project, snapshot)

Retrieve an object.

Returns data for the object.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    snapshot = 'snapshot_example' # str | 
    try:
        api_response = api_instance.projects_snapshots_read(project, snapshot)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_snapshots_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 
 **snapshot** | **str**|  | 

### Return type

[**Snapshot**](Snapshot.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_snapshots_session**
> Snapshot projects_snapshots_session(project, snapshot, data)

Get a session with the snapshot as the working directory.

If the user has already created or connected to a `session` job for this snapshot, and that job is still running then will return that job. Otherwise, will create a new session.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    snapshot = 'snapshot_example' # str | 
    data = stencila.hub.Snapshot() # Snapshot | 
    try:
        api_response = api_instance.projects_snapshots_session(project, snapshot, data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_snapshots_session: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 
 **snapshot** | **str**|  | 
 **data** | [**Snapshot**](Snapshot.md)|  | 

### Return type

[**Snapshot**](Snapshot.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_sources_create**
> projects_sources_create(project)

Create a project source.

Receives details of the source. This should include the `type` of source, a string matching one of the implemented source classes e.g. `ElifeSource`, `GoogleDocsSource`, `GithubSource` as well as the destination `path`, and other type specific properties. See https://github.com/stencila/hub/blob/master/manager/projects/models/sources.py.  For example, to create a new source for a Google Doc:  ```json {     \"type\": \"GoogleDocsSource\",     \"path\": \"report.gdoc\",     \"docId\": \"1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA\" } ```  Returns details of the new source.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    try:
        api_instance.projects_sources_create(project)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_sources_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_sources_delete**
> projects_sources_delete(project, source)

Destroy a project source.

Removes the source from the project. Returns an empty response on success.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    source = 'source_example' # str | 
    try:
        api_instance.projects_sources_delete(project, source)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_sources_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 
 **source** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_sources_list**
> InlineResponse20013 projects_sources_list(project, limit=limit, offset=offset, search=search)

List a project's sources.

Returns a list of sources in the project. The returned list can be filtered using the query parameter, `search` which matches against the source's `path` string.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    limit = 56 # int | Number of results to return per page. (optional)
    offset = 56 # int | The initial index from which to return the results. (optional)
    search = 'search_example' # str | A string to search for in the source's `path`. (optional)
    try:
        api_response = api_instance.projects_sources_list(project, limit=limit, offset=offset, search=search)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_sources_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 
 **limit** | **int**| Number of results to return per page. | [optional] 
 **offset** | **int**| The initial index from which to return the results. | [optional] 
 **search** | **str**| A string to search for in the source&#39;s &#x60;path&#x60;. | [optional] 

### Return type

[**InlineResponse20013**](InlineResponse20013.md)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_sources_open**
> object projects_sources_open(path, project, source)

Open a project source, or a file within it.

Returns a redirect response to an external URL.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    path = 'path_example' # str | 
    project = 'project_example' # str | 
    source = 'source_example' # str | 
    try:
        api_response = api_instance.projects_sources_open(path, project, source)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_sources_open: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **path** | **str**|  | 
 **project** | **str**|  | 
 **source** | **str**|  | 

### Return type

**object**

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_sources_partial_update**
> projects_sources_partial_update(project, source)

Update a project source.

Receives details of the source. Returns updated details of the source.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    source = 'source_example' # str | 
    try:
        api_instance.projects_sources_partial_update(project, source)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_sources_partial_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 
 **source** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_sources_pull**
> object projects_sources_pull(project, source, data)

Pull a project source.

Creates a pull job and redirects to it.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    source = 'source_example' # str | 
    data = None # object | 
    try:
        api_response = api_instance.projects_sources_pull(project, source, data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_sources_pull: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 
 **source** | **str**|  | 
 **data** | **object**|  | 

### Return type

**object**

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **projects_sources_read**
> object projects_sources_read(project, source)

Retrieve a project source.

Returns details of the source.

### Example

* Api Key Authentication (Token):
```python
from pprint import pprint

import stencila.hub
from stencila.hub.rest import ApiException

configuration = stencila.hub.Configuration(
    host="https://hub.stenci.la/api",
    api_key={'Token': 'YOUR_API_TOKEN'},
    api_key_prefix={'Token': 'Token'}
)
with stencila.hub.ApiClient(configuration) as api_client:
    api_instance = stencila.hub.ProjectsApi(api_client)
    project = 'project_example' # str | 
    source = 'source_example' # str | 
    try:
        api_response = api_instance.projects_sources_read(project, source)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ProjectsApi.projects_sources_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project** | **str**|  | 
 **source** | **str**|  | 

### Return type

**object**

### Authorization

[Token](../README.md#Token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

