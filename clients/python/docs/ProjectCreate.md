# ProjectCreate

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] [readonly] 
**account** | **int** | Account that the project belongs to. | [optional] 
**created** | **datetime** | The time the project was created. | [optional] [readonly] 
**name** | **str** | Name of the project. Lowercase only and unique for the account. Will be used in URLS e.g. https://hub.stenci.la/awesome-org/great-project. | [optional] 
**title** | **str** | Title of the project to display in its profile. | [optional] 
**description** | **str** | Brief description of the project. | [optional] 
**temporary** | **bool** | Is the project temporary? | [optional] 
**public** | **bool** | Is the project publicly visible? | [optional] 
**key** | **str** | A unique, and very difficult to guess, key to access this project if it is not public. | [optional] 
**main** | **str** | Path of the main file of the project | [optional] 
**theme** | **str** | The name of the theme to use as the default when generating content for this project. | [optional] 
**extra_head** | **str** | Content to inject into the &lt;head&gt; element of HTML served for this project. | [optional] 
**extra_top** | **str** | Content to inject at the top of the &lt;body&gt; element of HTML served for this project. | [optional] 
**extra_bottom** | **str** | Content to inject at the bottom of the &lt;body&gt; element of HTML served for this project. | [optional] 
**liveness** | **str** | Where to serve the content for this project from. | [optional] 
**pinned** | **str** | If pinned, the snapshot to pin to, when serving content. | [optional] [readonly] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


