import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { useTenantApi } from './tenantApi';
import { fetchList, filterMapSortList, sortByLabelAscending } from './utils';

export const useGovernanceStore = defineStore('governance', () => {
  // state
  const schemaTemplates: any = ref(null);
  const selectedSchemaTemplate: any = ref(null);
  const schemaTemplateFilters: any = ref(null);

  const credentialTemplates: any = ref(null);
  const selectedCredentialTemplate: any = ref(null);
  const credentialTemplateFilters: any = ref(null);

  const loading: any = ref(false);
  const error: any = ref(null);

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
      schemaTemplates.value,
      schemaLabelValue,
      sortByLabelAscending
    );
  });

  const credentialTemplateDropdown = computed(() => {
    return filterMapSortList(
      credentialTemplates.value,
      credDefLabelValue,
      sortByLabelAscending
    );
  });

  // grab the tenant api
  const tenantApi = useTenantApi();

  async function listSchemaTemplates() {
    selectedSchemaTemplate.value = null;
    schemaTemplates.value = null;
    //return fetchList('/tenant/v1/governance/schema_templates/', schemaTemplates, error, loading);

    // this is a total hack for expedience, lets get cred templates at the same time...
    // just so we can show it all in one grid, this should happen at the api level...
    const schemas = ref();
    await fetchList(
      '/tenant/v1/governance/schema_templates/',
      schemas,
      error,
      loading
    );
    await listCredentialTemplates();
    schemaTemplates.value = await Promise.all(
      schemas.value.map(async (item: any) => {
        // find any credential templates...
        const templates = ref();
        await fetchList(
          '/tenant/v1/governance/credential_templates/',
          templates,
          error,
          loading,
          { schema_template_id: item.schema_template_id }
        );
        return {
          ...item,
          credential_templates: templates,
        };
      })
    );
    return schemaTemplates.value;
  }

  async function listCredentialTemplates() {
    selectedCredentialTemplate.value = null;
    return fetchList(
      '/tenant/v1/governance/credential_templates/',
      credentialTemplates,
      error,
      loading
    );
  }

  async function createSchemaTemplate(payload: any = {}) {
    console.log('> governanceStore.createSchemaTemplate');
    error.value = null;
    loading.value = true;

    let result = null;

    await tenantApi
      .postHttp('/tenant/v1/governance/schema_templates/', payload)
      .then((res) => {
        console.log(res);
        result = res.data.item;
        console.log(result);
      })
      .then(() => {
        // do we want to automatically reload? or have the caller of this to load?
        console.log(
          'schema template created. the store calls load automatically, but do we want this done "manually"?'
        );
        listSchemaTemplates();
      })
      .catch((err) => {
        error.value = err;
        //console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< governanceStore.createSchemaTemplate');

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

    await tenantApi
      .postHttp('/tenant/v1/governance/credential_templates/', payload)
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
        // TODO: for demo, we aren't separating schema/cred templates, so load the schema list (that has sub-list of cred templates.)
        //listCredentialTemplates();
        listSchemaTemplates();
      })
      .catch((err) => {
        error.value = err;
        //console.log(error.value);
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

    await tenantApi
      .postHttp('/tenant/v1/governance/schema_templates/import', payload)
      .then((res) => {
        console.log(res);
        result = res.data.item;
        console.log(result);
      })
      .then(() => {
        console.log(
          'schema copied. the store calls load automatically, but do we want this done "manually"?'
        );
        listSchemaTemplates();
      })
      .catch((err) => {
        error.value = err;
        //console.log(error.value);
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

  async function getSchemaTemplate(id: String, params: any = {}) {
    console.log('> governanceStore.getSchemaTemplate');
    error.value = null;
    loading.value = true;

    let result = null;

    await tenantApi
      .getHttp(`/tenant/v1/governance/schema_templates/${id}`, params)
      .then((res) => {
        console.log(res);
        result = res.data.item;
        console.log(result);
      })
      .catch((err) => {
        error.value = err;
        //console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< governanceStore.getSchemaTemplate');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  async function getCredentialTemplate(id: String, params: any = {}) {
    console.log('> governanceStore.getCredentialTemplate');
    error.value = null;
    loading.value = true;

    let result = null;

    await tenantApi
      .getHttp(`/tenant/v1/governance/credential_templates/${id}`, params)
      .then((res) => {
        console.log(res);
        result = res.data.item;
        console.log(result);
      })
      .catch((err) => {
        error.value = err;
        //console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< governanceStore.getCredentialTemplate');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  /**
   * # delete Schema
   * Delete a schema template
   * @param payload Data object of schema row entry
   */
  async function deleteSchema(payload: any = {}) {
    console.log('> governanceStore.deleteSchema');

    // Need the UUID to delete the schema
    const schemaId = payload.schema_template_id;

    error.value = null;
    loading.value = true;

    let result = null;

    await tenantApi
      .deleteHttp(`/tenant/v1/governance/schema_templates/${schemaId}`, payload)
      .then((res) => {
        result = res.data.item;
      })
      .then(() => {
        console.log('schema deleted.');
        listSchemaTemplates(); // Refresh table
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
    schemaTemplates,
    selectedSchemaTemplate,
    schemaTemplateFilters,
    credentialTemplates,
    selectedCredentialTemplate,
    credentialTemplateFilters,
    loading,
    error,
    schemaTemplateDropdown,
    credentialTemplateDropdown,
    listSchemaTemplates,
    createSchemaTemplate,
    copySchema,
    deleteSchema,
    getSchemaTemplate,
    listCredentialTemplates,
    createCredentialTemplate,
    getCredentialTemplate,
  };
});

export default {
  useGovernanceStore,
};
