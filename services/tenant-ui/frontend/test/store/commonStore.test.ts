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
    expect(store.cardExpanded).toBe(false);
    expect(store.sidebarOpen).toBeNull();
  });

  test('sidebarOpenClass returns open when sidebarOpen is truthy', () => {
    const store = useCommonStore();
    store.sidebarOpen = true;

    expect(store.sidebarOpenClass).toBe('open');
  });

  test('sidebarOpenClass returns clased when sidebarOpen is falsy', () => {
    const store = useCommonStore();
    store.sidebarOpen = false;

    expect(store.sidebarOpenClass).toBe('closed');
  });
});
