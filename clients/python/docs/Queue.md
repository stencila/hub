# Queue

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] [readonly] 
**name** | **str** | The name of the queue. | 
**priority** | **int** | The relative priority of jobs placed on the queue. | [optional] 
**untrusted** | **bool** | Whether or not the queue should be sent jobs which run untrusted code. | [optional] 
**interrupt** | **bool** | Whether or not the queue should be sent jobs which can not be interupted.False (default): jobs should not be interrupted | [optional] 
**zone** | **int** | The zone this job is associated with. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


