# InlineObject3

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | An autoincrementing integer to allow selecting jobs in the order they were created. | [optional] [readonly] 
**status_message** | **str** |  | [optional] [readonly] 
**summary_string** | **str** |  | [optional] [readonly] 
**runtime_formatted** | **str** |  | [optional] [readonly] 
**url** | **str** |  | [optional] [readonly] 
**position** | **int** |  | [optional] [readonly] 
**children** | **list[int]** |  | [optional] [readonly] 
**key** | **str** | A unique, and very difficult to guess, key to access the job with. | [optional] 
**description** | **str** | A short description of the job. | [optional] 
**created** | **datetime** | The time the job was created. | [optional] [readonly] 
**updated** | **datetime** | The time the job was last updated. | [optional] [readonly] 
**began** | **datetime** | The time the job began. | [optional] 
**ended** | **datetime** | The time the job ended. | [optional] 
**status** | **str** | The current status of the job. | [optional] 
**is_active** | **bool** | Is the job active? | [optional] 
**method** | **str** | The job method. | [optional] [readonly] 
**params** | **str** | The parameters of the job; a JSON object. | [optional] [readonly] 
**result** | **str** | The result of the job; a JSON value. | [optional] 
**error** | **str** | Any error associated with the job; a JSON object with type, message etc. | [optional] 
**log** | **str** | The job log; a JSON array of log objects, including any errors. | [optional] 
**runtime** | **float** | The running time of the job. | [optional] 
**worker** | **str** | The identifier of the worker that ran the job. | [optional] 
**retries** | **int** | The number of retries to fulfil the job. | [optional] 
**callback_id** | **str** | The id of the object to call back. | [optional] 
**callback_method** | **str** | The name of the method to call back. | [optional] 
**project** | **int** | The project this job is associated with. | [optional] 
**snapshot** | **str** | The snapshot that this job is associated with. Usually &#x60;session&#x60; jobs for the snapshot. | [optional] 
**creator** | **int** | The user who created the job. | [optional] [readonly] 
**queue** | **int** | The queue that this job was routed to | [optional] [readonly] 
**parent** | **int** | The parent job | [optional] 
**callback_type** | **int** | The type of the object to call back. | [optional] 
**users** | **list[int]** | Users who have created or connected to the job; not necessarily currently connected. | [optional] 
**anon_users** | **list[str]** | Anonymous users who have created or connected to the job. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


