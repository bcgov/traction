import {
  AddOcaRecordRequest,
  CredDefStorageRecord,
  CredentialDefinitionSendRequest,
  OcaRecord,
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
    listOcas,
    listStoredCredentialDefinitions,
    listStoredSchemas,
    setSelectedSchemaById,
  };
});

export default {
  useGovernanceStore,
};
