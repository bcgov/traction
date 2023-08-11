import { createPinia, setActivePinia } from 'pinia';
import { beforeAll, beforeEach, describe, expect, test } from 'vitest';

import { useTokenStore } from '@/store/tokenStore';
import { testErrorResponse, testSuccessResponse } from '../../test/commonTests';
import { restHandlersUnknownError, server } from '../setupApi';

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
