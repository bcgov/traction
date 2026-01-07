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
import { truncateId } from '@/helpers';

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
      // For AnonCreds credential definitions, try to create a more readable label
      // Use tag if available, otherwise use truncated cred_def_id
      let label;
      if (item.tag) {
        // If tag exists, show tag with truncated ID in parentheses
        label = `${item.tag} (${truncateId(item.cred_def_id)})`;
      } else {
        // Otherwise just show truncated ID
        label = truncateId(item.cred_def_id);
      }
      result = {
        label: label,
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

  async function listAllSchemasForAnoncredsWallet() {
    // For askar-anoncreds wallets, load from BOTH sources and merge
    error.value = null;
    loading.value = true;

    try {
      // Load from both endpoints in parallel
      const [indySchemasResult, anoncredsSchemasResult] =
        await Promise.allSettled([
          acapyApi.getHttp(API_PATH.SCHEMA_STORAGE),
          acapyApi.getHttp(API_PATH.ANONCREDS_SCHEMAS),
        ]);

      const indySchemas: SchemaStorageRecord[] = [];
      if (indySchemasResult.status === 'fulfilled') {
        const indyData =
          indySchemasResult.value?.data || indySchemasResult.value;
        indySchemas.push(...(indyData?.results || []));
      }

      // Process AnonCreds schemas
      const anoncredsSchemas: SchemaStorageRecord[] = [];
      if (anoncredsSchemasResult.status === 'fulfilled') {
        const anoncredsData =
          anoncredsSchemasResult.value?.data || anoncredsSchemasResult.value;
        const schemaIds =
          (anoncredsData as GetSchemasResponse).schema_ids || [];

        const schemaPromises = schemaIds.map(async (schemaId: string) => {
          try {
            const encodedSchemaId = encodeURIComponent(schemaId);
            const schemaUrl = `/anoncreds/schema/${encodedSchemaId}`;
            const schemaResponse = await acapyApi.getHttp(schemaUrl);
            const schemaData = (schemaResponse?.data ||
              schemaResponse) as GetSchemaResult;

            if (!schemaData?.schema) {
              return null;
            }

            const schemaObj = schemaData.schema;
            return {
              schema_id: schemaData.schema_id || schemaId,
              state: 'active',
              schema: {
                name: schemaObj.name || 'Unknown',
                version: schemaObj.version || 'Unknown',
                attrNames: Array.isArray(schemaObj.attrNames)
                  ? schemaObj.attrNames
                  : [],
                issuerId: schemaObj.issuerId,
              } as any,
              schema_dict: schemaObj,
              created_at: schemaData.schema_metadata?.created_at,
              updated_at: schemaData.schema_metadata?.updated_at,
              ledger_id: schemaData.schema_id,
            } as SchemaStorageRecord;
          } catch (err) {
            console.error(
              'Failed to fetch anoncreds schema',
              { schemaId, error: err }
            );
            return null;
          }
        });

        const schemaResults = await Promise.allSettled(schemaPromises);
        anoncredsSchemas.push(
          ...schemaResults
            .filter(
              (result): result is PromiseFulfilledResult<SchemaStorageRecord> =>
                result.status === 'fulfilled' && result.value !== null
            )
            .map((result) => result.value)
        );
      }

      // Merge and deduplicate by schema_id
      const schemaMap = new Map<string, SchemaStorageRecord>();

      // Add Indy schemas first
      indySchemas.forEach((schema) => {
        if (schema?.schema_id) {
          schemaMap.set(schema.schema_id, schema);
        }
      });

      // Add AnonCreds schemas (will overwrite if duplicate, but that's okay)
      anoncredsSchemas.forEach((schema) => {
        if (schema?.schema_id) {
          schemaMap.set(schema.schema_id, schema);
        }
      });

      storedSchemas.value = Array.from(schemaMap.values());
    } catch (err) {
      console.error(err);
      error.value = err;
    } finally {
      loading.value = false;
    }
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

      // Handle both direct data and axios response structure
      const responseData = schemasResponse?.data || schemasResponse;
      const schemaIds = (responseData as GetSchemasResponse).schema_ids || [];

      // Fetch full schema details for each schema ID
      const schemaPromises = schemaIds.map(async (schemaId: string) => {
        // URL encode the schema ID for use in the path parameter
        // Schema IDs contain special characters like : and / that must be encoded
        const encodedSchemaId = encodeURIComponent(schemaId);

        // Manually construct the URL path with encoded ID to ensure encoding is preserved
        const schemaUrl = `/anoncreds/schema/${encodedSchemaId}`;

        const schemaResponse = await acapyApi.getHttp(schemaUrl);

        // Handle both direct data and axios response structure
        const schemaData = (schemaResponse?.data ||
          schemaResponse) as GetSchemaResult;

        // Check if schemaData exists and has the expected structure
        if (!schemaData) {
          throw new Error('Empty response from schema endpoint');
        }

        // Ensure schema object exists
        if (!schemaData.schema) {
          throw new Error('Schema object missing from response');
        }

        // Map GetSchemaResult to SchemaStorageRecord format
        const schemaObj = schemaData.schema;
        const mappedSchema: SchemaStorageRecord = {
          schema_id: schemaData.schema_id || schemaId,
          state: 'active',
          schema: {
            name: schemaObj.name || 'Unknown',
            version: schemaObj.version || 'Unknown',
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

        return mappedSchema;
      });

      // Use Promise.allSettled to handle individual failures without stopping all requests
      const schemaResults = await Promise.allSettled(schemaPromises);

      // Extract only successfully fetched schemas
      const schemas = schemaResults
        .filter(
          (result): result is PromiseFulfilledResult<SchemaStorageRecord> =>
            result.status === 'fulfilled'
        )
        .map((result) => result.value);

      // Filter out null, undefined, and schemas without proper structure
      storedSchemas.value = schemas.filter(
        (s) => s !== null && s !== undefined && s.schema_id && s.schema
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

  async function listAllCredDefsForAnoncredsWallet() {
    // For askar-anoncreds wallets, load from BOTH sources and merge
    error.value = null;
    loading.value = true;

    try {
      // Load from both endpoints in parallel
      const [indyCredDefsResult, anoncredsCredDefsResult] =
        await Promise.allSettled([
          acapyApi.getHttp(API_PATH.CREDENTIAL_DEFINITION_STORAGE),
          acapyApi.getHttp(API_PATH.ANONCREDS_CREDENTIAL_DEFINITIONS),
        ]);

      const indyCredDefs: CredDefStorageRecord[] = [];
      if (indyCredDefsResult.status === 'fulfilled') {
        const indyData =
          indyCredDefsResult.value?.data || indyCredDefsResult.value;
        indyCredDefs.push(...(indyData?.results || []));
      }

      // Process AnonCreds credential definitions
      const anoncredsCredDefs: CredDefStorageRecord[] = [];
      if (anoncredsCredDefsResult.status === 'fulfilled') {
        const anoncredsData =
          anoncredsCredDefsResult.value?.data || anoncredsCredDefsResult.value;
        const credDefIds =
          (anoncredsData as { credential_definition_ids?: string[] })
            ?.credential_definition_ids || [];

        if (credDefIds && credDefIds.length > 0) {
          const credDefPromises = credDefIds.map(async (credDefId: string) => {
            try {
              const encodedCredDefId = encodeURIComponent(credDefId);
              const credDefUrl = `/anoncreds/credential-definition/${encodedCredDefId}`;
              const credDefResponse = await acapyApi.getHttp(credDefUrl);
              const credDefData = credDefResponse?.data || credDefResponse;

              const hasRevocationObject =
                credDefData?.credential_definition?.value?.revocation !==
                  undefined &&
                credDefData.credential_definition.value.revocation !== null;

              const revocationSupport =
                hasRevocationObject ||
                credDefData?.credential_definition?.revocation !== undefined ||
                credDefData?.options?.support_revocation === true ||
                credDefData?.support_revocation === true;

              const tag =
                credDefData?.credential_definition?.tag ||
                credDefData?.tag ||
                '';

              return {
                cred_def_id: credDefId,
                schema_id: credDefData?.credential_definition?.schemaId || '',
                tag: tag,
                support_revocation: Boolean(revocationSupport),
                created_at:
                  credDefData?.credential_definition_metadata?.created_at,
              } as CredDefStorageRecord;
            } catch (err) {
              console.error(
                'Failed to fetch anoncreds credential definition',
                { cred_def_id: credDefId, error: err }
              );
              return null;
            }
          });

          const credDefResults = await Promise.allSettled(credDefPromises);
          anoncredsCredDefs.push(
            ...credDefResults
              .filter(
                (
                  result
                ): result is PromiseFulfilledResult<CredDefStorageRecord> =>
                  result.status === 'fulfilled' && result.value !== null
              )
              .map((result) => result.value)
          );
        }
      }

      // Merge and deduplicate by cred_def_id
      const credDefMap = new Map<string, CredDefStorageRecord>();

      // Add Indy cred defs first
      indyCredDefs.forEach((credDef) => {
        if (credDef?.cred_def_id) {
          credDefMap.set(credDef.cred_def_id, credDef);
        }
      });

      // Add AnonCreds cred defs (will overwrite if duplicate)
      anoncredsCredDefs.forEach((credDef) => {
        if (credDef?.cred_def_id) {
          credDefMap.set(credDef.cred_def_id, credDef);
        }
      });

      storedCredDefs.value = Array.from(credDefMap.values());
    } catch (err) {
      console.error(err);
      error.value = err;
    } finally {
      loading.value = false;
    }
  }

  async function listAnoncredsCredentialDefinitions() {
    storedCredDefs.value = [];
    error.value = null;
    loading.value = true;

    try {
      // Fetch list of credential definition IDs
      const credDefsResponse = await acapyApi.getHttp(
        API_PATH.ANONCREDS_CREDENTIAL_DEFINITIONS
      );

      // Handle both direct data and axios response structure
      const responseData = credDefsResponse?.data || credDefsResponse;
      const credDefIds =
        (responseData as { credential_definition_ids?: string[] })
          ?.credential_definition_ids || [];

      // If no credential definitions found, return early
      if (!credDefIds || credDefIds.length === 0) {
        storedCredDefs.value = [];
        return;
      }

      // Fetch full credential definition details for each ID
      const credDefPromises = credDefIds.map(async (credDefId: string) => {
        try {
          // URL encode the credential definition ID for use in the path parameter
          const encodedCredDefId = encodeURIComponent(credDefId);
          const credDefUrl = `/anoncreds/credential-definition/${encodedCredDefId}`;

          const credDefResponse = await acapyApi.getHttp(credDefUrl);
          const credDefData = credDefResponse?.data || credDefResponse;

          // Map to CredDefStorageRecord format
          // Check for revocation support
          // In AnonCreds, revocation is indicated by the presence of a revocation object
          // in credential_definition.value.revocation
          const hasRevocationObject =
            credDefData?.credential_definition?.value?.revocation !==
              undefined &&
            credDefData.credential_definition.value.revocation !== null;

          // Also check other possible locations
          const revocationSupport =
            hasRevocationObject ||
            credDefData?.credential_definition?.revocation !== undefined ||
            credDefData?.options?.support_revocation === true ||
            credDefData?.support_revocation === true;

          // Extract tag from credential definition - check multiple possible locations
          const tag =
            credDefData?.credential_definition?.tag || credDefData?.tag || '';

          return {
            cred_def_id: credDefId,
            schema_id: credDefData?.credential_definition?.schemaId || '',
            tag: tag,
            support_revocation: Boolean(revocationSupport),
            created_at: credDefData?.credential_definition_metadata?.created_at,
          } as CredDefStorageRecord;
        } catch (_err) {
          // Return minimal record if fetch fails
          return {
            cred_def_id: credDefId,
            schema_id: '',
            tag: '',
            support_revocation: false,
            created_at: undefined,
          } as CredDefStorageRecord;
        }
      });

      // Use Promise.allSettled to handle individual failures
      const credDefResults = await Promise.allSettled(credDefPromises);

      // Extract only successfully fetched credential definitions
      storedCredDefs.value = credDefResults
        .filter(
          (result): result is PromiseFulfilledResult<CredDefStorageRecord> =>
            result.status === 'fulfilled'
        )
        .map((result) => result.value)
        .filter((cd) => cd.cred_def_id); // Filter out any invalid entries
    } catch (err) {
      console.error(err);
      error.value = err;
    } finally {
      loading.value = false;
    }
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
      .then(async () => {
        // Extract schema_id from response
        const schemaId = result?.schema_state?.schema_id;

        if (!schemaId) {
          console.warn('No schema_id found in response, cannot verify storage');
          return;
        }

        // Wait a bit for event handler to complete (if it runs)
        await new Promise((resolve) => setTimeout(resolve, 1500));

        // Refresh the stored schema list
        await listStoredSchemas();

        // Check if schema is in storage after refresh
        const storedSchema = storedSchemas.value.find(
          (s: any) => s.schema_id === schemaId
        );

        if (!storedSchema) {
          // Schema not in storage, manually add it via storage endpoint
          console.log(
            `Schema ${schemaId} not found in storage after event handler, manually adding...`
          );
          try {
            await addSchemaFromLedgerToStorage({ schema_id: schemaId });
            // Refresh again after manual add
            await listStoredSchemas();
          } catch (err) {
            console.error(
              `Failed to manually add schema ${schemaId} to storage:`,
              err
            );
            // Don't throw - schema was created successfully, just storage failed
          }
        } else {
          console.log(`Schema ${schemaId} found in storage`);
        }
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

  async function addCredDefFromLedgerToStorage(payload: {
    cred_def_id: string;
  }) {
    console.log('> governanceStore.addCredDefFromLedgerToStorage');
    error.value = null;
    loading.value = true;

    let result = null;

    await acapyApi
      .postHttp(API_PATH.CREDENTIAL_DEFINITION_STORAGE, payload)
      .then((res) => {
        result = res.data;
        console.log(result);
      })
      .then(() => {
        listStoredCredentialDefinitions();
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< governanceStore.addCredDefFromLedgerToStorage');

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
      .then(async () => {
        // Extract cred_def_id from response
        const credDefId =
          result?.credential_definition_state?.credential_definition_id;

        if (!credDefId) {
          console.warn(
            'No cred_def_id found in response, cannot verify storage'
          );
          return;
        }

        // Wait a bit for event handler to complete (if it runs)
        await new Promise((resolve) => setTimeout(resolve, 1500));

        // Refresh the credential definition list
        await listStoredCredentialDefinitions();

        // Check if credential definition is in storage after refresh
        const storedCredDef = storedCredDefs.value.find(
          (c: any) => c.cred_def_id === credDefId
        );

        if (!storedCredDef) {
          // Cred def not in storage, manually add it via storage endpoint
          console.log(
            `Credential definition ${credDefId} not found in storage after event handler, manually adding...`
          );
          try {
            await addCredDefFromLedgerToStorage({ cred_def_id: credDefId });
            // Refresh again after manual add
            await listStoredCredentialDefinitions();
          } catch (err) {
            console.error(
              `Failed to manually add credential definition ${credDefId} to storage:`,
              err
            );
            // Don't throw - cred def was created successfully, just storage failed
          }
        } else {
          console.log(`Credential definition ${credDefId} found in storage`);
        }
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
    addCredDefFromLedgerToStorage,
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
    listAllCredDefsForAnoncredsWallet,
    listAllSchemasForAnoncredsWallet,
    listAnoncredsCredentialDefinitions,
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
