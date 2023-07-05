import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, test } from 'vitest';

import { useInnkeeperOidcStore } from '@/store/innkeeper/innkeeperOidcStore';

let store: any;

describe('innkeeperOidcStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useInnkeeperOidcStore();
  });

  describe('Successful API calls', () => {
    test.todo('login');
  });

  describe('Unsuccessful API calls', () => {
    test.todo('login');
  });
});
