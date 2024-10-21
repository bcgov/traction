<template>
  <MainCardContent
    :title="$t('issue.credentials')"
    :refresh-callback="loadTable"
  >
    <DataTable
      v-model:selection="selectedCredential"
      v-model:filters="filter"
      v-model:expanded-rows="expandedRows"
      :loading="loading"
      :value="formattedIssuedCredentials"
      :paginator="true"
      :rows="TABLE_OPT.ROWS_DEFAULT"
      :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
      selection-mode="single"
      data-key="credential_exchange_id"
      sort-field="created_at"
      :sort-order="-1"
      filter-display="menu"
    >
      <template #header>
        <div class="flex justify-content-between">
          <div class="flex justify-content-start">
            <OfferCredential
              v-if="
                stringOrBooleanTruthy(config.frontend.showWritableComponents)
              "
            />
          </div>
          <div class="flex justify-content-end">
            <IconField icon-position="left">
              <InputIcon><i class="pi pi-search" /></InputIcon>
              <InputText
                v-model="filter.global.value"
                placeholder="Search Credentials"
              />
            </IconField>
          </div>
        </div>
      </template>
      <template #empty>{{ $t('common.noRecordsFound') }}</template>
      <template #loading>{{ $t('common.loading') }}</template>
      <Column :expander="true" header-style="width: 3rem" />
      <Column header="Actions">
        <template #body="{ data }">
          <DeleteCredentialExchangeButton
            v-if="stringOrBooleanTruthy(config.frontend.showWritableComponents)"
            :cred-exch-id="data.credential_exchange_id"
          />

          <RevokeCredentialButton
            v-if="stringOrBooleanTruthy(config.frontend.showWritableComponents)"
            :cred-exch-record="data"
            :connection-display="findConnectionName(data.connection_id) ?? ''"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="credential_definition_id"
        header="Credential Definition"
        filter-field="credential_definition_id"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By Credential Definition"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="connection"
        header="Connection"
        filter-field="Connection"
        :show-filter-match-modes="false"
      >
        <template #body="{ data }">
          <LoadingLabel :value="data.connection" />
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By Connection"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="state"
        header="Status"
        filter-field="state"
        :show-filter-match-modes="false"
      >
        <template #body="{ data }">
          <StatusChip :status="data.state" />
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By Status"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="created"
        header="Created at"
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
            placeholder="Search By Time"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <template #expansion="{ data }">
        <RowExpandData
          :id="data.credential_exchange_id"
          :url="API_PATH.ISSUE_CREDENTIAL_20_RECORDS"
        />
      </template>
    </DataTable>
  </MainCardContent>
</template>

<script setup lang="ts">
// Types
import { ExtendedV20CredExRecordByFormat } from '@/types';

// Vue
import { computed, onMounted, ref } from 'vue';
// State
import { useConnectionStore, useIssuerStore } from '@/store';
import { storeToRefs } from 'pinia';
import { useConfigStore } from '@/store/configStore';
// PrimeVue/etc
import { FilterMatchMode } from 'primevue/api';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import InputIcon from 'primevue/inputicon';
import IconField from 'primevue/iconfield';
import { useToast } from 'vue-toastification';
// Other Components
import { stringOrBooleanTruthy } from '@/helpers';
import { formatIssuedCredentials } from '@/helpers/tableFormatters';
import { API_PATH, TABLE_OPT } from '@/helpers/constants';
import LoadingLabel from '@/components/common/LoadingLabel.vue';
import RowExpandData from '@/components/common/RowExpandData.vue';
import StatusChip from '@/components/common/StatusChip.vue';
import MainCardContent from '@/components/layout/mainCard/MainCardContent.vue';
import DeleteCredentialExchangeButton from './DeleteCredentialExchangeButton.vue';
import RevokeCredentialButton from './RevokeCredentialButton.vue';
import OfferCredential from './OfferCredential.vue';

const { config } = storeToRefs(useConfigStore());

const toast = useToast();

const { listConnections, findConnectionName } = useConnectionStore();
const { connections } = storeToRefs(useConnectionStore());
const issuerStore = useIssuerStore();
// use the loading state from the store to disable the button...
const { loading, credentials, selectedCredential } =
  storeToRefs(useIssuerStore());

const formattedIssuedCredentials = computed(() =>
  formatIssuedCredentials(credentials, findConnectionName)
);

// Get the credentials
const loadTable = async () => {
  await issuerStore.listCredentials().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });

  // Load connections if not already there for display
  if (!connections.value || !connections.value.length) {
    listConnections().catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
  }
};

onMounted(async () => {
  await loadTable();
});

// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);

// Filter for search
const filter = ref({
  global: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  connection: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  credential_definition_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  created: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
});
</script>
