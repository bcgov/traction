import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, test, vi } from 'vitest';

import { useTenantStore } from '@/store/tenantStore';

import { store as tokenStore } from '../__mocks__/store/token';

vi.mock('@/store/tokenStore', () => ({
  useTokenStore: vi.fn(() => tokenStore),
}));

let store: any;

describe('tenantStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useTenantStore();
  });

  test("initial values haven't changed from expected", () => {
    expect(store.tenant).toBeNull();
    expect(store.loading).toEqual(false);
    expect(store.loadingIssuance).toEqual(false);
    expect(store.error).toBeNull();
    expect(store.endorserConnection).toBeNull();
    expect(store.endorserInfo).toBeNull();
    expect(store.publicDid).toBeNull();
    expect(store.publicDidRegistrationProgress).toBe('');
    expect(store.taa).toBeNull();
    expect(store.tenantConfig).toBeNull();
    expect(store.tenantWallet).toBeNull();
  });

  describe('Successful API calls', () => {
    test('getSelf sets tenant', async () => {
      await store.getSelf();
      expect(store.tenant).not.toBeNull();
    });

    test('getTenantConfig sets tenantConfig', async () => {
      await store.getTenantConfig();
      expect(store.tenantConfig).not.toBeNull();
    });

    test('getTaa sets taa', async () => {
      await store.getTaa();
      expect(store.taa).not.toBeNull();
    });

    test('getEndorserInfo sets endorser info', async () => {
      await store.getEndorserInfo();
      expect(store.endorserInfo).not.toBeNull();
    });

    test('getEndorserConnection sets endorser connection', async () => {
      await store.getEndorserConnection();
      expect(store.endorserConnection).not.toBeNull();
    });

    test('getPublicDid sets public did', async () => {
      await store.getPublicDid();
      expect(store.publicDid).not.toBeNull();
    });

    test('clearTenant set tenant to null', async () => {
      store.tenant = 'something';
      store.clearTenant();
      expect(store.tenant).toBeNull();
    });

    test('getIssuanceStatus sets taa, endorser info/connection and public did and loading properly', async () => {
      const response = store.getIssuanceStatus();
      expect(store.loadingIssuance).toEqual(true);
      await response;

      expect(store.taa).not.toBeNull();
      expect(store.endorserInfo).not.toBeNull();
      expect(store.endorserConnection).not.toBeNull();
      expect(store.publicDid).not.toBeNull();

      expect(store.loadingIssuance).toEqual(false);
    });

    test('connectToEndorser sets endorser connection and loadingIssuance and loading correctly', async () => {
      const response = store.connectToEndorser();
      expect(store.loadingIssuance).toEqual(true);
      await response;

      expect(store.endorserConnection).not.toBeNull();
      expect(store.loadingIssuance).toEqual(false);
    });

    test('getTenantSubWallet sets wallet and loading correctly', async () => {
      const response = store.getTenantSubWallet();
      expect(store.loading).toEqual(true);
      await response;

      expect(store.tenantWallet).not.toBeNull();
      expect(store.loading).toEqual(false);
    });

    test.todo('updateTenantSubWallet');
  });

  describe('Failed API calls', () => {
    test.todo('acceptTaa');
    test.todo('clearTenant');
    test.todo('connectToEndorser');
    test.todo('getEndorserConnection');
    test.todo('getEndorserInfo');
    test.todo('getIssuanceStatus');
    test.todo('getPublicDid');
    test.todo('getSelf');
    test.todo('getTaa');
    test.todo('getTenantConfig');
    test.todo('getTenantSubWallet');
    test.todo('registerPublicDid');
    test.todo('updateTenantSubWallet');
  });
});
