import { ProjectsApi } from '../src/apis/ProjectsApi'
import { SourcePolymorphic, SourcePolymorphicTypeEnum } from '../src/models/SourcePolymorphic';
import { configAnon, configMember } from './config'

test('List as anonymous user', async () => {
  const api = new ProjectsApi(configAnon())
  
  const listAll = await api.projectsList({})
  expect(listAll.count).toBeGreaterThan(0)
  
  // Filtering to only public should return the same number
  const listPublic = await api.projectsList({
    _public: true
  })
  expect(listPublic.count).toEqual(listAll.count)
})

test('List as member user', async () => {
  const api = new ProjectsApi(await configMember())
  
  const listAll = await api.projectsList({})
  expect(listAll.count).toBeGreaterThan(0)
  
  // Filtering by only public should return fewer
  const listPublic = await api.projectsList({
    _public: true
  })
  expect(listPublic.count).toBeLessThan(listAll.count)

  // Filtering by role should return fewer
  const listRole = await api.projectsList({
    role: 'owner'
  })
  expect(listRole.count).toBeLessThan(listAll.count)
})

test('Create a source', async () => {
  const api = new ProjectsApi(await configMember())
  
  const dataIn: SourcePolymorphic = {
    type: SourcePolymorphicTypeEnum.GoogleDocsSource,
    path: "my.gdoc",
    docId: "1BW6MubIyDirCGW9Wq-" + Math.random().toString(36).slice(2)
  }
  const source = await api.projectsSourcesCreate({
    project: "1",
    data: dataIn
  })

  const dataOut = await api.projectsSourcesRead({
    project: "1",
    source: source.id
  })
  expect(dataOut.type).toBe(dataOut.type)
  expect(dataOut.path).toBe(dataOut.path)
  expect(dataOut.docId).toBe(dataOut.docId)
})

