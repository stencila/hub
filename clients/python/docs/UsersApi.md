# stencila.hub.UsersApi

All URIs are relative to *https://hub.stenci.la/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**users_list**](UsersApi.md#users_list) | **GET** /users/ | List users.
[**users_me**](UsersApi.md#users_me) | **GET** /users/me/ | Retrieve the current user.
[**users_read**](UsersApi.md#users_read) | **GET** /users/{id}/ | Retrieve a user.


# **users_list**
> InlineResponse20015 users_list(limit=limit, offset=offset, search=search)

List users.

The optional `search` parameter is a search string used to filter user. Returns details on each user.

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
    api_instance = stencila.hub.UsersApi(api_client)
    limit = 56 # int | Number of results to return per page. (optional)
    offset = 56 # int | The initial index from which to return the results. (optional)
    search = 'search_example' # str | String to search for within user usernames, first and last names and email addresses. (optional)
    try:
        api_response = api_instance.users_list(limit=limit, offset=offset, search=search)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling UsersApi.users_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| Number of results to return per page. | [optional] 
 **offset** | **int**| The initial index from which to return the results. | [optional] 
 **search** | **str**| String to search for within user usernames, first and last names and email addresses. | [optional] 

### Return type

[**InlineResponse20015**](InlineResponse20015.md)

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

# **users_me**
> Me users_me()

Retrieve the current user.

Returns details of the user who is currently authenticated.

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
    api_instance = stencila.hub.UsersApi(api_client)
    try:
        api_response = api_instance.users_me()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling UsersApi.users_me: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Me**](Me.md)

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

# **users_read**
> User users_read(id)

Retrieve a user.

Returns details of the user.

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
    api_instance = stencila.hub.UsersApi(api_client)
    id = 'id_example' # str | 
    try:
        api_response = api_instance.users_read(id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling UsersApi.users_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**User**](User.md)

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

