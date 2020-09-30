# stencila.hub.AccountsApi

All URIs are relative to *https://hub.stenci.la/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**accounts_broker_list**](AccountsApi.md#accounts_broker_list) | **GET** /accounts/{account}/broker | Connect to the job broker for the account.
[**accounts_create**](AccountsApi.md#accounts_create) | **POST** /accounts/ | Create an object.
[**accounts_list**](AccountsApi.md#accounts_list) | **GET** /accounts/ | List objects.
[**accounts_partial_update**](AccountsApi.md#accounts_partial_update) | **PATCH** /accounts/{account}/ | Update an object.
[**accounts_queues_list**](AccountsApi.md#accounts_queues_list) | **GET** /accounts/{account}/queues/ | List objects.
[**accounts_queues_read**](AccountsApi.md#accounts_queues_read) | **GET** /accounts/{account}/queues/{queue}/ | Retrieve an object.
[**accounts_read**](AccountsApi.md#accounts_read) | **GET** /accounts/{account}/ | Retrieve an object.
[**accounts_teams_create**](AccountsApi.md#accounts_teams_create) | **POST** /accounts/{account}/teams/ | Create a team.
[**accounts_teams_delete**](AccountsApi.md#accounts_teams_delete) | **DELETE** /accounts/{account}/teams/{team}/ | Destroy a team.
[**accounts_teams_list**](AccountsApi.md#accounts_teams_list) | **GET** /accounts/{account}/teams/ | List teams.
[**accounts_teams_members_create**](AccountsApi.md#accounts_teams_members_create) | **POST** /accounts/{account}/teams/{team}/members/ | 
[**accounts_teams_members_delete**](AccountsApi.md#accounts_teams_members_delete) | **DELETE** /accounts/{account}/teams/{team}/members/{user}/ | 
[**accounts_teams_partial_update**](AccountsApi.md#accounts_teams_partial_update) | **PATCH** /accounts/{account}/teams/{team}/ | Update a team.
[**accounts_teams_read**](AccountsApi.md#accounts_teams_read) | **GET** /accounts/{account}/teams/{team}/ | Retrieve a team.
[**accounts_update_plan**](AccountsApi.md#accounts_update_plan) | **PATCH** /accounts/{account}/update_plan/ | 
[**accounts_users_create**](AccountsApi.md#accounts_users_create) | **POST** /accounts/{account}/users/ | Add an account user.
[**accounts_users_delete**](AccountsApi.md#accounts_users_delete) | **DELETE** /accounts/{account}/users/{user}/ | Remove an account user.
[**accounts_users_list**](AccountsApi.md#accounts_users_list) | **GET** /accounts/{account}/users/ | A view set for account users.
[**accounts_users_partial_update**](AccountsApi.md#accounts_users_partial_update) | **PATCH** /accounts/{account}/users/{user}/ | A view set for account users.
[**accounts_users_read**](AccountsApi.md#accounts_users_read) | **GET** /accounts/{account}/users/{user}/ | A view set for account users.
[**accounts_workers_heartbeats_list**](AccountsApi.md#accounts_workers_heartbeats_list) | **GET** /accounts/{account}/workers/{worker}/heartbeats/ | List objects.
[**accounts_workers_list**](AccountsApi.md#accounts_workers_list) | **GET** /accounts/{account}/workers/ | List objects.
[**accounts_workers_read**](AccountsApi.md#accounts_workers_read) | **GET** /accounts/{account}/workers/{worker}/ | Retrieve an object.
[**accounts_zones_create**](AccountsApi.md#accounts_zones_create) | **POST** /accounts/{account}/zones/ | Create an object.
[**accounts_zones_delete**](AccountsApi.md#accounts_zones_delete) | **DELETE** /accounts/{account}/zones/{zone}/ | Destroy an object.
[**accounts_zones_list**](AccountsApi.md#accounts_zones_list) | **GET** /accounts/{account}/zones/ | List objects.
[**accounts_zones_read**](AccountsApi.md#accounts_zones_read) | **GET** /accounts/{account}/zones/{zone}/ | Retrieve an object.


# **accounts_broker_list**
> accounts_broker_list(account)

Connect to the job broker for the account.

This endpoint is for self-hosted workers. These need to be enabled for the account.  You may need to include your authentication token in the URL. For example, when using [Celery](https://www.celeryproject.org/) in Python:  ```python app = Celery(     broker=\"https://{token}@hub.stenci.la/api/accounts/{account}/jobs/broker\".format(         token = os.environ.get(\"STENCILA_TOKEN\"),         account = os.environ.get(\"STENCILA_ACCOUNT\")     ) ) ```

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    try:
        api_instance.accounts_broker_list(account)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_broker_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 

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

# **accounts_create**
> AccountCreate accounts_create(data)

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
    api_instance = stencila.hub.AccountsApi(api_client)
    data = stencila.hub.AccountCreate() # AccountCreate | 
    try:
        api_response = api_instance.accounts_create(data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **data** | [**AccountCreate**](AccountCreate.md)|  | 

### Return type

[**AccountCreate**](AccountCreate.md)

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

# **accounts_list**
> InlineResponse200 accounts_list(limit=limit, offset=offset)

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
    api_instance = stencila.hub.AccountsApi(api_client)
    limit = 56 # int | Number of results to return per page. (optional)
    offset = 56 # int | The initial index from which to return the results. (optional)
    try:
        api_response = api_instance.accounts_list(limit=limit, offset=offset)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| Number of results to return per page. | [optional] 
 **offset** | **int**| The initial index from which to return the results. | [optional] 

### Return type

[**InlineResponse200**](InlineResponse200.md)

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

# **accounts_partial_update**
> AccountUpdate accounts_partial_update(account, data)

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    data = stencila.hub.AccountUpdate() # AccountUpdate | 
    try:
        api_response = api_instance.accounts_partial_update(account, data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_partial_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **data** | [**AccountUpdate**](AccountUpdate.md)|  | 

### Return type

[**AccountUpdate**](AccountUpdate.md)

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

# **accounts_queues_list**
> InlineResponse2001 accounts_queues_list(account, limit=limit, offset=offset)

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    limit = 56 # int | Number of results to return per page. (optional)
    offset = 56 # int | The initial index from which to return the results. (optional)
    try:
        api_response = api_instance.accounts_queues_list(account, limit=limit, offset=offset)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_queues_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **limit** | **int**| Number of results to return per page. | [optional] 
 **offset** | **int**| The initial index from which to return the results. | [optional] 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

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

# **accounts_queues_read**
> Queue accounts_queues_read(account, queue)

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    queue = 'queue_example' # str | 
    try:
        api_response = api_instance.accounts_queues_read(account, queue)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_queues_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **queue** | **str**|  | 

### Return type

[**Queue**](Queue.md)

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

# **accounts_read**
> AccountRetrieve accounts_read(account)

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    try:
        api_response = api_instance.accounts_read(account)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 

### Return type

[**AccountRetrieve**](AccountRetrieve.md)

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

# **accounts_teams_create**
> accounts_teams_create(account)

Create a team.

Returns data for the new team.

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    try:
        api_instance.accounts_teams_create(account)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_teams_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 

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

# **accounts_teams_delete**
> accounts_teams_delete(account, team)

Destroy a team.

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    team = 'team_example' # str | 
    try:
        api_instance.accounts_teams_delete(account, team)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_teams_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **team** | **str**|  | 

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

# **accounts_teams_list**
> InlineResponse2002 accounts_teams_list(account, limit=limit, offset=offset)

List teams.

Returns a list of teams for the account.

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    limit = 56 # int | Number of results to return per page. (optional)
    offset = 56 # int | The initial index from which to return the results. (optional)
    try:
        api_response = api_instance.accounts_teams_list(account, limit=limit, offset=offset)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_teams_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **limit** | **int**| Number of results to return per page. | [optional] 
 **offset** | **int**| The initial index from which to return the results. | [optional] 

### Return type

[**InlineResponse2002**](InlineResponse2002.md)

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

# **accounts_teams_members_create**
> InlineObject1 accounts_teams_members_create(account, team, data)



Add a user to the team.

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    team = 'team_example' # str | 
    data = stencila.hub.InlineObject1() # InlineObject1 | 
    try:
        api_response = api_instance.accounts_teams_members_create(account, team, data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_teams_members_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **team** | **str**|  | 
 **data** | [**InlineObject1**](InlineObject1.md)|  | 

### Return type

[**InlineObject1**](InlineObject1.md)

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

# **accounts_teams_members_delete**
> accounts_teams_members_delete(account, team, user)



Remove a user from the team.

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    team = 'team_example' # str | 
    user = 'user_example' # str | 
    try:
        api_instance.accounts_teams_members_delete(account, team, user)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_teams_members_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **team** | **str**|  | 
 **user** | **str**|  | 

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

# **accounts_teams_partial_update**
> InlineObject accounts_teams_partial_update(account, team, data)

Update a team.

Returns data for the team.

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    team = 'team_example' # str | 
    data = stencila.hub.InlineObject() # InlineObject | 
    try:
        api_response = api_instance.accounts_teams_partial_update(account, team, data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_teams_partial_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **team** | **str**|  | 
 **data** | [**InlineObject**](InlineObject.md)|  | 

### Return type

[**InlineObject**](InlineObject.md)

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

# **accounts_teams_read**
> AccountTeam accounts_teams_read(account, team)

Retrieve a team.

Returns data for the team.

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    team = 'team_example' # str | 
    try:
        api_response = api_instance.accounts_teams_read(account, team)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_teams_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **team** | **str**|  | 

### Return type

[**AccountTeam**](AccountTeam.md)

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

# **accounts_update_plan**
> accounts_update_plan(account)



Update the plan / tier for an account.

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    try:
        api_instance.accounts_update_plan(account)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_update_plan: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 

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

# **accounts_users_create**
> InlineObject2 accounts_users_create(account, data)

Add an account user.

Returns data for the new account user.

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    data = stencila.hub.InlineObject2() # InlineObject2 | 
    try:
        api_response = api_instance.accounts_users_create(account, data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_users_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **data** | [**InlineObject2**](InlineObject2.md)|  | 

### Return type

[**InlineObject2**](InlineObject2.md)

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

# **accounts_users_delete**
> accounts_users_delete(account, user)

Remove an account user.

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    user = 'user_example' # str | 
    try:
        api_instance.accounts_users_delete(account, user)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_users_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **user** | **str**|  | 

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

# **accounts_users_list**
> InlineResponse2003 accounts_users_list(account, limit=limit, offset=offset)

A view set for account users.

Provides basic CRUD views for account users.

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    limit = 56 # int | Number of results to return per page. (optional)
    offset = 56 # int | The initial index from which to return the results. (optional)
    try:
        api_response = api_instance.accounts_users_list(account, limit=limit, offset=offset)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_users_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **limit** | **int**| Number of results to return per page. | [optional] 
 **offset** | **int**| The initial index from which to return the results. | [optional] 

### Return type

[**InlineResponse2003**](InlineResponse2003.md)

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

# **accounts_users_partial_update**
> AccountUser accounts_users_partial_update(account, user, data)

A view set for account users.

Provides basic CRUD views for account users.

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    user = 'user_example' # str | 
    data = stencila.hub.AccountUser() # AccountUser | 
    try:
        api_response = api_instance.accounts_users_partial_update(account, user, data)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_users_partial_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **user** | **str**|  | 
 **data** | [**AccountUser**](AccountUser.md)|  | 

### Return type

[**AccountUser**](AccountUser.md)

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

# **accounts_users_read**
> AccountUser accounts_users_read(account, user)

A view set for account users.

Provides basic CRUD views for account users.

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    user = 'user_example' # str | 
    try:
        api_response = api_instance.accounts_users_read(account, user)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_users_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **user** | **str**|  | 

### Return type

[**AccountUser**](AccountUser.md)

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

# **accounts_workers_heartbeats_list**
> InlineResponse2005 accounts_workers_heartbeats_list(account, worker, limit=limit, offset=offset)

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    worker = 'worker_example' # str | 
    limit = 56 # int | Number of results to return per page. (optional)
    offset = 56 # int | The initial index from which to return the results. (optional)
    try:
        api_response = api_instance.accounts_workers_heartbeats_list(account, worker, limit=limit, offset=offset)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_workers_heartbeats_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **worker** | **str**|  | 
 **limit** | **int**| Number of results to return per page. | [optional] 
 **offset** | **int**| The initial index from which to return the results. | [optional] 

### Return type

[**InlineResponse2005**](InlineResponse2005.md)

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

# **accounts_workers_list**
> InlineResponse2004 accounts_workers_list(account, limit=limit, offset=offset)

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    limit = 56 # int | Number of results to return per page. (optional)
    offset = 56 # int | The initial index from which to return the results. (optional)
    try:
        api_response = api_instance.accounts_workers_list(account, limit=limit, offset=offset)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_workers_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **limit** | **int**| Number of results to return per page. | [optional] 
 **offset** | **int**| The initial index from which to return the results. | [optional] 

### Return type

[**InlineResponse2004**](InlineResponse2004.md)

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

# **accounts_workers_read**
> Worker accounts_workers_read(account, worker)

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    worker = 'worker_example' # str | 
    try:
        api_response = api_instance.accounts_workers_read(account, worker)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_workers_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **worker** | **str**|  | 

### Return type

[**Worker**](Worker.md)

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

# **accounts_zones_create**
> accounts_zones_create(account)

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    try:
        api_instance.accounts_zones_create(account)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_zones_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 

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

# **accounts_zones_delete**
> accounts_zones_delete(account, zone)

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    zone = 'zone_example' # str | 
    try:
        api_instance.accounts_zones_delete(account, zone)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_zones_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **zone** | **str**|  | 

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

# **accounts_zones_list**
> InlineResponse2006 accounts_zones_list(account, limit=limit, offset=offset)

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    limit = 56 # int | Number of results to return per page. (optional)
    offset = 56 # int | The initial index from which to return the results. (optional)
    try:
        api_response = api_instance.accounts_zones_list(account, limit=limit, offset=offset)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_zones_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **limit** | **int**| Number of results to return per page. | [optional] 
 **offset** | **int**| The initial index from which to return the results. | [optional] 

### Return type

[**InlineResponse2006**](InlineResponse2006.md)

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

# **accounts_zones_read**
> Zone accounts_zones_read(account, zone)

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
    api_instance = stencila.hub.AccountsApi(api_client)
    account = 'account_example' # str | 
    zone = 'zone_example' # str | 
    try:
        api_response = api_instance.accounts_zones_read(account, zone)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountsApi.accounts_zones_read: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | **str**|  | 
 **zone** | **str**|  | 

### Return type

[**Zone**](Zone.md)

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

