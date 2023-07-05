import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, test } from 'vitest';

import { useInnkeeperTenantsStore } from '@/store/innkeeper/innkeeperTenantsStore';

let store: any;

describe('innkeeperTenantsStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useInnkeeperTenantsStore();
  });

  test("initial values haven't changed from expected", () => {
    expect(store.reservations).toEqual([]);
    expect(store.tenants).toEqual([]);
    expect(store.loading).toEqual(false);
    expect(store.error).toBeNull();
  });

  describe('Successful API calls', () => {
    test.todo('approveReservation');
    test.todo('denyReservation');
    test.todo('listTenants');
    test.todo('listReservations');
    test.todo('updateTenantConfig');
  });

  describe('Unsuccessful API calls', () => {
    test.todo('approveReservation');
    test.todo('denyReservation');
    test.todo('listTenants');
    test.todo('listReservations');
    test.todo('updateTenantConfig');
  });
});
