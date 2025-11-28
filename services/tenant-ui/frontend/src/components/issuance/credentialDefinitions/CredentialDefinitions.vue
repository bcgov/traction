<template>
  <MainCardContent
    :title="$t('configuration.credentialDefinitions.stored')"
    :refresh-callback="loadTable"
  >
    <DataTable
      v-model:selection="selectedCredentialDefinition"
      v-model:expanded-rows="expandedRows"
      v-model:filters="filter"
      :loading="loading"
      :value="formattedstoredCredDefs"
      :paginator="true"
      :rows="TABLE_OPT.ROWS_DEFAULT"
      :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
      selection-mode="single"
      data-key="cred_def_id"
      sort-field="created_at"
      :sort-order="-1"
      filter-display="menu"
    >
      <template #header>
        <div class="flex justify-content-between">
          <div class="flex justify-content-start">
            <div
              v-if="
                stringOrBooleanTruthy(config.frontend.showWritableComponents)
              "
              class="flex justify-content-start"
            >
              <CreateCredentialDefinition :table-reload="loadTable" />
            </div>
          </div>
          <div class="flex justify-content-end">
            <IconField icon-position="left">
              <InputIcon><i class="pi pi-search" /></InputIcon>
              <InputText
                v-model="filter.global.value"
                :placeholder="t('configuration.search.credDefs')"
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
              :title="t('configuration.credentialDefinitions.delete')"
              icon="pi pi-trash"
              class="p-button-rounded p-button-icon-only p-button-text"
              @click="deleteCredDef($event, data.cred_def_id)"
            />
            <Button
              :title="t('configuration.credentialDefinitions.copy')"
              icon="pi pi-copy"
              class="p-button-rounded p-button-icon-only p-button-text"
              @click="openCopyModal(data)"
            />
          </div>
        </template>
      </Column>
      <Column
        :sortable="true"
        field="cred_def_id"
        header="ID"
        filter-field="cred_def_id"
        :show-filter-match-modes="false"
      >
        <template #body="{ data }">
          <span
            v-tooltip="data.cred_def_id"
            :title="data.cred_def_id"
            class="truncated-id"
          >
            {{ truncateId(data.cred_def_id) }}
          </span>
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            :placeholder="t('configuration.search.byId')"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="schema_id"
        :header="$t('configuration.schemas.id')"
        filter-field="schema_id"
        :show-filter-match-modes="false"
      >
        <template #body="{ data }">
          <div
            v-tooltip="data.schema_id"
            class="schema-link"
            :title="data.schema_id"
            @click="navigateToSchema(data)"
          >
            {{ truncateId(data.schema_id) }}
          </div>
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            :placeholder="$t('configuration.search.bySchemaId')"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="tag"
        header="Tag"
        filter-field="tag"
        :show-filter-match-modes="false"
      >
        <template #body="{ data }">
          {{ data.tag || '-' }}
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            :placeholder="t('configuration.search.byTag')"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="support_revocation"
        :header="$t('configuration.credentialDefinitions.revokable')"
      >
        <template #body="{ data }">
          <span v-if="data.support_revocation">
            <i class="pi pi-check-circle"></i>
          </span>
        </template>
      </Column>
      <Column
        :sortable="true"
        field="created"
        :header="t('configuration.search.createdAt')"
        filter-field="created"
        :show-filter-match-modes="false"
      >
        <template #body="{ data }">
          {{ data.created }}
        </template>
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
      <template #expansion="{ data }">
        <RowExpandData
          :id="data.cred_def_id"
          :url="API_PATH.CREDENTIAL_DEFINITION_STORAGE"
        />
      </template>
    </DataTable>
  </MainCardContent>
  <Dialog
    v-model:visible="displayModal"
    :header="t('configuration.credentialDefinitions.copy')"
    :modal="true"
    :style="{ minWidth: '400px' }"
  >
    <CopyCredentialDefinitionForm @closed="handleCopyModalClose" />
  </Dialog>
</template>

<script setup lang="ts">
// Libraries
import { storeToRefs } from 'pinia';
import { FilterMatchMode } from 'primevue/api';
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import InputIcon from 'primevue/inputicon';
import IconField from 'primevue/iconfield';
import { useConfirm } from 'primevue/useconfirm';
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
// Source
import RowExpandData from '@/components/common/RowExpandData.vue';
import MainCardContent from '@/components/layout/mainCard/MainCardContent.vue';
import { stringOrBooleanTruthy, truncateId } from '@/helpers';
import { API_PATH, TABLE_OPT } from '@/helpers/constants';
import { formatStoredCredDefs } from '@/helpers/tableFormatters';
import { useGovernanceStore, useTenantStore } from '@/store';
import { useConfigStore } from '@/store/configStore';
import {
  CredDefStorageRecord,
  CredentialDefinitionSendRequest,
} from '@/types/acapyApi/acapyInterface';
import CopyCredentialDefinitionForm from './CopyCredentialDefinitionForm.vue';
import CreateCredentialDefinition from './CreateCredentialDefinition.vue';
import checkCredDefPostedInterval from './checkCredDefPostedInterval';

const confirm = useConfirm();
const toast = useToast();
const router = useRouter();
const { t } = useI18n();

const { config } = storeToRefs(useConfigStore());
const governanceStore = useGovernanceStore();
const tenantStore = useTenantStore();
const { loading, storedCredDefs, selectedCredentialDefinition } =
  storeToRefs(useGovernanceStore());
const { tenantWallet } = storeToRefs(useTenantStore());

// Check if wallet is askar-anoncreds
const isAskarAnoncredsWallet = computed(() => {
  return tenantWallet?.value?.settings?.['wallet.type'] === 'askar-anoncreds';
});

const formattedstoredCredDefs = computed(() =>
  formatStoredCredDefs(storedCredDefs)
);

// LOADING the schema list and the stored cred defs
const loadTable = async () => {
  try {
    if (isAskarAnoncredsWallet.value) {
      // For askar-anoncreds wallets, use AnonCreds endpoints
      await governanceStore.listAnoncredsSchemas();
      await governanceStore.listAnoncredsCredentialDefinitions();
    } else {
      // For askar wallets, use regular endpoints
      await governanceStore.listStoredSchemas();
      // Wait til schemas are loaded so the getter can map together the schems to creds
      await governanceStore.listStoredCredentialDefinitions();
    }
  } catch (err) {
    console.error(err);
    toast.error(`Failure: ${err}`);
  }
};

onMounted(async () => {
  // Ensure tenant wallet is loaded to check wallet type
  if (!tenantWallet?.value && tenantStore.getTenantSubWallet) {
    await tenantStore.getTenantSubWallet();
  }
  loadTable();
});

// Deleting a stored schema
const deleteCredDef = (event: any, id: string) => {
  confirm.require({
    target: event.currentTarget,
    message: t('configuration.credentialDefinitions.confirmDelete'),
    header: t('common.confirmation'),
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      governanceStore
        .deleteStoredCredentialDefinition(id)
        .then(() => {
          toast.success(t('configuration.credentialDefinitions.deleteSuccess'));
        })
        .catch((err) => {
          console.error(err);
          toast.error(`Failure: ${err}`);
        });
    },
  });
};

// Modal
const displayModal = ref(false);
const openCopyModal = async (credDef: CredDefStorageRecord) => {
  selectedCredentialDefinition.value = credDef;
  displayModal.value = true;
};
const handleCopyModalClose = async (
  credDef: CredentialDefinitionSendRequest
) => {
  displayModal.value = false;
  checkCredDefPostedInterval(
    credDef,
    governanceStore.getStoredCredDefs,
    loadTable,
    t('configuration.credentialDefinitions.postFinished'),
    selectedCredentialDefinition
  );
};

const navigateToSchema = (data: any) => {
  governanceStore.setSelectedSchemaById(data.schema_id);
  router.push({ name: 'Schemas' });
};

// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);

// Filter for search
const filter = ref({
  global: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  cred_def_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  schema_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  created: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
});

onUnmounted(() => {
  selectedCredentialDefinition.value = undefined;
});
</script>

<style scoped>
.row.buttons {
  float: right;
  margin: 3rem 1rem 0 0;
}
.schema-link:hover {
  text-shadow: 0 0 1px black;
}
</style>
