import { createPinia, setActivePinia } from 'pinia';
import { afterAll, beforeEach, describe, expect, test } from 'vitest';

import { useConfigStore } from '@/store/configStore';
import { testErrorResponse, testSuccessResponse } from '../../test/commonTests';
import { restHandlersUnknownError, server } from '../setupApi';

import { configResponse } from '../__mocks__/api/responses';

let store: any;

describe('configStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useConfigStore();
  });

  afterAll(() => {
    configResponse.setTenantProxyUrl('http://localhost:8080');
  });

  describe('Successful API calls', () => {
    test("initial values haven't changed from expected", () => {
      expect(store.acapyPlugins).toEqual([]);
      expect(store.loading).toEqual(false);
      expect(store.config).toBeNull();
      expect(store.error).toBeNull();
    });

    test('load() properly sets values and loading correctly ', async () => {
      let config = store.load();

      await testSuccessResponse(store, config, 'loading');
      config = await config;
      expect(config).not.toBeNull();
      expect(config.frontend).not.toBeNull();
      expect(config.frontend.tenantProxyPath).not.toBeNull();
      expect(config.frontend.apiPath).not.toBeNull();
      expect(config.frontend.basePath).not.toBeNull();
      expect(config.frontend.showDeveloper).not.toBeNull();
      expect(config.frontend.showInnkeeperReservationPassword).not.toBeNull();
      expect(config.frontend.showInnkeeperAdminLogin).not.toBeNull();
      expect(config.frontend.oidc).not.toBeNull();
      expect(config.frontend.oidc.active).not.toBeNull();
      expect(config.frontend.oidc.authority).not.toBeNull();
      expect(config.frontend.oidc.client).not.toBeNull();
      expect(config.frontend.oidc.label).not.toBeNull();
      expect(config.frontend.ux).not.toBeNull();
      expect(config.frontend.ux.appTitle).not.toBeNull();
      expect(config.frontend.ux.appInnkeeperTitle).not.toBeNull();
      expect(config.frontend.ux.sidebarTitle).not.toBeNull();
      expect(config.frontend.ux.aboutBusiness).not.toBeNull();
      expect(config.image).not.toBeNull();
      expect(config.server.tractionUrl).not.toBeNull();
    });

    test('proxyPath() returns the correct value', async () => {
      configResponse.setTenantProxyUrl('http://localhost:8080');
      let config = await store.load();
      expect(store.proxyPath('/test')).toEqual(
        config.frontend.tenantProxyPath + '/test'
      );
      expect(store.proxyPath('test')).toEqual(
        config.frontend.tenantProxyPath + '/test'
      );

      configResponse.setTenantProxyUrl('http://localhost:8080/');
      config = await store.load();
      expect(store.proxyPath('/test')).toEqual(
        config.frontend.tenantProxyPath + 'test'
      );
    });

    test('getPluginList succeeds', async () => {
      const response = await store.getPluginList();
      expect(response).toHaveLength(3);
    });
  });

  describe('Unsuccessful API calls', () => {
    beforeEach(async () => {
      server.use(...restHandlersUnknownError);
    });

    test('load error sets store error and loading', async () => {
      await testErrorResponse(store, store.load(), 'loading');
    });
  });
});
