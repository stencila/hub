/**
 * API configuration
 * 
 * Use the exported `config` when constructing API instances
 * in tests. e.g. `new AccountsApi(config)`.
 * 
 * Assumes a locally running dev server.
 */

import { Configuration } from '../src/runtime'
import { TokensApi } from '../src/apis/TokensApi'

const basePath = 'http://127.0.0.1:8000/api'

/**
 * Create a configuration for an anonymous user.
 */
export function configAnon() {
  return new Configuration({
    basePath
  })
}

/**
 * Create a configuration that uses an API token for authentication.
 */
export function configTokened(token: string) {
  return new Configuration({
    basePath,
    apiKey: `Token ${token}`
  })
}

/**
 * Create a configuration for the `member` user.
 */
export async function configMember() {
  const api = new TokensApi(configAnon())
  const {token} = await api.tokensCreate({
    data: {
      username: 'member',
      password: 'member'
    }
  })
  return configTokened(token)
}
