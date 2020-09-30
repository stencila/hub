# WorkerHeartbeat

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**time** | **datetime** | The time of the heartbeat. | 
**clock** | **int** | The tick number of the worker&#39;s monotonic clock | 
**active** | **int** | The number of active jobs on the worker. | 
**processed** | **int** | The number of jobs that have been processed by the worker. | 
**load** | **str** | An array of the system load over the last 1, 5 and 15 minutes. From os.getloadavg(). | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


