import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, test } from 'vitest';

import { useCommonStore } from '@/store/commonStore';

describe('commonStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
  });

  test('initial values have not changed from expected', () => {
    const store = useCommonStore();
    expect(store).toBeDefined();
    expect(store.sidebarOpen).toBeNull();
  });
});
