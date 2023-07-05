import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, test } from 'vitest';

import { useInnkeeperTokenStore } from '@/store/innkeeper/innkeeperTokenStore';

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

  test('clearToken sets token to null', async () => {
    store.clearToken();

    expect(store.innkeeperReady).toBeFalsy();
  });

  describe('Successful API calls', () => {
    test.todo('login');
  });

  describe('Unsuccessful API calls', () => {
    test.todo('login');
  });
});
