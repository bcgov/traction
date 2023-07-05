import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, test } from 'vitest';

import { useIssuerStore } from '@/store/issuerStore';

let store: any;

describe('issuerStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useIssuerStore();
  });

  test("initial values haven't changed from expected", () => {
    expect(store.credentials).toEqual([]);
    expect(store.selectedCredential).toBeNull();
    expect(store.loading).toEqual(false);
    expect(store.error).toBeNull();
  });

  describe('Successful API calls', () => {
    // TODO: Test with non empty response
    test('listCredentials does not throw error and sets loading correctly', async () => {
      let response = store.listCredentials();
      expect(store.loading).toEqual(true);
      response = await response;

      expect(response.result).not.toBeNull();
      expect(store.loading).toEqual(false);
      expect(store.error).toBeNull();
    });

    test.todo('offerCredential');
    test.todo('getCredential');
    test.todo('revokeCredential');
    test.todo('deleteCredentialExchange');
  });

  describe('Unsuccessful API calls', () => {
    test.todo('listCredentials');
    test.todo('offerCredential');
    test.todo('getCredential');
    test.todo('revokeCredential');
    test.todo('deleteCredentialExchange');
  });
});
