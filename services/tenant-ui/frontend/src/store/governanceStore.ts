import { API_PATH } from '@/helpers/constants';
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { useAcapyApi } from './acapyApi';
import {
  fetchItem,
  fetchList,
  filterByStatusActive,
  filterMapSortList,
  sortByLabelAscending,
} from './utils';

export const useGovernanceStore = defineStore('governance', () => {
  // state
  const storedSchemas: any = ref([]);
  const selectedSchema: any = ref(null);
  // const schemaTemplateFilters: any = ref(null);

  const credentialDefinitions: any = ref([
    {
      schema_id: 'HhVXFoPyMCsW2HiXDPvRZG:2:fvxcvcx:1.2.3',
      state: 'Pending',
      name: 'Name',
      tag: 'Tag',
    },
  ]);
  const selectedCredentialDefinition: any = ref(null);
  // const credentialTemplateFilters: any = ref(null);

  const loading: any = ref(false);
  const error: any = ref(null);

  // getters

  const schemaList = computed(() => {
    // For the list of schemas in the schema table, add cred defs
    return storedSchemas.value.map((s: any) => {
      s.credentialDefinition = credentialDefinitions.value.find(
        (c: any) => c.schema_id === s.schema_id
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
        label: `${item.name}`,
        value: item.credential_template_id,
        status: item.status,
      };
    }
    return result;
  };

  const schemaTemplateDropdown = computed(() => {
    return filterMapSortList(
      storedSchemas.value,
      schemaLabelValue,
      sortByLabelAscending,
      filterByStatusActive
    );
  });

  const credentialDropdown = computed(() => {
    return filterMapSortList(
      credentialDefinitions.value,
      credDefLabelValue,
      sortByLabelAscending,
      filterByStatusActive
    );
  });

  // actions

  const acapyApi = useAcapyApi();

  async function listStoredSchemas() {
    selectedSchema.value = null;
    storedSchemas.value = null;
    return fetchList(API_PATH.SCHEMA_STORAGE, storedSchemas, error, loading);
  }

  async function listStoredCredentialDefinitions() {
    selectedCredentialDefinition.value = null;
    credentialDefinitions.value = null;
    return fetchList(
      API_PATH.CREDENTIAL_DEFINITION_STORAGE,
      credentialDefinitions,
      error,
      loading
    );
  }

  async function createSchema(payload: any = {}) {
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

  async function createCredentialTemplate(payload: any = {}) {
    console.log('> governanceStore.createCredentialTemplate');
    error.value = null;
    loading.value = true;

    let result = null;

    await acapyApi
      .postHttp(API_PATH.GOVERNANCE_CREDENTIAL_TEMPLATES, payload)
      .then((res) => {
        console.log(res);
        result = res.data.item;
        console.log(result);
      })
      .then(() => {
        // do we want to automatically reload? or have the caller of this to load?
        console.log(
          'credential template created. the store calls load automatically, but do we want this done "manually"?'
        );
        // load schemas for tables...
        listStoredSchemas();
      })
      .then(() => {
        // reload this for pick lists...
        listStoredCredentialDefinitions();
      })
      .catch((err) => {
        error.value = err;
        // console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< governanceStore.createCredentialTemplate');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  async function copySchema(payload: any = {}) {
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
      API_PATH.GOVERNANCE_CREDENTIAL_TEMPLATES,
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

  return {
    loading,
    error,
    storedSchemas,
    selectedSchema,
    schemaList,
    // schemaTemplateFilters,
    credentialDefinitions,
    selectedCredentialDefinition,
    // credentialTemplateFilters,
    schemaTemplateDropdown,
    credentialDropdown,
    listStoredSchemas,
    createSchema,
    copySchema,
    deleteSchema,
    // getSchemaTemplate,
    listStoredCredentialDefinitions,
    createCredentialTemplate,
    getCredentialTemplate,
  };
});

export default {
  useGovernanceStore,
};
