import { createPinia, setActivePinia } from 'pinia';
import {
  afterEach,
  beforeAll,
  beforeEach,
  describe,
  expect,
  test,
  vi,
} from 'vitest';

import { useTokenStore } from '@/store/tokenStore';
import { testErrorResponse, testSuccessResponse } from '../../test/commonTests';
import { restHandlersUnknownError, server } from '../setupApi';

import { API_PATH } from '@/helpers/constants';
import { configStore } from '../../test/__mocks__/store';

vi.mock('@/store/configStore', () => ({
  useConfigStore: () => configStore,
}));

vi.mock('global.localStorage', () => ({
  getItem: vi.fn(),
  setItem: vi.fn(),
}));

const setLocalStorageSpy = vi.spyOn(Storage.prototype, 'setItem');
const removeLocalStorageSpy = vi.spyOn(Storage.prototype, 'removeItem');

configStore.proxyPath = vi
  .fn()
  .mockReturnValue(API_PATH.MULTITENANCY_WALLET_TOKEN('username'));

let store: any;

describe('tokenStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useTokenStore();
  });

  afterEach(() => {
    setLocalStorageSpy.mockClear();
    removeLocalStorageSpy.mockClear();
    localStorage.clear();
  });

  test("initial values haven't changed from expected", () => {
    expect(store.token).toBeNull();
    expect(store.loading).toEqual(false);
    expect(store.error).toBeNull();
  });

  test('clearToken sets token to null and removes local storage', () => {
    store.clearToken();

    expect(store.token).toBeNull();
    expect(removeLocalStorageSpy).toHaveBeenCalledOnce();
  });

  describe('Successful API calls', () => {
    test('login sets token, local storage and loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.login('username', 'password'),
        'loading'
      );
    });
  });

  describe('Unsuccessful API calls', () => {
    beforeAll(() => {
      server.use(...restHandlersUnknownError);
    });

    test('login error sets store error and loading', async () => {
      await testErrorResponse(
        store,
        store.login('username', 'password'),
        'loading'
      );
    });
  });
});
