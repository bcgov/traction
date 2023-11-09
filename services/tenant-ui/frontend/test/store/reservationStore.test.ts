import { flushPromises } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { beforeAll, beforeEach, describe, expect, test } from 'vitest';

import { useReservationStore } from '@/store/reservationStore';
import { testErrorResponse, testSuccessResponse } from '../../test/commonTests';
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
    test('makeReservation with automatic checkin succeeds and handles loading correctly', async () => {
      expect(store.loading).toEqual(false);
      const response = await store.makeReservation({
        contact_email: 'test@email.com',
        tenant_name: 'Test',
        auto_approve: true,
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

    test('makeReservation with verification send email and does not throw an error', async () => {
      expect(store.loading).toEqual(false);
      const response = await store.makeReservation({
        contact_email: 'test@email.com',
        tenant_name: 'Test',
        auto_approve: false,
      });
      await flushPromises();

      expect(store.loading).toEqual(false);
      expect(response.reservation_id).toEqual('reservation_id');
      expect(response.reservation_pwd).toBeFalsy();
      expect(store.reservation.reservation_id).toEqual('reservation_id');
      expect(store.reservation.reservation_pwd).toBeFalsy();
      expect(store.error).toEqual(null);
    });

    test('checkReservation succeeds and handles loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.checkReservation('test-id'),
        'loading'
      );
    });

    test('checkIn succeeds and set values correctly', async () => {
      await testSuccessResponse(
        store,
        store.checkIn('reservation_id', 'test-pwd'),
        'loading'
      );

      expect(store.walletId).toEqual('wallet_id');
      expect(store.walletKey).toEqual('wallet_key');
      expect(store.status).toEqual('show_wallet');
    });

    test.todo('checkIn');
  });

  describe('Unsuccessful API calls', () => {
    beforeAll(() => {
      server.use(...restHandlersUnknownError);
    });

    test('makeReservation handles fails at /multitenancy/reservations correctly', async () => {
      await testErrorResponse(
        store,
        store.makeReservation({
          contact_email: 'test@email.com',
          tenant_name: 'Test',
        }),
        'loading'
      );
    });

    test('checkReservation fails with 404 when emails do not match', async () => {
      const response = await store.checkReservation('test-id');
      expect(response).toEqual('not_found');
    });

    test('checkIn does not throw error and sets loading and error properly', async () => {
      await store.checkIn('reservation_id', 'test-pwd');

      expect(store.loading).toEqual(false);
    });

    test.todo('checkIn');
  });
});
