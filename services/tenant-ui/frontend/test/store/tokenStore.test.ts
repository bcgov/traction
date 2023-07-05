import { createPinia, setActivePinia } from 'pinia';
import { beforeAll, beforeEach, describe, expect, test } from 'vitest';

import { useTokenStore } from '@/store/tokenStore';
import { server, restHandlersUnknownError } from '../setupApi';

let store: any;

describe('tokenStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useTokenStore();
  });

  test("initial values haven't changed from expected", () => {
    expect(store.token).toBeNull();
    expect(store.loading).toEqual(false);
    expect(store.error).toBeNull();
  });

  test('clearToken sets token to null', () => {
    store.clearToken();

    expect(store.token).toBeNull();
  });

  describe('Successful API calls', () => {
    test('login sets token and loading correctly', async () => {
      const response = store.login('username', 'password');
      expect(store.loading).toEqual(true);
      await response;

      expect(store.token).not.toBeNull();
      expect(store.loading).toEqual(false);
    });
  });

  describe('Unsuccessful API calls', () => {
    beforeAll(() => {
      server.use(...restHandlersUnknownError);
    });

    test('login error sets store error and loading', async () => {
      await expect(store.login('username', 'password')).rejects.toThrow();
      expect(store.error).not.toBeNull();
      expect(store.loading).toEqual(false);
    });
  });
});
