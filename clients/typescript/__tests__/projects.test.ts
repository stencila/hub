import { ProjectsApi } from '../src/apis/ProjectsApi'
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
