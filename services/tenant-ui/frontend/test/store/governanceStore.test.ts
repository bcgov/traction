import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, test } from 'vitest';

import { useGovernanceStore } from '@/store/governanceStore';

let store: any;

describe('governanceStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useGovernanceStore();
  });

  describe('Initialization', () => {
    test("initial values haven't changed from expected", () => {
      expect(store.storedSchemas).toEqual([]);
      expect(store.selectedSchema).toBeNull();
      expect(store.storedCredDefs).toEqual([]);
      expect(store.selectedCredentialDefinition).toBeNull();
      expect(store.ocas).toEqual([]);
      expect(store.loading).toEqual(false);
      expect(store.error).toBeNull();
    });
  });

  describe('Success API responses', async () => {
    test('listStoredSchemas does not throw error and sets loading correctly', async () => {
      let response = store.listStoredSchemas();
      expect(store.loading).toEqual(true);
      response = await response;

      expect(response.result).not.toBeNull();
      expect(store.loading).toEqual(false);
      expect(store.error).toBeNull();
      expect(response).toHaveLength(1);
    });

    test('createSchema does not throw error and sets loading correctly', async () => {
      let response = store.createSchema({
        attributes: ['age'],
        schema_name: 'Test Schema',
        schema_version: '1.0',
      });

      expect(store.loading).toEqual(true);
      response = await response;
      expect(response.result).not.toBeNull();
      expect(store.loading).toEqual(false);
      expect(store.error).toBeNull();
    });

    test.todo('copySchema');
    test.todo('deleteSchema');
    test.todo('listStoredCredentialDefinitions');
    test.todo('createCredentialDefinition');
    test.todo('getCredentialTemplate');
    test.todo('deleteStoredCredentialDefinition');
    test.todo('listOcas');
    test.todo('getOca');
    test.todo('createOca');
    test.todo('deleteOca');
  });

  describe('Unsuccessful API responses', () => {
    test.todo('listStoredSchemas');
    test.todo('createSchema');
    test.todo('copySchema');
    test.todo('deleteSchema');
    test.todo('listStoredCredentialDefinitions');
    test.todo('createCredentialDefinition');
    test.todo('getCredentialTemplate');
    test.todo('deleteStoredCredentialDefinition');
    test.todo('listOcas');
    test.todo('getOca');
    test.todo('createOca');
    test.todo('deleteOca');
  });
});
