# stencila.hub.TokensApi

All URIs are relative to *https://hub.stenci.la/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**tokens_create**](TokensApi.md#tokens_create) | **POST** /tokens/ | Create an authentication token.
[**tokens_delete**](TokensApi.md#tokens_delete) | **DELETE** /tokens/{token}/ | Destroy an authentication token.
[**tokens_list**](TokensApi.md#tokens_list) | **GET** /tokens/ | List authentication tokens.
[**tokens_read**](TokensApi.md#tokens_read) | **GET** /tokens/{token}/ | Retrieve and refresh an authentication token.


# **tokens_create**
> InlineResponse201 tokens_create(data)

Create an authentication token.

Receives a POST with either (a) user's username and password, or (b) an OpenID Connect JSON Web Token. Returns the `username`, and an `token` that can be used for authenticated API requests. Currently, only OpenID tokens issued by Google are accepted.

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
    api_instance = stencila.hub.TokensApi(api_client)
    data = stencila.hub.InlineObject5() # InlineObject5 | 
    try:
        api_response = api_instance.tokens_create(data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling TokensApi.tokens_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **data** | [**InlineObject5**](InlineObject5.md)|  | 

### Return type

[**InlineResponse201**](InlineResponse201.md)

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

# **tokens_delete**
> tokens_delete(token)

Destroy an authentication token.

Deletes the token, whether or not is is expired.

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
    api_instance = stencila.hub.TokensApi(api_client)
    token = 'token_example' # str | 
    try:
        api_instance.tokens_delete(token)
    except ApiException as e:
        print("Exception when calling TokensApi.tokens_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**|  | 

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

# **tokens_list**
> InlineResponse20014 tokens_list(limit=limit, offset=offset)

List authentication tokens.

Returns a list of the authentication tokens for the current user. Stencila does not store the raw token only the `id` (the first eight characters).

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
    api_instance = stencila.hub.TokensApi(api_client)
    limit = 56 # int | Number of results to return per page. (optional)
    offset = 56 # int | The initial index from which to return the results. (optional)
    try:
        api_response = api_instance.tokens_list(limit=limit, offset=offset)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling TokensApi.tokens_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| Number of results to return per page. | [optional] 
 **offset** | **int**| The initial index from which to return the results. | [optional] 

### Return type

[**InlineResponse20014**](InlineResponse20014.md)

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

# **tokens_read**
> Token tokens_read(token)

Retrieve and refresh an authentication token.

Returns details of the authentication token identified including it's new expiry date.

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
    api_instance = stencila.hub.TokensApi(api_client)
    token = 'token_example' # str | 
    try:
        api_response = api_instance.tokens_read(token)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling TokensApi.tokens_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**|  | 

### Return type

[**Token**](Token.md)

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

