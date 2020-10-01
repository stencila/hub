import { TokensApi } from '../src/apis/TokensApi'
import { configAnon, configTokened } from './config'

test('CR(U)D', async () => {
  const api = new TokensApi(configAnon())
  
  // Create a token, by supplying username / password
  const createResponse = await api.tokensCreate({
    data: {
      username: 'a-user',
      password: 'a-user'
    }
  })
  const {username, token, user, created, expiry} = createResponse
  expect(username).toBe('a-user')
  expect(token).not.toBeFalsy()

  // Reading a token returns its details AND refreshes it
  const readResponse = await api.tokensRead({
    token
  })
  expect(readResponse.user).toBe(user)
  expect(readResponse.created).toEqual(created)
  expect(readResponse.expiry.valueOf()).toBeGreaterThan(expiry.valueOf())

  // Listing tokens requires an authenticated request
  const apiAuthenticated = new TokensApi(configTokened(token))
  const listResponse = await apiAuthenticated.tokensList({
    limit: 10
  })
  expect(listResponse.count).toBeGreaterThan(0)

  // Deleting token can be done without authentication
  const deleteResponse = await api.tokensDelete({
    token
  })
  expect(deleteResponse).toBeFalsy()

})
