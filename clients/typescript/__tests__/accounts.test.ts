import { AccountsApi, AccountsListRoleEnum, AccountsListIsEnum } from '../src/apis/AccountsApi'
import { configAnon, configMember } from './config'

test('List as anonymous user', async () => {
  const api = new AccountsApi(configAnon())
  
  const listAll = await api.accountsList({})
  expect(listAll.count).toBeGreaterThan(0)

  // Filtering by account type should return fewer
  const listOrgs = await api.accountsList({
    is: AccountsListIsEnum.Org
  })
  expect(listOrgs.count).toBeLessThan(listAll.count)

  const listUsers = await api.accountsList({
    is: AccountsListIsEnum.User
  })
  expect(listUsers.count).toBeLessThan(listAll.count)
  expect(listUsers.count).not.toEqual(listOrgs.count)
  
  // Filtering by role has no effect
  const listOwner = await api.accountsList({
    role: AccountsListRoleEnum.Owner
  })
  expect(listOwner.count).toEqual(listAll.count)
})

test('List as member user', async () => {
  const api = new AccountsApi(await configMember())
  
  const listAll = await api.accountsList({})
  expect(listAll.count).toBeGreaterThan(0)
  
  // Filtering by role should return fewer
  const listRole = await api.accountsList({
    role: AccountsListRoleEnum.Member
  })
  expect(listRole.count).toBeLessThan(listAll.count)
})
