<template>
  <MainCardContent
    :title="$t('verifier.verifications')"
    :refresh-callback="loadTable"
  >
    <DataTable
      v-model:selection="selectedPresentation"
      v-model:filters="filter"
      v-model:expandedRows="expandedRows"
      :loading="loading"
      :value="presentations"
      data-key="presentation_exchange_id"
      :paginator="true"
      :global-filter-fields="[
        'presentation_request.name',
        'presentation_request_dict.comment',
      ]"
      :rows="TABLE_OPT.ROWS_DEFAULT"
      :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
      selection-mode="single"
      sort-field="created_at"
      :sort-order="-1"
    >
      <template #header>
        <div class="flex justify-content-between">
          <div class="flex justify-content-start">
            <CreateRequest
              v-if="
                stringOrBooleanTruthy(config.frontend.showWritableComponents)
              "
            />
          </div>

          <div class="flex justify-content-end">
            <span class="p-input-icon-left">
              <i class="pi pi-search" />
              <InputText
                v-model="filter['global'].value"
                placeholder="Search Verifications"
              />
            </span>
          </div>
        </div>
      </template>
      <template #empty>{{ $t('common.noRecordsFound') }}</template>
      <template #loading>{{ $t('common.loading') }}</template>
      <Column :expander="true" header-style="width: 3rem" />
      <Column :sortable="false" :header="$t('common.actions')">
        <template #body="{ data }">
          <div class="flex">
            <DeleteExchangeRecord
              v-if="
                stringOrBooleanTruthy(config.frontend.showWritableComponents)
              "
              :record-id="data.presentation_exchange_id"
            />
            <CreateRequest
              v-if="
                data.role === 'verifier' &&
                stringOrBooleanTruthy(config.frontend.showWritableComponents)
              "
              :existing-pres-req="data.presentation_request"
              icon-display
            />
          </div>
        </template>
      </Column>
      <Column
        :sortable="true"
        field="presentation_request.name"
        header="Name"
      />
      <Column :sortable="true" field="role" header="Role" />
      <Column :sortable="true" field="connection_id" header="Connection">
        <template #body="{ data }">
          <LoadingLabel :value="findConnectionName(data.connection_id)" />
        </template>
      </Column>
      <Column :sortable="true" field="status" header="Status">
        <template #body="{ data }">
          <StatusChip :status="data.state" />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="presentation_request_dict.comment"
        header="Comment"
      />
      <Column :sortable="true" field="created_at" header="Created at">
        <template #body="{ data }">
          {{ formatDateLong(data.created_at) }}
        </template>
      </Column>
      <template #expansion="{ data }">
        <!-- <PresentationRowExpandData
        :row="data"
        :header="false"
        :show-information="true"
      /> -->
        <RowExpandData
          :id="data.presentation_exchange_id"
          :url="API_PATH.PRESENT_PROOF_RECORDS"
        />
      </template>
    </DataTable>
  </MainCardContent>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref } from 'vue';
// PrimeVue
import { FilterMatchMode } from 'primevue/api';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { useToast } from 'vue-toastification';
// State
import { useConnectionStore, useVerifierStore } from '@/store';
import { storeToRefs } from 'pinia';
import { useConfigStore } from '@/store/configStore';
// Components
import MainCardContent from '@/components/layout/mainCard/MainCardContent.vue';
import CreateRequest from './createPresentationRequest/CreateRequest.vue';
import DeleteExchangeRecord from './DeleteExchangeRecord.vue';
import LoadingLabel from '@/components/common/LoadingLabel.vue';
import RowExpandData from '@/components/common/RowExpandData.vue';
import StatusChip from '@/components/common/StatusChip.vue';
import { formatDateLong, stringOrBooleanTruthy } from '@/helpers';
import { API_PATH, TABLE_OPT } from '@/helpers/constants';

const toast = useToast();

// State
const { listConnections, findConnectionName } = useConnectionStore();
const verifierStore = useVerifierStore();
const { connections } = storeToRefs(useConnectionStore());
const { loading, presentations, selectedPresentation } =
  storeToRefs(useVerifierStore());
const { config } = storeToRefs(useConfigStore());

const loadTable = async () => {
  verifierStore.listPresentations().catch((err) => {
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
  loadTable();
});

// used by datatable expander behind the scenes
const expandedRows = ref([]);

const filter = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
});
</script>
