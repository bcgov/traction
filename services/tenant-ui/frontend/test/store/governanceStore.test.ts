import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, test } from 'vitest';

import { useGovernanceStore } from '@/store/governanceStore';
import { testErrorResponse, testSuccessResponse } from '../../test/commonTests';
import { restHandlersUnknownError, server } from '../setupApi';

import responses from '../__mocks__/api/responses/governance';

let store: any;

describe('connectionStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useGovernanceStore();
  });

  test("initial values haven't changed from expected", () => {
    expect(store.storedSchemas).toEqual([]);
    expect(store.selectedSchema).toBeUndefined();
    expect(store.storedCredDefs).toEqual([]);
    expect(store.selectedCredentialDefinition).toBeUndefined();
    expect(store.ocas).toEqual([]);
    expect(store.loading).toEqual(false);
    expect(store.error).toBeNull();
  });

  test('schemaList appends credential definition to schema object', () => {
    store.storedSchemas = responses.schemas.results;
    store.storedCredDefs = responses.credentialDefinitions.results;

    const result = store.schemaList;

    expect(result).toHaveLength(1);
    expect(result[0].credentialDefinitions).toBeDefined();
  });

  // Some interesting behavior here. Needs more testing.
  test.todo('schemaTemplateDropdown');
  test.todo('credentialDropdown');

  describe('Success API responses', async () => {
    test('listStoredSchemas does not throw error and sets loading correctly', async () => {
      const response = store.listStoredSchemas();
      await testSuccessResponse(store, response, 'loading');
      expect(await response).toHaveLength(1);
      expect(store.storedSchemas).toHaveLength(1);
    });

    test('createSchema does not throw error and sets loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.createSchema({
          attributes: ['age'],
          schema_name: 'Test Schema',
          schema_version: '1.0',
        }),
        'loading'
      );
    });

    test('deleteSchema does not throw error and sets loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.deleteSchema('test-uuid'),
        'loading'
      );
    });

    test('listStoredCredentialDefinitions does not throw error and sets loading correctly', async () => {
      const response = store.listStoredCredentialDefinitions();
      await testSuccessResponse(store, response, 'loading');
      expect(await response).toHaveLength(1);
      expect(store.storedCredDefs).toHaveLength(1);
    });

    test('createCredentialDefinition does not throw error and sets loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.createCredentialDefinition(),
        'loading'
      );
    });

    test('getCredentialTemplate does not throw error and sets loading correctly', async () => {
      const response = await store.getCredentialTemplate('test-id');

      expect(response).not.toBeNull();
      expect(store.error).toBeNull();
    });

    test('deleteStoredCredentialDefinition does not throw error and sets loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.deleteStoredCredentialDefinition('test-uuid'),
        'loading'
      );
    });

    test('listOcas does not throw error and sets loading correctly', async () => {
      const response = store.listOcas();
      await testSuccessResponse(store, response, 'loading');
      expect(await response).toHaveLength(1);
      expect(store.ocas).toHaveLength(1);
    });

    test('getOca does not throw error and sets loading correctly', async () => {
      const response = await store.getOca('test-id');

      expect(response).not.toBeNull();
      expect(store.error).toBeNull();
    });

    test('createOca does not throw error and sets loading correctly', async () => {
      await testSuccessResponse(store, store.createOca(), 'loading');
    });

    test('deleteOca does not throw error and sets loading correctly', async () => {
      await testSuccessResponse(store, store.deleteOca('test-uuid'), 'loading');
    });
  });

  describe.skip('Unsuccessful API calls', async () => {
    beforeEach(() => {
      server.use(...restHandlersUnknownError);
    });

    test('listStoredSchemas throws error and sets loading correctly', async () => {
      await testErrorResponse(store, store.listStoredSchemas(), 'loading');
    });

    test('createSchema throws error and sets loading correctly', async () => {
      await testErrorResponse(
        store,
        store.createSchema({
          attributes: ['age'],
          schema_name: 'Test Schema',
          schema_version: '1.0',
        }),
        'loading'
      );
    });

    test('deleteSchema throws error and sets loading correctly', async () => {
      await testErrorResponse(
        store,
        store.deleteSchema('test-uuid'),
        'loading'
      );
    });

    test('listStoredCredentialDefinitions throws error and sets loading correctly', async () => {
      await testErrorResponse(
        store,
        store.listStoredCredentialDefinitions(),
        'loading'
      );
    });

    test('createCredentialDefinition throws error and sets loading correctly', async () => {
      await testErrorResponse(
        store,
        store.createCredentialDefinition(),
        'loading'
      );
    });

    test('deleteStoredCredentialDefinition throws error and sets loading correctly', async () => {
      await testErrorResponse(
        store,
        store.deleteStoredCredentialDefinition('test-uuid'),
        'loading'
      );
    });

    test('listOcas throws error and sets loading correctly', async () => {
      await testErrorResponse(store, store.listOcas(), 'loading');
    });

    test('getOca does not throw error and sets loading correctly', async () => {
      await expect(store.getOca('test-id')).rejects.toThrow();
      expect(store.error).not.toBeNull();
    });

    test('createOca throws error and sets loading correctly', async () => {
      await testErrorResponse(store, store.createOca(), 'loading');
    });

    test('deleteStoredCredentialDefinition throws error and sets loading correctly', async () => {
      await testErrorResponse(store, store.deleteOca('test-uuid'), 'loading');
    });
  });
});
