import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, test } from 'vitest';

import { useInnkeeperOidcStore } from '@/store/innkeeper/innkeeperOidcStore';

describe('innkeeperOidcStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    useInnkeeperOidcStore();
  });

  describe('Successful API calls', () => {
    test.todo('login');
  });

  describe('Unsuccessful API calls', () => {
    test.todo('login');
  });
});
