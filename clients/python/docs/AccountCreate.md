# AccountCreate

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] [readonly] 
**name** | **str** | Name of the account. Lowercase and no spaces or leading numbers. Will be used in URLS e.g. https://hub.stenci.la/awesome-org | 
**user** | **int** | The user for this account. Only applies to personal accounts. | [optional] 
**created** | **datetime** | The time the account was created. | [optional] [readonly] 
**display_name** | **str** | Name to display in account profile. | [optional] 
**location** | **str** | Location to display in account profile. | [optional] 
**image** | **str** | Image for the account. | [optional] [readonly] 
**website** | **str** | URL to display in account profile. | [optional] 
**email** | **str** | An email to display in account profile. Will not be used by Stencila to contact you. | [optional] 
**theme** | **str** | The default theme for the account. | [optional] 
**extra_head** | **str** | Content to inject into the &lt;head&gt; element of HTML served for this account. | [optional] 
**extra_top** | **str** | Content to inject at the top of the &lt;body&gt; element of HTML served for this account. | [optional] 
**extra_bottom** | **str** | Content to inject at the bottom of the &lt;body&gt; element of HTML served for this account. | [optional] 
**hosts** | **str** | A space separated list of valid hosts for the account. Used for setting Content Security Policy headers when serving content for this account. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


