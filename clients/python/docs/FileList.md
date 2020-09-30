# FileList

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] [readonly] 
**name** | **str** |  | [optional] [readonly] 
**is_directory** | **bool** |  | [optional] [readonly] 
**count** | **int** |  | [optional] [readonly] 
**source** | **str** |  | [optional] [readonly] 
**path** | **str** | The path of the file within the project. | 
**current** | **bool** | Is the file currently in the project? Used to retain a history for file paths within a project. | [optional] 
**created** | **datetime** | The time the file info was created. | [optional] [readonly] 
**updated** | **datetime** | The time the file info was updated. This field will have the last time this row was altered (i.e. changed from current, to not). | [optional] 
**modified** | **datetime** | The file modification time. | [optional] 
**size** | **int** | The size of the file in bytes | [optional] 
**mimetype** | **str** | The mimetype of the file. | [optional] 
**encoding** | **str** | The encoding of the file e.g. gzip | [optional] 
**fingerprint** | **str** | The fingerprint of the file | [optional] 
**job** | **int** | The job that created the file e.g. a source pull or file conversion. | [optional] 
**snapshot** | **str** | The snapshot that the file belongs. If the snapshot is deleted so will the files. | [optional] 
**upstreams** | **list[int]** | The files that this file was derived from (if any). | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


