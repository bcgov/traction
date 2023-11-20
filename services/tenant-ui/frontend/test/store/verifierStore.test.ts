import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, test } from 'vitest';

import { useVerifierStore } from '@/store/verifierStore';
import { testErrorResponse, testSuccessResponse } from '../../test/commonTests';
import { restHandlersUnknownError, server } from '../setupApi';

let store: any;

describe('verifierStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useVerifierStore();
  });

  test("initial values haven't changed from expected", () => {
    expect(store.presentations).toBeNull();
    expect(store.selectedPresentation).toBeNull();
    expect(store.loading).toEqual(false);
    expect(store.error).toBeNull();
  });

  describe('Successful API calls', () => {
    test('listPresentations sets presentations', async () => {
      await store.listPresentations();
      expect(store.presentations).toHaveLength(1);
      expect(store.selectedPresentation).toBeNull();
    });

    test('deleteRecord does not throw error and sets loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.deleteRecord('test-uuid'),
        'loading'
      );
    });

    test('sendPresentationRequest does not throw error and sets loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.sendPresentationRequest('test-uuid'),
        'loading'
      );
    });
  });

  describe.skip('Unsuccessful API calls', () => {
    beforeEach(() => {
      server.use(...restHandlersUnknownError);
    });

    test('listPresentations handles error correctly', async () => {
      await expect(store.listPresentations).rejects.toThrow();
    });

    test('deleteRecord handles error correctly', async () => {
      await testErrorResponse(
        store,
        store.deleteRecord('test-uuid'),
        'loading'
      );
    });

    test('sendPresentationRequest handles error correctly', async () => {
      await testErrorResponse(
        store,
        store.sendPresentationRequest('test-uuid'),
        'loading'
      );
    });
  });
});
