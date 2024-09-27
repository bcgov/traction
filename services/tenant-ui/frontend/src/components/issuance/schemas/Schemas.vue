<template>
  <MainCardContent
    :title="$t('configuration.schemas.stored')"
    :refresh-callback="loadTable"
  >
    <DataTable
      v-model:selection="selectedSchema"
      v-model:expanded-rows="expandedRows"
      v-model:filters="filter"
      :loading="loading"
      :value="formattedSchemaList"
      :paginator="true"
      :rows="TABLE_OPT.ROWS_DEFAULT"
      :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
      :global-filter-fields="['schema_id', 'version']"
      selection-mode="single"
      data-key="schema_id"
      sort-field="created_at"
      :sort-order="-1"
      filter-display="menu"
    >
      <template #header>
        <div class="flex justify-content-between">
          <div
            v-if="stringOrBooleanTruthy(config.frontend.showWritableComponents)"
            class="flex justify-content-start"
          >
            <CreateSchema :table-reload="loadTable" />
            <AddSchemaFromLedger />
          </div>
          <div class="flex justify-content-end">
            <IconField icon-position="left">
              <InputIcon><i class="pi pi-search" /></InputIcon>
              <InputText
                v-model="filter.schema_id.value"
                :placeholder="t('configuration.search.schemas')"
              />
            </IconField>
          </div>
        </div>
      </template>
      <template #empty>{{ $t('common.noRecordsFound') }}</template>
      <template #loading>{{ $t('common.loading') }}</template>
      <Column :expander="true" header-style="width: 3rem" />
      <Column :sortable="false" :header="t('configuration.search.actions')">
        <template #body="{ data }">
          <div
            v-if="stringOrBooleanTruthy(config.frontend.showWritableComponents)"
          >
            <Button
              :title="t('configuration.schemas.delete')"
              icon="pi pi-trash"
              class="p-button-rounded p-button-icon-only p-button-text"
              @click="deleteSchema($event, data)"
            />
            <CopySchema :stored-schema="data" :table-reload="loadTable" />
          </div>
        </template>
      </Column>
      <Column
        :sortable="true"
        field="schema.name"
        :header="t('configuration.search.name')"
        filter-field="schema.name"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            :placeholder="t('configuration.search.byName')"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="schema_id"
        header="Schema ID"
        filter-field="schema_id"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            :placeholder="t('configuration.search.bySchemaId')"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="schema.version"
        :header="t('configuration.search.version')"
        filter-field="schema.version"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            :placeholder="t('configuration.search.byVersion')"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="schema.attrNames"
        :header="t('configuration.search.attributes')"
        filter-field="schema.attrNames"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            :placeholder="t('configuration.search.byAttributes')"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="created"
        :header="t('configuration.search.createdAt')"
        filter-field="created"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            :placeholder="t('configuration.search.byDate')"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="credential_templates"
        :header="t('configuration.credentialDefinitions.title')"
      >
        <template #body="{ data }">
          <NestedCredentialDefinition
            :schema="data"
            :table-reload="loadTable"
          />
        </template>
      </Column>
      <template #expansion="{ data }">
        <RowExpandData :id="data.schema_id" :url="API_PATH.SCHEMA_STORAGE" />
      </template>
    </DataTable>
  </MainCardContent>
</template>

<script setup lang="ts">
// Libraries
import { storeToRefs } from 'pinia';
import { FilterMatchMode } from 'primevue/api';
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import InputIcon from 'primevue/inputicon';
import IconField from 'primevue/iconfield';
import { useConfirm } from 'primevue/useconfirm';
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useToast } from 'vue-toastification';
// Source
import RowExpandData from '@/components/common/RowExpandData.vue';
import NestedCredentialDefinition from '@/components/issuance/credentialDefinitions/NestedCredentialDefinition.vue';
import MainCardContent from '@/components/layout/mainCard/MainCardContent.vue';
import { stringOrBooleanTruthy } from '@/helpers';
import { API_PATH, TABLE_OPT } from '@/helpers/constants';
import { formatSchemaList } from '@/helpers/tableFormatters';
import { useGovernanceStore } from '@/store';
import { useConfigStore } from '@/store/configStore';
import { SchemaStorageRecord } from '@/types';
import AddSchemaFromLedger from './AddSchemaFromLedger.vue';
import CopySchema from './CopySchema.vue';
import CreateSchema from './CreateSchema.vue';

const { t } = useI18n();
const confirm = useConfirm();
const toast = useToast();

const { config } = storeToRefs(useConfigStore());
const governanceStore = useGovernanceStore();
const { loading, schemaList, selectedSchema } =
  storeToRefs(useGovernanceStore());

const formattedSchemaList = computed(() => formatSchemaList(schemaList));

// Loading the schema list and the stored cred defs
const loadTable = async () => {
  try {
    await governanceStore.listStoredSchemas();
    // Wait til schemas are loaded so the getter can map together the schemas to creds
    await governanceStore.listStoredCredentialDefinitions();
  } catch (err) {
    console.error(err);
    toast.error(`Failure: ${err}`);
  }
};

// Deleting a stored schema
const deleteSchema = (event: any, schema: SchemaStorageRecord) => {
  confirm.require({
    target: event.currentTarget,
    message: t('configuration.schemas.confirmDelete'),
    header: t('common.confirmation'),
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      governanceStore
        .deleteSchema(schema.schema_id)
        .then(() => {
          toast.success(t('configuration.schemas.deleteSuccess'));
        })
        .catch((err) => {
          console.error(err);
          toast.error(`Failure: ${err}`);
        });
    },
  });
};

// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);

const filter = ref({
  schema_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  'schema.name': {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  'schema.version': {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  'schema.attrNames': {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  created: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
});

// Lifecycle hooks
onMounted(async () => {
  loadTable();
});

onBeforeUnmount(() => {
  selectedSchema.value = undefined;
});
</script>

<style scoped>
.row.buttons {
  float: right;
  margin: 3rem 1rem 0 0;
}
</style>
