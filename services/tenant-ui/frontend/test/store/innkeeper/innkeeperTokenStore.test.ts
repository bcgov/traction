import { createPinia, setActivePinia } from 'pinia';
import { beforeAll, beforeEach, describe, expect, test } from 'vitest';

import { useInnkeeperTokenStore } from '@/store/innkeeper/innkeeperTokenStore';
import { testErrorResponse, testSuccessResponse } from '../../../test/commonTests';
import { restHandlersUnknownError, server } from '../../setupApi';

let store: any;

describe('innkeeperTokenStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useInnkeeperTokenStore();
  });

  test("initial values haven't changed from expected", () => {
    expect(store.loading).toEqual(false);
    expect(store.error).toBeNull();
  });

  test('clearToken sets innkeeperReady as falsy', async () => {
    store.clearToken();

    expect(store.innkeeperReady).toBeFalsy();
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
