# Invite

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] [readonly] 
**url** | **str** |  | [optional] [readonly] 
**key** | **str** | The key for the invite. | [optional] [readonly] 
**email** | **str** | The email address of the person you are inviting. | 
**message** | **str** | An optional message to send to the invitee. | [optional] 
**created** | **datetime** | When the invite was created. | [optional] [readonly] 
**sent** | **datetime** | When the invite was sent. | [optional] 
**accepted** | **bool** | Whether the invite has been accepted. Will only be true if the user has clicked on the invitation AND authenticated. | [optional] 
**completed** | **datetime** | When the invite action was completed | [optional] 
**action** | **str** | The action to perform when the invitee signs up. | [optional] 
**subject_id** | **int** | The id of the target of the action. | [optional] 
**arguments** | **str** | Any additional arguments to pass to the action. | [optional] 
**inviter** | **int** | The user who created the invite. | [optional] 
**subject_type** | **int** | The type of the target of the action. e.g Team, Account | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


