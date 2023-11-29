import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, test } from 'vitest';

import { useIssuerStore } from '@/store/issuerStore';
import { restHandlersUnknownError, server } from '../setupApi';
import { testSuccessResponse, testErrorResponse } from '../../test/commonTests';

let store: any;

describe('connectionStore', () => {
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
    test('listCredentials does not throw error and sets loading correctly', async () => {
      await testSuccessResponse(store, store.listCredentials(), 'loading');
    });

    test('offerCredential does not throw error and sets loading correctly', async () => {
      await testSuccessResponse(store, store.offerCredential(), 'loading');
    });

    test('getCredential does not throw error and sets loading correctly', async () => {
      const response = await store.getCredential('test-id');

      expect(response).not.toBeNull();
      expect(store.error).toBeNull();
    });

    test('revokeCredential does not throw error and sets loading correctly', async () => {
      await testSuccessResponse(store, store.revokeCredential(), 'loading');
    });

    test('deleteCredentialExchange does not throw error and sets loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.deleteCredentialExchange('test-id'),
        'loading'
      );
    });
  });

  describe.skip('Unsuccessful API calls', async () => {
    beforeEach(() => {
      server.use(...restHandlersUnknownError);
    });

    test('listCredentials throws error and sets loading correctly', async () => {
      await testErrorResponse(store, store.listCredentials(), 'loading');
    });

    test('offerCredential throws error and sets loading correctly', async () => {
      await testErrorResponse(store, store.offerCredential(), 'loading');
    });

    test('getCredential does not throw error and sets loading correctly', async () => {
      await expect(store.getCredential('test-id')).rejects.toThrow();
      expect(store.error).not.toBeNull();
    });

    test('revokeCredential throws error and sets loading correctly', async () => {
      await testErrorResponse(store, store.revokeCredential(), 'loading');
    });

    test('deleteCredentialExchange throws error and sets loading correctly', async () => {
      await testErrorResponse(
        store,
        store.deleteCredentialExchange('test-id'),
        'loading'
      );
    });
  });
});
