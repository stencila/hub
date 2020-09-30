# stencila.hub.JobsApi

All URIs are relative to *https://hub.stenci.la/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**jobs_partial_update**](JobsApi.md#jobs_partial_update) | **PATCH** /jobs/{id}/ | Update a job.
[**jobs_update**](JobsApi.md#jobs_update) | **PUT** /jobs/{id}/ | A view set intended for the &#x60;overseer&#x60; service to update the status of workers.


# **jobs_partial_update**
> InlineObject4 jobs_partial_update(id, data)

Update a job.

This action is intended only to be used by the `overseer` service for it to update the details of a job based on events from the job queue.

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
    api_instance = stencila.hub.JobsApi(api_client)
    id = 56 # int | An autoincrementing integer to allow selecting jobs in the order they were created.
    data = stencila.hub.InlineObject4() # InlineObject4 | 
    try:
        api_response = api_instance.jobs_partial_update(id, data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling JobsApi.jobs_partial_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| An autoincrementing integer to allow selecting jobs in the order they were created. | 
 **data** | [**InlineObject4**](InlineObject4.md)|  | 

### Return type

[**InlineObject4**](InlineObject4.md)

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

# **jobs_update**
> InlineObject3 jobs_update(id, data)

A view set intended for the `overseer` service to update the status of workers.

Requires that the user is a Stencila staff member. Does not require the `overseer` to know which project a job is associated with, or have project permission.

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
    api_instance = stencila.hub.JobsApi(api_client)
    id = 56 # int | An autoincrementing integer to allow selecting jobs in the order they were created.
    data = stencila.hub.InlineObject3() # InlineObject3 | 
    try:
        api_response = api_instance.jobs_update(id, data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling JobsApi.jobs_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| An autoincrementing integer to allow selecting jobs in the order they were created. | 
 **data** | [**InlineObject3**](InlineObject3.md)|  | 

### Return type

[**InlineObject3**](InlineObject3.md)

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

