import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, test } from 'vitest';

import { useHolderStore } from '@/store/holderStore';
import { testErrorResponse, testSuccessResponse } from '../../test/commonTests';
import { restHandlersUnknownError, server } from '../setupApi';

let store: any;

describe('connectionStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useHolderStore();
  });

  test("initial values haven't changed from expected", () => {
    expect(store.credentials).toEqual([]);
    expect(store.credentialExchanges).toEqual([]);
    expect(store.selectedCredential).toBeNull();
    expect(store.ocas).toEqual([]);
    expect(store.loadingOca).toEqual(false);
    expect(store.presentations).toBeNull();
    expect(store.selectedPresentation).toBeNull();
    expect(store.loading).toEqual(false);
    expect(store.error).toBeNull();
  });

  describe('Success API calls', async () => {
    test('acceptCredentialOffer does not throw exception and sets loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.acceptCredentialOffer('test-id'),
        'loading'
      );
    });

    test('deleteCredentialExchange does not throw exception and sets loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.deleteCredentialExchange('test-id'),
        'loading'
      );
    });

    // TODO: This doesn't seem to be used anywhere
    test.todo('getCredential');
    // TODO: This doesn't seem to be used anywhere
    test.todo('getCredentialOca');
    // TODO: This doesn't seem to be used anywhere
    test.todo('getPresentation');

    test('listCredentials gets a response', async () => {
      const response = await store.listCredentials();
      expect(response).toBeDefined();
    });

    test.todo('listHolderCredentialExchanges');
    test.todo('listOcas');
    test.todo('listPresentations');
    test.todo('rejectCredentialOffer');
  });

  describe('Unsuccessful API calls', async () => {
    beforeEach(() => {
      server.use(...restHandlersUnknownError);
    });

    test('acceptCredentialOffer does not throw exception and sets loading correctly', async () => {
      await testErrorResponse(
        store,
        store.acceptCredentialOffer('test-id'),
        'loading'
      );
    });

    test('deleteCredentialExchange does not throw exception and sets loading correctly', async () => {
      await testErrorResponse(
        store,
        store.deleteCredentialExchange('test-id'),
        'loading'
      );
    });

    test('listCredentials throws an error', async () => {
      await expect(store.listCredentials()).rejects.toThrow();
    });

    test.todo('listHolderCredentialExchanges');
    test.todo('listOcas');
    test.todo('listPresentations');
    test.todo('rejectCredentialOffer');
  });
});
