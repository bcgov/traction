import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, test } from 'vitest';

import { useInnkeeperTenantsStore } from '@/store/innkeeper/innkeeperTenantsStore';
import {
  testErrorResponse,
  testSuccessResponse,
} from '../../../test/commonTests';
import { restHandlersUnknownError, server } from '../../setupApi';

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
    test.skip('approveReservation does not throw error and handles loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.approveReservation('test-id'),
        'loading'
      );
    });

    test.skip('denyReservation does not throw error and handles loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.denyReservation('test-id'),
        'loading'
      );
    });

    test('listTenants does not throw error and handles loading correctly', async () => {
      await testSuccessResponse(store, store.listReservations(), 'loading');
    });

    test('listReservations does not throw error and handles loading correctly', async () => {
      await testSuccessResponse(store, store.listReservations(), 'loading');
    });

    test('updateTenantConfig does not throw error and handles loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.updateTenantConfig('test-id'),
        'loading'
      );
    });
  });

  describe('Unsuccessful API calls', () => {
    beforeEach(() => {
      server.use(...restHandlersUnknownError);
    });

    test('approveReservation handles error correctly', async () => {
      await testErrorResponse(
        store,
        store.approveReservation('test-id'),
        'loading'
      );
    });

    test('denyReservation handles error correctly', async () => {
      await testErrorResponse(
        store,
        store.denyReservation('test-id'),
        'loading'
      );
    });

    test('listTenants handles error correctly', async () => {
      await testErrorResponse(store, store.listTenants(), 'loading');
    });

    test('listReservations handles error correctly', async () => {
      await testErrorResponse(store, store.listReservations(), 'loading');
    });

    test('updateTenantConfig handles error correctly', async () => {
      await testErrorResponse(
        store,
        store.updateTenantConfig('test-id'),
        'loading'
      );
    });
  });
});
