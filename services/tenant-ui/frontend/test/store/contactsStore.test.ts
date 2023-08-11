import { flushPromises } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, test } from 'vitest';

import { useContactsStore } from '@/store/contactsStore';
import { testErrorResponse, testSuccessResponse } from '../../test/commonTests';
import { restHandlersUnknownError, server } from '../setupApi';

import { contactsResponse } from '../__mocks__/api/responses/';

let store: any;

describe('contactsStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useContactsStore();
  });

  test("initial values haven't changed from expected", async () => {
    expect(store.contacts).toEqual([]);
    expect(store.loading).toEqual(false);
    expect(store.error).toBeNull();
    expect(store.selectedContact).toBeNull();
    expect(store.loadingItem).toEqual(false);
  });

  test('contactsDropdown sorts by label and filters non active connections', async () => {
    store.contacts = contactsResponse.listConnections.results;
    await flushPromises();
    const result = store.contactsDropdown;

    expect(result).toHaveLength(2);
    expect(result[0].label).toEqual('Atest');
  });

  test('findConnectionName returns undefined while loading and connection exists', async () => {
    store.contacts = contactsResponse.listConnections.results;
    store.loading = true;
    await flushPromises();
    const result = store.findConnectionName(
      '97bacd18-2b4e-47e8-81b4-a7e7c7ef64d7'
    );
    expect(result).not.toBeDefined();
  });

  test('findConnectionName returns name while not loading and connection exists', async () => {
    store.contacts = contactsResponse.listConnections.results;
    store.loading = false;
    await flushPromises();
    const result = store.findConnectionName(
      '97bacd18-2b4e-47e8-81b4-a7e7c7ef64d7'
    );
    expect(result).toBe('Atest');
  });

  test('findConnectionName returns blank string when can not find matching connection', async () => {
    store.contacts = contactsResponse.listConnections.results;
    store.loading = false;
    await flushPromises();
    const result = store.findConnectionName('97bacd18-not-found');
    expect(result).toBe('');
  });

  describe('Success API calls', async () => {
    test('listContacts does not throw error and sets loading correctly', async () => {
      let response = store.listContacts();

      await testSuccessResponse(store, response, 'loading');
      response = await response;
      expect(response).toHaveLength(3);
    });

    test('createInvitation does not throw error and sets loading correctly', async () => {
      await testSuccessResponse(store, store.createInvitation(), 'loading');
    });

    test('receiveInvitation does not throw error and sets loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.receiveInvitation(
          '{"@type": "https://didcomm.org/connections/1.0/invitation", "@id": "8fbc2934-f7d1-4f46-aa98-41252847b3b9", "label": "Jamie", "recipientKeys": ["7pZ4SMd7KBDSqPT2HUnsbocJ1YjZQMrzzcGcsfN5NfTr"], "serviceEndpoint": "https://2682-70-66-140-105.ngrok-free.app"}',
          'test'
        ),
        'loading'
      );
    });

    test('deleteContact does not throw error and sets loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.deleteContact('test-uuid'),
        'loading'
      );
    });

    test('getContact does not throw error and sets loadingItem correctly', async () => {
      await testSuccessResponse(
        store,
        store.getContact('test-uuid'),
        'loadingItem'
      );
    });

    test('getInvitation does not throw error and sets loadingItem correctly', async () => {
      await testSuccessResponse(
        store,
        store.getInvitation('test-uuid'),
        'loadingItem'
      );
    });

    test('updateConnection does not throw error and sets loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.updateConnection('test-uuid'),
        'loading'
      );
    });

    test('didCreateRequest does not throw error and sets loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.didCreateRequest('test-did', 'test.alias', 'test-label'),
        'loading'
      );
    });
  });

  describe('Unsuccessful API calls', async () => {
    beforeEach(() => {
      server.use(...restHandlersUnknownError);
    });

    test('listContacts throws error and sets loading correctly', async () => {
      await testErrorResponse(store, store.listContacts(), 'loading');
    });

    test('createInvitation throws error and sets loading correctly', async () => {
      await testErrorResponse(store, store.createInvitation(), 'loading');
    });

    test('createInvitation throws error and sets loading correctly', async () => {
      await testErrorResponse(
        store,
        store.receiveInvitation(
          '{"@type": "https://didcomm.org/connections/1.0/invitation", "@id": "8fbc2934-f7d1-4f46-aa98-41252847b3b9", "label": "Jamie", "recipientKeys": ["7pZ4SMd7KBDSqPT2HUnsbocJ1YjZQMrzzcGcsfN5NfTr"], "serviceEndpoint": "https://2682-70-66-140-105.ngrok-free.app"}',
          'test'
        ),
        'loading'
      );
    });

    // FIXME: In src code: Does not set error or loading because exception isn't handled
    test('createInvitation with bad invite throws error and sets loading correctly', async () => {
      const response = store.receiveInvitation('', 'test');

      expect(store.loading).toEqual(true);
      await expect(response).rejects.toThrow();
    });

    test('deleteContact sets error and loading correctly', async () => {
      await testErrorResponse(
        store,
        store.deleteContact('test-uuid'),
        'loading'
      );
    });

    test('getContact sets error and loading correctly', async () => {
      await testErrorResponse(
        store,
        store.getContact('test-uuid'),
        'loadingItem'
      );
    });

    test('getInvitation sets error and loading correctly', async () => {
      await testErrorResponse(
        store,
        store.getInvitation('test-uuid'),
        'loadingItem'
      );
    });

    test('updateConnection sets error and loading correctly', async () => {
      await testErrorResponse(
        store,
        store.updateConnection('test-uuid'),
        'loading'
      );
    });

    test('didCreateRequest sets error and loading correctly', async () => {
      await testErrorResponse(
        store,
        store.didCreateRequest('test-did', 'test.alias', 'test-label'),
        'loading'
      );
    });
  });
});
