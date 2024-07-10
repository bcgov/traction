import { createPinia, setActivePinia } from 'pinia';
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';

import { useTenantStore } from '@/store/tenantStore';
import { testErrorResponse, testSuccessResponse } from '../../test/commonTests';
import { restHandlersUnknownError, server } from '../setupApi';

import { tokenStore } from '../../test/__mocks__/store';

vi.mock('global.localStorage', () => ({
  getItem: vi.fn(),
  setItem: vi.fn(),
}));

const setLocalStorageSpy = vi.spyOn(Storage.prototype, 'setItem');
const removeLocalStorageSpy = vi.spyOn(Storage.prototype, 'removeItem');

let store: any;

describe('tenantStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useTenantStore();
  });

  afterEach(() => {
    setLocalStorageSpy.mockClear();
    removeLocalStorageSpy.mockClear();
    localStorage.clear();
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

  test('tenantReady is false when token is null', () => {
    tokenStore.token.value = null;
    expect(store.tenantReady).toEqual(false);
  });

  test('tenantReady is false when token is null', () => {
    tokenStore.token.value = 'token';
    expect(store.tenantReady).toEqual(true);
  });

  test('isIssuer is true when endorderConnection active and has did and TAA not required', () => {
    store.endorserConnection = {
      state: 'active',
    };
    store.publicDid = {
      did: 'did',
    };
    store.taa = {
      taa_required: false,
    };
    expect(store.isIssuer).toBeTruthy();
    expect(store.isIssuer).toEqual(true);
  });

  test('isIssuer is true when endorderConnection active and has did and TAA accepted', () => {
    store.endorserConnection = {
      state: 'active',
    };
    store.publicDid = {
      did: 'did',
    };
    store.taa = {
      taa_required: true,
      taa_accepted: true,
    };
    expect(store.isIssuer).toBeTruthy();
    expect(store.isIssuer).toEqual(true);
  });

  test('isIssuer is false when the TAA is not accepted ', () => {
    store.endorserConnection = {
      state: 'active',
    };
    store.publicDid = {
      did: 'did',
    };
    store.taa = {
      taa_required: true,
      taa_accepted: false,
    };
    expect(store.isIssuer).toBeFalsy();
  });

  test('isIssuer is false when the taa_accepted is not there ', () => {
    store.endorserConnection = {
      state: 'active',
    };
    store.publicDid = {
      did: 'did',
    };
    store.taa = {
      taa_required: true,
    };
    expect(store.isIssuer).toBeFalsy();
  });

  test('isIssuer is falsy when endorserConnection is not-active', () => {
    store.endorserConnection = {
      state: 'not-active',
    };
    expect(store.isIssuer).toBeFalsy();
  });

  test('isIssuer is falsy when endorserConnection is null', () => {
    store.endorserConnection = null;
    expect(store.isIssuer).toBeFalsy();
  });

  test('isIssuer is falsy when publicDid is null', () => {
    store.publicDid = null;
    expect(store.isIssuer).toBeFalsy();
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

    test.skip('getIssuanceStatus sets taa, endorser info/connection and public did and loading properly', async () => {
      const response = store.getIssuanceStatus();
      testSuccessResponse(store, response, 'loadingIssuance');
      await response;

      expect(store.taa).not.toBeNull();
      expect(store.endorserInfo).not.toBeNull();
      expect(store.endorserConnection).not.toBeNull();
      expect(store.publicDid).not.toBeNull();
    });

    test.skip('connectToEndorser sets endorser connection and loadingIssuance and loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.connectToEndorser(),
        'loadingIssuance'
      );
      expect(store.endorserConnection).not.toBeNull();
    });

    test('connectToEndorser sets endorser connection and loadingIssuance and loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.connectToEndorser(),
        'loadingIssuance'
      );
      expect(store.endorserConnection).not.toBeNull();
    });

    test('getTenantSubWallet sets wallet and loading correctly', async () => {
      await testSuccessResponse(store, store.getTenantSubWallet(), 'loading');
      expect(store.tenantWallet).not.toBeNull();
    });

    test('updateTenantSubWallet sets wallet and loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.updateTenantSubWallet(),
        'loading'
      );
    });
    test('updateTenantContact sets wallet and loading correctly', async () => {
      await testSuccessResponse(store, store.updateTenantContact(), 'loading');
    });
  });

  describe('Failed API calls', () => {
    beforeEach(() => {
      server.use(...restHandlersUnknownError);
    });

    test('getSelf handles error correctly and does not change tenant', async () => {
      store.tenant = null;
      await expect(store.getSelf()).rejects.toThrow();
      expect(store.tenant).toBeNull();
    });

    test('getTenantConfig handles error correctly and does not change tenantConfig', async () => {
      store.tenantConfig = null;
      await expect(store.getTenantConfig()).rejects.toThrow();
      expect(store.tenantConfig).toBeNull();
    });

    test.skip('getIssuanceStatus handles error correctly and does not change issuanceStatus', async () => {
      await expect(store.getIssuanceStatus()).rejects.toThrow();
    });

    test('getEndorserConnection handles error correctly and set connection to null', async () => {
      store.endorserConnection = 'connection';
      await expect(store.getEndorserConnection()).rejects.toThrow();
      expect(store.error).not.toBeNull();
      store.endorserConnection = null;
    });

    test('getEndorserInfo handles error correctly and set info to null', async () => {
      store.endorserInfo = 'info';
      await testErrorResponse(
        store,
        store.getEndorserInfo(),
        'loadingIssuance'
      );
      store.endorserInfo = null;
    });

    test('getPublicDid handles error correctly and does not change publicDid', async () => {
      store.publicDid = null;
      await expect(store.getPublicDid()).rejects.toThrow();
      expect(store.publicDid).toBeNull();
    });

    test('getTenantSubWallet handles error correctly', async () => {
      await testErrorResponse(store, store.getTenantSubWallet(), 'loading');
    });

    test('getTaa handles error correctly and does not change taa', async () => {
      store.taa = null;
      await expect(store.getTaa()).rejects.toThrow();
      expect(store.taa).toBeNull();
    });

    test.skip('acceptTaa handles error correctly', async () => {
      await testErrorResponse(store, store.acceptTaa(), 'loadingIssuance');
    });

    test('updateTenantSubWallet handles error correctly', async () => {
      await testErrorResponse(store, store.updateTenantSubWallet(), 'loading');
    });
    test('updateTenantContact handles error correctly', async () => {
      await testErrorResponse(store, store.updateTenantContact(), 'loading');
    });
  });
});
