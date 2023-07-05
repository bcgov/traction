import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, test } from 'vitest';

import { useContactsStore } from '@/store/contactsStore';

import { restHandlersUnknownError, server } from '../setupApi';

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

  describe('Success API calls', async () => {
    test('listContacts does not throw error and sets loading correctly', async () => {
      let response = store.listContacts();
      expect(store.loading).toEqual(true);
      response = await response;

      expect(response.result).not.toBeNull();
      expect(store.loading).toEqual(false);
      expect(store.error).toBeNull();
      expect(response).toHaveLength(2);
    });

    test('createInvitation does not throw error and sets loading correctly', async () => {
      let response = store.createInvitation();
      expect(store.loading).toEqual(true);
      response = await response;

      expect(response.result).not.toBeNull();
      expect(store.loading).toEqual(false);
      expect(store.error).toBeNull();
    });

    test('receiveInvitation does not throw error and sets loading correctly', async () => {
      let response = store.receiveInvitation(
        '{"@type": "https://didcomm.org/connections/1.0/invitation", "@id": "8fbc2934-f7d1-4f46-aa98-41252847b3b9", "label": "Jamie", "recipientKeys": ["7pZ4SMd7KBDSqPT2HUnsbocJ1YjZQMrzzcGcsfN5NfTr"], "serviceEndpoint": "https://2682-70-66-140-105.ngrok-free.app"}',
        'test'
      );

      expect(store.loading).toEqual(true);
      response = await response;

      expect(response.result).not.toBeNull();
      expect(store.loading).toEqual(false);
      expect(store.error).toBeNull();
    });

    test('deleteContact does not throw error and sets loading correctly', async () => {
      let response = store.deleteContact('test-uuid');

      expect(store.loading).toEqual(true);
      response = await response;

      expect(response.result).not.toBeNull();
      expect(store.loading).toEqual(false);
      expect(store.error).toBeNull();
    });

    test.todo('getContact');
    test.todo('getInvitation');
    test.todo('updateConnection');
    test.todo('didCreateRequest');
  });

  describe('Unsuccessful API calls', async () => {
    beforeEach(() => {
      server.use(...restHandlersUnknownError);
    });

    test('listContacts throws error and sets loading correctly', async () => {
      let response = store.listContacts();

      expect(store.loading).toEqual(true);
      await expect(response).rejects.toThrow();
      expect(store.loading).toEqual(false);
      expect(store.error).not.toBeNull();
    });

    test('createInvitation throws error and sets loading correctly', async () => {
      let response = store.createInvitation();

      expect(store.loading).toEqual(true);
      await expect(response).rejects.toThrow();
      expect(store.loading).toEqual(false);
      expect(store.error).not.toBeNull();
    });

    test('createInvitation throws error and sets loading correctly', async () => {
      let response = store.receiveInvitation(
        '{"@type": "https://didcomm.org/connections/1.0/invitation", "@id": "8fbc2934-f7d1-4f46-aa98-41252847b3b9", "label": "Jamie", "recipientKeys": ["7pZ4SMd7KBDSqPT2HUnsbocJ1YjZQMrzzcGcsfN5NfTr"], "serviceEndpoint": "https://2682-70-66-140-105.ngrok-free.app"}',
        'test'
      );

      expect(store.loading).toEqual(true);
      await expect(response).rejects.toThrow();
      expect(store.loading).toEqual(false);
      expect(store.error).not.toBeNull();
    });

    // FIXME: In src code: Does not set error or loading because exception isn't handled
    test('createInvitation with bad invite throws error and sets loading correctly', async () => {
      let response = store.receiveInvitation('', 'test');

      expect(store.loading).toEqual(true);
      await expect(response).rejects.toThrow();
    });

    test('deleteContact sets error and loading correctly', async () => {
      let response = store.deleteContact('test-uuid');

      expect(store.loading).toEqual(true);
      await expect(response).rejects.toThrow();
      expect(store.loading).toEqual(false);
      expect(store.error).not.toBeNull();
    });

    test.todo('getContact');
    test.todo('getInvitation');
    test.todo('updateConnection');
    test.todo('didCreateRequest');
  });
});
