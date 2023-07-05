import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, test } from 'vitest';

import { useVerifierStore } from '@/store/verifierStore';

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
      expect(store.presentations).not.toBeNull();
      expect(store.presentations).toHaveLength(1);
      expect(store.selectedPresentation).toBeNull();
    });

    // TODO: currently using legacy api
    test.todo('getPresentation');

    test.todo('deleteRecord');
    test.todo('sendPresentationRequest');
  });

  describe('Unsuccessful API calls', () => {
    test.todo('listPresentations');
    test.todo('getPresentation');
    test.todo('deleteRecord');
    test.todo('sendPresentationRequest');
  });
});
