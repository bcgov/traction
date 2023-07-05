import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, test, vi } from 'vitest';

import { useAcapyApi } from '@/store/acapyApi';
import {
  restHandlersAuthorizationError,
  restHandlersUnknownError,
  server,
} from '../setupApi';

import { acapyResponse } from '../__mocks__/api/responses';
import { store as tenantStore } from '../__mocks__/store/tenant';
import { store as tokenStore } from '../__mocks__/store/token';

tokenStore.clearToken = vi.fn();
tokenStore.setToken = 'token';
tenantStore.clearTenant = vi.fn();

let store: any;

describe('acapyApi', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useAcapyApi();
  });

  describe('Successful API calls', () => {
    test('get success returns expected value', async () => {
      const response = await store.getHttp('');
      expect(response.data).toEqual(acapyResponse.basic);
    });

    test('post success returns expected value', async () => {
      const response = await store.postHttp('');
      expect(response.data).toEqual(acapyResponse.basic);
    });

    test('update success returns expected value', async () => {
      const response = await store.updateHttp('');
      expect(response.data).toEqual(acapyResponse.basic);
    });

    test('put success returns expected value', async () => {
      const response = await store.putHttp('');
      expect(response.data).toEqual(acapyResponse.basic);
    });

    test('patch success returns expected value', async () => {
      const response = await store.patchHttp('');
      expect(response.data).toEqual(acapyResponse.basic);
    });

    test('delete success returns expected value', async () => {
      const response = await store.deleteHttp('');
      expect(response.data).toEqual(acapyResponse.basic);
    });
  });

  describe('Unauthorized API calls', () => {
    beforeEach(async () => {
      server.use(...restHandlersAuthorizationError);
    });

    test('get authorization failure clears token and tenant', async () => {
      const clearTokenSpy = vi.spyOn(tokenStore, 'clearToken');
      const clearTenantSpy = vi.spyOn(tenantStore, 'clearTenant');

      await expect(store.getHttp('')).rejects.toThrow();

      expect(clearTokenSpy).toHaveBeenCalled();
      expect(clearTenantSpy).toHaveBeenCalled();
    });

    test('get failure with Authorization override', async () => {
      try {
        await store.getHttp('', undefined, {
          headers: {
            Authorization: 'Bearer token-override',
          },
        });
      } catch (e) {
        expect(e).toContain('Unauthorized');
        expect(e).toContain('token-override');
      }
    });
  });

  describe('Unknown error API calls', () => {
    beforeEach(async () => {
      server.use(...restHandlersUnknownError);
    });

    test('get failure returns expected value', async () => {
      await expect(store.getHttp('')).rejects.toThrow();
    });
  });
});
