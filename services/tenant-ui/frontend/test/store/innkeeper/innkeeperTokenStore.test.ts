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

import { useInnkeeperTokenStore } from '@/store/innkeeper/innkeeperTokenStore';
import {
  testErrorResponse,
  testSuccessResponse,
} from '../../../test/commonTests';
import { restHandlersUnknownError, server } from '../../setupApi';

let store: any;

vi.mock('global.localStorage', () => ({
  getItem: vi.fn(),
  setItem: vi.fn(),
}));

const setLocalStorageSpy = vi.spyOn(Storage.prototype, 'setItem');
const removeLocalStorageSpy = vi.spyOn(Storage.prototype, 'removeItem');

describe('innkeeperTokenStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useInnkeeperTokenStore();
  });

  afterEach(() => {
    setLocalStorageSpy.mockClear();
    removeLocalStorageSpy.mockClear();
    localStorage.clear();
  });

  test("initial values haven't changed from expected", () => {
    expect(store.loading).toEqual(false);
    expect(store.error).toBeNull();
  });

  test('clearToken sets innkeeperReady as falsy', async () => {
    store.clearToken();

    expect(store.innkeeperReady).toBeFalsy();
    expect(removeLocalStorageSpy).toHaveBeenCalledOnce();
  });

  describe('Successful API calls', async () => {
    test('login sets loading correctly and sets token', async () => {
      await testSuccessResponse(
        store,
        store.login({
          adminName: 'admin',
          adminKey: 'adminKey',
        }),
        'loading'
      );
      expect(store.innkeeperReady).toBeTruthy();
    });
  });

  describe('Unsuccessful API calls', () => {
    beforeAll(() => {
      server.use(...restHandlersUnknownError);
    });

    test('login error sets store error and loading', async () => {
      await testErrorResponse(
        store,
        store.login({
          adminName: 'admin',
          adminKey: 'adminKey',
        }),
        'loading'
      );
    });
  });
});
