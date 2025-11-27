import {
  AddOcaRecordRequest,
  CredDefPostRequest,
  CredDefResult,
  CredDefStorageRecord,
  CredentialDefinitionSendRequest,
  GetSchemaResult,
  GetSchemasResponse,
  OcaRecord,
  SchemaPostRequest,
  SchemaResult,
  SchemaSendRequest,
} from '@/types/acapyApi/acapyInterface';
import { SchemaStorageRecord } from '@/types';

import { API_PATH } from '@/helpers/constants';
import { defineStore } from 'pinia';
import { computed, Ref, ref } from 'vue';
import { useAcapyApi } from './acapyApi';
import {
  fetchItem,
  fetchList,
  filterByStateActive,
  filterMapSortList,
  sortByLabelAscending,
} from './utils';
import { AddSchemaFromLedgerRequest, StoredSchemaWithCredDefs } from '@/types';

export const useGovernanceStore = defineStore('governance', () => {
  // state
  const storedSchemas: Ref<SchemaStorageRecord[]> = ref([]);
  const selectedSchema: Ref<SchemaStorageRecord | undefined> = ref();

  const storedCredDefs: Ref<CredDefStorageRecord[]> = ref([]);
  const selectedCredentialDefinition: Ref<CredDefStorageRecord | undefined> =
    ref(undefined);

  const ocas: Ref<OcaRecord[]> = ref([]);

  const loading: Ref<boolean> = ref(false);
  const error: any = ref(null);

  // getters

  const schemaList: Ref<StoredSchemaWithCredDefs[]> = computed(() => {
    // For the list of schemas in the schema table, add cred defs
    return storedSchemas.value.map((s: any) => {
      s.credentialDefinitions = storedCredDefs.value.filter(
        (c: CredDefStorageRecord) => c.schema_id === s.schema_id
      );
      return s;
    });
  });

  const schemaLabelValue = (item: any) => {
    let result = null;
    if (item != null) {
      result = {
        label: `${item.name} (${item.version})`,
        value: item.schema_template_id,
        status: item.status,
        can_issue: item.credential_templates.length > 0,
      };
    }
    return result;
  };

  const credDefLabelValue = (item: any) => {
    let result = null;
    if (item != null) {
      result = {
        label: `${item.cred_def_id}`,
        value: item.cred_def_id,
        status: item.state,
      };
    }
    return result;
  };

  const schemaTemplateDropdown = computed(() => {
    return filterMapSortList(
      storedSchemas.value,
      schemaLabelValue,
      sortByLabelAscending,
      filterByStateActive
    );
  });

  const credentialDropdown = computed(() => {
    return filterMapSortList(
      storedCredDefs.value,
      credDefLabelValue,
      sortByLabelAscending
    );
  });

  // actions

  const acapyApi = useAcapyApi();

  async function listStoredSchemas() {
    storedSchemas.value = [];
    return fetchList(API_PATH.SCHEMA_STORAGE, storedSchemas, error, loading);
  }

  async function listAnoncredsSchemas() {
    storedSchemas.value = [];
    error.value = null;
    loading.value = true;

    try {
      // Fetch list of schema IDs
      const schemasResponse = await acapyApi.getHttp(
        API_PATH.ANONCREDS_SCHEMAS
      );
      console.log('listAnoncredsSchemas - schemasResponse:', schemasResponse);
      console.log(
        'listAnoncredsSchemas - schemasResponse.data:',
        schemasResponse.data
      );

      // Handle both direct data and axios response structure
      const responseData = schemasResponse?.data || schemasResponse;
      const schemaIds =
        (responseData as GetSchemasResponse).schema_ids || [];
      console.log('listAnoncredsSchemas - schemaIds:', schemaIds);

      // Fetch full schema details for each schema ID
      const schemaPromises = schemaIds.map(async (schemaId: string) => {
        try {
          // For schema IDs with special characters, we need to URL encode them
          // But we need to be careful - if the API expects it in the path, we encode the whole thing
          // If it expects it as a query param, we handle it differently
          // Try URL encoding the schema ID for the path
          const encodedSchemaId = encodeURIComponent(schemaId);
          console.log(`Fetching schema - original ID: ${schemaId}`);
          console.log(`Fetching schema - encoded ID: ${encodedSchemaId}`);
          console.log(`Fetching schema - URL: ${API_PATH.ANONCREDS_SCHEMA(encodedSchemaId)}`);
          
          // Build the full URL to see what we're actually calling
          const schemaUrl = API_PATH.ANONCREDS_SCHEMA(encodedSchemaId);
          console.log(`Schema ${schemaId} - Full URL being called:`, schemaUrl);
          
          const schemaResponse = await acapyApi.getHttp(schemaUrl);
          console.log(`Schema ${schemaId} - schemaResponse:`, schemaResponse);
          console.log(
            `Schema ${schemaId} - schemaResponse.data:`,
            schemaResponse.data
          );
          console.log(
            `Schema ${schemaId} - schemaResponse.status:`,
            schemaResponse.status
          );

          // Handle both direct data and axios response structure
          const schemaData = (schemaResponse?.data ||
            schemaResponse) as GetSchemaResult;

          console.log(`Schema ${schemaId} - parsed schemaData:`, schemaData);
          console.log(`Schema ${schemaId} - schemaData.schema:`, schemaData?.schema);

          // Check if schemaData exists and has the expected structure
          if (!schemaData) {
            console.warn(`Schema ${schemaId} returned empty response`);
            throw new Error('Empty response from schema endpoint');
          }

          // Ensure schema object exists
          if (!schemaData.schema) {
            console.warn(
              `Schema ${schemaId} missing schema object:`,
              schemaData
            );
            throw new Error('Schema object missing from response');
          }

          // Map GetSchemaResult to SchemaStorageRecord format
          const schemaObj = schemaData.schema;
          console.log(`Schema ${schemaId} - schemaObj:`, schemaObj);
          console.log(`Schema ${schemaId} - schemaObj.name:`, schemaObj.name);
          console.log(`Schema ${schemaId} - schemaObj.name type:`, typeof schemaObj.name);
          console.log(`Schema ${schemaId} - schemaObj.name truthy?:`, !!schemaObj.name);
          console.log(`Schema ${schemaId} - schemaObj.version:`, schemaObj.version);
          console.log(`Schema ${schemaId} - schemaObj.attrNames:`, schemaObj.attrNames);
          console.log(`Schema ${schemaId} - schemaObj.issuerId:`, schemaObj.issuerId);

          // Extract values with explicit checks
          const schemaName = schemaObj.name;
          const schemaVersion = schemaObj.version;
          console.log(`Schema ${schemaId} - extracted name:`, schemaName);
          console.log(`Schema ${schemaId} - extracted version:`, schemaVersion);
          console.log(`Schema ${schemaId} - name || 'Unknown' evaluates to:`, schemaName || 'Unknown');
          console.log(`Schema ${schemaId} - version || 'Unknown' evaluates to:`, schemaVersion || 'Unknown');

          const mappedSchema: SchemaStorageRecord = {
            schema_id: schemaData.schema_id || schemaId,
            state: 'active',
            schema: {
              name: schemaName || 'Unknown',
              version: schemaVersion || 'Unknown',
              attrNames: Array.isArray(schemaObj.attrNames)
                ? schemaObj.attrNames
                : [],
              // Add issuerId from AnonCreds schema response
              issuerId: schemaObj.issuerId,
            } as any, // Type assertion needed since issuerId is not in base Schema interface
            schema_dict: schemaObj, // Store full schema including issuerId
            created_at: schemaData.schema_metadata?.created_at,
            updated_at: schemaData.schema_metadata?.updated_at,
            ledger_id: schemaData.schema_id,
          };

          console.log(`Schema ${schemaId} - mappedSchema:`, mappedSchema);
          console.log(`Schema ${schemaId} - mappedSchema.schema:`, mappedSchema.schema);
          console.log(`Schema ${schemaId} - mappedSchema.schema.name:`, mappedSchema.schema.name);
          return mappedSchema;
        } catch (err: any) {
          console.error(`Failed to fetch schema ${schemaId}:`, err);
          console.error(`Error details:`, {
            message: err?.message,
            response: err?.response?.data,
            status: err?.response?.status,
            fullError: err,
          });
          // Log the full error response to understand what's happening
          if (err?.response) {
            console.error(`Full error response:`, err.response);
          }
          // Return a minimal schema record even if fetch fails
          // Note: state is optional and typically 'active' or 'deleted' from API
          // We don't set it for error cases since it's not a valid state value
          return {
            schema_id: schemaId,
            // state is optional - don't set it for error cases
            schema: {
              name: 'Unknown',
              version: 'Unknown',
              attrNames: [],
              // No id field - removed per user request
            },
            schema_dict: undefined,
            created_at: undefined,
            updated_at: undefined,
            ledger_id: schemaId,
          } as SchemaStorageRecord;
        }
      });

      const schemas = await Promise.all(schemaPromises);
      console.log('listAnoncredsSchemas - schemas after Promise.all:', schemas);

      // Filter out null, undefined, and schemas without proper structure
      storedSchemas.value = schemas.filter(
        (s) => s !== null && s !== undefined && s.schema_id && s.schema
      );
      console.log(
        'listAnoncredsSchemas - storedSchemas.value after filter:',
        storedSchemas.value
      );
    } catch (err) {
      console.error(err);
      error.value = err;
    } finally {
      loading.value = false;
    }
  }

  async function getStoredSchemas(): Promise<
    SchemaStorageRecord[] | undefined
  > {
    try {
      return (await acapyApi.getHttp(API_PATH.SCHEMA_STORAGE)).data.results;
    } catch (err) {
      console.error(err);
    }
    return;
  }

  async function getStoredCredDefs(): Promise<
    CredDefStorageRecord[] | undefined
  > {
    try {
      return (await acapyApi.getHttp(API_PATH.CREDENTIAL_DEFINITION_STORAGE))
        .data.results;
    } catch (err) {
      console.error(err);
    }
    return;
  }

  async function listStoredCredentialDefinitions() {
    storedCredDefs.value = [];
    return fetchList(
      API_PATH.CREDENTIAL_DEFINITION_STORAGE,
      storedCredDefs,
      error,
      loading
    );
  }

  async function listOcas() {
    ocas.value = [];
    return fetchList(API_PATH.OCAS, ocas, error, loading);
  }

  async function createSchema(payload: SchemaSendRequest) {
    console.log('> governanceStore.createSchema');
    error.value = null;
    loading.value = true;

    let result = null;

    await acapyApi
      .postHttp(API_PATH.SCHEMAS, payload)
      .then((res) => {
        result = res.data;
        console.log(result);
      })
      .then(() => {
        // Refresh the schema list
        listStoredSchemas();
      })
      .catch((err) => {
        console.log(err);
        error.value = err;
        // console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< governanceStore.createSchema');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  async function createAnoncredsSchema(payload: SchemaPostRequest) {
    console.log('> governanceStore.createAnoncredsSchema');
    error.value = null;
    loading.value = true;

    let result: SchemaResult | null = null;

    await acapyApi
      .postHttp(API_PATH.ANONCREDS_SCHEMA_POST, payload)
      .then((res) => {
        result = res.data;
        console.log(result);
      })
      .then(() => {
        // Refresh the schema list
        listAnoncredsSchemas();
      })
      .catch((err) => {
        console.log(err);
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< governanceStore.createAnoncredsSchema');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  async function addSchemaFromLedgerToStorage(
    payload: AddSchemaFromLedgerRequest
  ) {
    console.log('> governanceStore.copySchema');
    error.value = null;
    loading.value = true;

    let result = null;

    await acapyApi
      .postHttp(API_PATH.SCHEMA_STORAGE, payload)
      .then((res) => {
        result = res.data;
        console.log(result);
      })
      .then(() => {
        listStoredSchemas();
      })
      .catch((err) => {
        error.value = err;
        // console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< governanceStore.copySchema');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  async function createCredentialDefinition(
    payload: CredentialDefinitionSendRequest
  ) {
    console.log('> governanceStore.createCredentialDefinition');
    error.value = null;
    loading.value = true;

    let result = null;

    await acapyApi
      .postHttp(API_PATH.CREDENTIAL_DEFINITIONS, payload)
      .then((res) => {
        result = res.data;
        console.log(result);
      })
      .then(() => {
        // Refresh the schema list
        listStoredCredentialDefinitions();
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< governanceStore.createCredentialDefinition');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  async function createAnoncredsCredentialDefinition(
    payload: CredDefPostRequest
  ) {
    console.log('> governanceStore.createAnoncredsCredentialDefinition');
    error.value = null;
    loading.value = true;

    let result: CredDefResult | null = null;

    await acapyApi
      .postHttp(API_PATH.ANONCREDS_CREDENTIAL_DEFINITION_POST, payload)
      .then((res) => {
        result = res.data;
        console.log(result);
      })
      .then(() => {
        // Refresh the credential definition list
        listStoredCredentialDefinitions();
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< governanceStore.createAnoncredsCredentialDefinition');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  // async function getSchemaTemplate(id: string, params: any = {}) {
  //   const getloading: any = ref(false);
  //   if (!('credential_templates' in params)) {
  //     // if we do not explicitly say not to get cred templates, get 'em.
  //     params.credential_templates = true;
  //   }
  //   return fetchItem(
  //     API_PATH.GOVERNANCE_SCHEMA_TEMPLATES,
  //     id,
  //     error,
  //     getloading,
  //     params
  //   );
  // }

  async function getCredentialTemplate(id: string, params: any = {}) {
    const getloading: any = ref(false);
    return fetchItem(
      API_PATH.CREDENTIAL_DEFINITIONS,
      id,
      error,
      getloading,
      params
    );
  }

  async function deleteSchema(schemaId: string) {
    console.log('> governanceStore.deleteSchema');
    error.value = null;
    loading.value = true;

    let result = null;

    await acapyApi
      .deleteHttp(API_PATH.SCHEMA_STORAGE_ITEM(schemaId), {})
      .then((res) => {
        result = res.data.item;
      })
      .then(() => {
        console.log('schema deleted.');
        listStoredSchemas(); // Refresh table
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< governanceStore.deleteSchema');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  async function deleteStoredCredentialDefinition(credDefId: string) {
    console.log('> governanceStore.deleteStoredCredentialDefinition');
    error.value = null;
    loading.value = true;

    let result = null;

    await acapyApi
      .deleteHttp(API_PATH.CREDENTIAL_DEFINITION_STORAGE_ITEM(credDefId), {})
      .then((res) => {
        result = res.data.item;
      })
      .then(() => {
        console.log('stored cred deleted.');
        listStoredCredentialDefinitions(); // Refresh table
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< governanceStore.deleteStoredCredentialDefinition');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  async function getOca(id: string, params: any = {}) {
    const getloading: any = ref(false);
    return fetchItem(API_PATH.OCAS, id, error, getloading, params);
  }

  async function createOca(payload: AddOcaRecordRequest) {
    console.log('> governanceStore.createOca');
    error.value = null;
    loading.value = true;

    let result = null;

    await acapyApi
      .postHttp(API_PATH.OCAS, payload)
      .then((res) => {
        result = res.data.item;
        console.log(result);
        listOcas(); // Refresh table
      })
      .catch((err) => {
        error.value = err;
        // console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< governanceStore.createOca');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  async function deleteOca(ocaId: string) {
    console.log('> governanceStore.deleteOca');
    error.value = null;
    loading.value = true;

    let result = null;

    await acapyApi
      .deleteHttp(API_PATH.OCA(ocaId), {})
      .then((res) => {
        result = res.data.item;
      })
      .then(() => {
        console.log('oca record deleted.');
        listOcas(); // Refresh table
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< governanceStore.deleteOca');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  const setSelectedSchemaById = async (id: string) => {
    await getStoredSchemas();
    selectedSchema.value = storedSchemas.value.find(
      (s: SchemaStorageRecord) => s.schema_id === id
    );
  };

  return {
    credentialDropdown,
    error,
    loading,
    ocas,
    schemaList,
    schemaTemplateDropdown,
    selectedCredentialDefinition,
    selectedSchema,
    storedCredDefs,
    storedSchemas,
    // getSchemaTemplate,
    addSchemaFromLedgerToStorage,
    createAnoncredsCredentialDefinition,
    createAnoncredsSchema,
    createCredentialDefinition,
    createOca,
    createSchema,
    deleteOca,
    deleteSchema,
    deleteStoredCredentialDefinition,
    getStoredCredDefs,
    getCredentialTemplate,
    getOca,
    getStoredSchemas,
    listAnoncredsSchemas,
    listOcas,
    listStoredCredentialDefinitions,
    listStoredSchemas,
    setSelectedSchemaById,
  };
});

export default {
  useGovernanceStore,
};
