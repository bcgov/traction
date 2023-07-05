import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, test } from 'vitest';

import { useHolderStore } from '@/store/holderStore';

let store: any;

describe('holderStore', () => {
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

  describe('Successful API calls', () => {
    test.todo('acceptCredentialOffer');
    test.todo('deleteCredentialExchange');
    test.todo('getCredential');
    test.todo('getCredentialOca');
    test.todo('getPresentation');
    test.todo('listCredentials');
    test.todo('listHolderCredentialExchanges');
    test.todo('listOcas');
    test.todo('listPresentations');
    test.todo('rejectCredentialOffer');
  });

  describe('Unuccessful API calls', () => {
    test.todo('acceptCredentialOffer');
    test.todo('deleteCredentialExchange');
    test.todo('getCredential');
    test.todo('getCredentialOca');
    test.todo('getPresentation');
    test.todo('listCredentials');
    test.todo('listHolderCredentialExchanges');
    test.todo('listOcas');
    test.todo('listPresentations');
    test.todo('rejectCredentialOffer');
  });
});
