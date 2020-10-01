/**
 * Setup script run before tests
 * 
 * Polly fills `fetch` if it is not available
 */

import fetch from 'node-fetch'

if (!globalThis.fetch) {
  globalThis.fetch = fetch;
}
