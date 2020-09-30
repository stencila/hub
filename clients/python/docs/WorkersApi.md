# stencila.hub.WorkersApi

All URIs are relative to *https://hub.stenci.la/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**workers_heartbeat**](WorkersApi.md#workers_heartbeat) | **POST** /workers/heartbeat/ | Create a worker heartbeat.
[**workers_offline**](WorkersApi.md#workers_offline) | **POST** /workers/offline/ | Record that a worker has gone offline.
[**workers_online**](WorkersApi.md#workers_online) | **POST** /workers/online/ | Record that a worker has come online.
[**workers_partial_update**](WorkersApi.md#workers_partial_update) | **PATCH** /workers/{hostname}/ | Update information on the worker.


# **workers_heartbeat**
> workers_heartbeat()

Create a worker heartbeat.

An internal route, intended primarily for the `overseer` service. Receives event data. Returns an empty response.

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
    api_instance = stencila.hub.WorkersApi(api_client)
    try:
        api_instance.workers_heartbeat()
    except ApiException as e:
        print("Exception when calling WorkersApi.workers_heartbeat: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

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
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **workers_offline**
> workers_offline()

Record that a worker has gone offline.

An internal route, intended primarily for the `overseer` service. Receives event data. Returns an empty response.

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
    api_instance = stencila.hub.WorkersApi(api_client)
    try:
        api_instance.workers_offline()
    except ApiException as e:
        print("Exception when calling WorkersApi.workers_offline: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

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
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **workers_online**
> workers_online()

Record that a worker has come online.

An internal route, intended primarily for the `overseer` service. Receives event data. Returns an empty response.

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
    api_instance = stencila.hub.WorkersApi(api_client)
    try:
        api_instance.workers_online()
    except ApiException as e:
        print("Exception when calling WorkersApi.workers_online: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

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
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **workers_partial_update**
> workers_partial_update(hostname)

Update information on the worker.

An internal route, intended primarily for the `overseer` service and intended to be used once per worker put separately to `/online`. Receives data such as which virtual host and queues it is listening to. Returns an empty response.

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
    api_instance = stencila.hub.WorkersApi(api_client)
    hostname = 'hostname_example' # str | 
    try:
        api_instance.workers_partial_update(hostname)
    except ApiException as e:
        print("Exception when calling WorkersApi.workers_partial_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **hostname** | **str**|  | 

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

