# Worker

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] [readonly] 
**active** | **bool** |  | [optional] [readonly] 
**created** | **datetime** | The time that the worker started (time of the first event for the worker). | [optional] [readonly] 
**started** | **datetime** | The time that the worker started (only recorded on a &#39;worker-online&#39; event). | [optional] 
**updated** | **datetime** | The time that the last heatbeat was received for the worker. | [optional] 
**finished** | **datetime** | The time that the worker finished (only recorded on a &#39;worker-offline&#39; event) | [optional] 
**hostname** | **str** | The &#x60;hostname&#x60; of the worker. | 
**utcoffset** | **int** | The &#x60;utcoffset&#x60; of the worker. | [optional] 
**pid** | **int** | The &#x60;pid&#x60; of the worker. | [optional] 
**freq** | **float** | The worker&#39;s heatbeat frequency (in seconds) | [optional] 
**software** | **str** | The name and version of the worker&#39;s software. | [optional] 
**os** | **str** | Operating system that the worker is running on. | [optional] 
**details** | **str** | Details about the worker including queues and statsSee https://docs.celeryproject.org/en/stable/userguide/workers.html#statistics | [optional] 
**signature** | **str** | The signature of the worker used to identify it. It is possible, but unlikely, that two or more active workers have the same signature. | [optional] 
**queues** | **list[int]** | The queues that this worker is listening to. | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


