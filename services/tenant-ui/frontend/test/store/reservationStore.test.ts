import { flushPromises } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { beforeAll, beforeEach, describe, expect, test } from 'vitest';

import { useReservationStore } from '@/store/reservationStore';
import { restHandlersUnknownError, server } from '../setupApi';

let store: any;

describe('reservationStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useReservationStore();
  });

  test('initial values have not changed from expected', async () => {
    expect(store.loading).toEqual(false);
    expect(store.error).toEqual(null);
    expect(store.reservation).toEqual(null);
    expect(store.status).toEqual('');
    expect(store.walletId).toEqual('');
    expect(store.walletKey).toEqual('');
  });

  test('resetState', async () => {
    store.reservation = { id: 'test' };
    store.status = 'test';
    store.walletId = 'test';
    store.walletKey = 'test';
    store.resetState();
    expect(store.reservation).toEqual(null);
    expect(store.status).toEqual('');
    expect(store.walletId).toEqual('');
    expect(store.walletKey).toEqual('');
  });

  describe('Successful API calls', () => {
    test('makeReservation with automatic checkin succeeds and handles laoding correctly', async () => {
      expect(store.loading).toEqual(false);
      const response = await store.makeReservation({
        contact_email: 'test@email.com',
        contact_name: 'Test',
        contact_phone: '1234567890',
        tenant_name: 'Test',
        tenant_reason: 'Testing',
      });
      expect(store.loading).toEqual(true);
      await flushPromises();

      expect(store.loading).toEqual(false);
      expect(response.reservation_id).toEqual('reservation_id');
      expect(response.reservation_pwd).toEqual('reservation_pwd');
      expect(store.reservation.reservation_id).toEqual('reservation_id');
      expect(store.reservation.reservation_pwd).toEqual('reservation_pwd');
      expect(store.error).toEqual(null);
    });

    test.todo('checkReservation');
    test.todo('checkIn');
  });

  describe('Unsuccessful API calls', () => {
    beforeAll(() => {
      server.use(...restHandlersUnknownError);
    });

    test('makeReservation handles fails at /multitenancy/reservations correctly', async () => {
      await expect(
        store.makeReservation({
          contact_email: 'test@email.com',
          contact_name: 'Test',
          contact_phone: '1234567890',
          tenant_name: 'Test',
          tenant_reason: 'Testing',
        })
      ).rejects.toThrow();
      expect(store.loading).toEqual(false);
      expect(store.error).not.toBeNull();
    });

    test.todo('checkReservation');
    test.todo('checkIn');
  });
});
