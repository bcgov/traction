<template>
  <h3 class="mt-0">Messages</h3>
  <DataTable
    v-model:expandedRows="expandedRows"
    v-model:selection="selectedMessage"
    :loading="loading"
    :paginator="true"
    :rows="10"
    :value="messages"
    selection-mode="single"
    data-key="message_id"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start">
          <SuperYou
            :api-url="apiUrl"
            :template-json="templateJson"
            text="Create a Message"
            icon="pi-envelope"
            @success="loadTable"
          />
        </div>
        <div class="flex justify-content-end">
          <Button
            icon="pi pi-refresh"
            class="p-button-rounded p-button-outlined"
            title="Refresh Table"
            @click="loadTable"
          ></Button>
        </div>
      </div>
    </template>
    <template #empty> No records found. </template>
    <template #loading> Loading data. Please wait... </template>
    <Column :expander="true" header-style="width: 3rem" />
    <Column field="contact.alias" header="Contact" />
    <Column field="role" header="Role" />
    <Column field="state" header="State" />
    <Column field="content" header="Content" />
    <Column field="tags" header="Tags" />
    <Column field="created_at" header="Created">
      <template #body="{ data }">
        {{ formatDateLong(data.created_at) }}
      </template>
    </Column>
    <template #expansion="{ data }">
      <RowExpandData
        :id="data.message_id"
        :url="'/tenant/v1/messages/'"
        :params="{ acapy: true }"
      />
    </template>
  </DataTable>
</template>
<script setup lang="ts">
// Vue
import { onMounted, ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import { useToast } from 'vue-toastification';
// State
import { useMessageStore } from '@/store';
import { storeToRefs } from 'pinia';

// Other components
import { formatDateLong } from '@/helpers';
import SuperYou from '@/components/common/SuperYou.vue';
import RowExpandData from '../common/RowExpandData.vue';

const toast = useToast();

const messageStore = useMessageStore();

const { loading, messages, selectedMessage } = storeToRefs(useMessageStore());

const loadTable = async () => {
  messageStore.listMessages().catch((err: any) => {
    toast.error(`Failure: ${err}`);
  });
};

// The API end point
const apiUrl = '/tenant/v1/messages/send-message';

// Some boilerplate JSON
const templateJson = {
  content: 'Here is a bunch of content',
  contact_id: 'e2711758-2f05-47ea-8365-0e9cc96244c4',
  tags: ['touchbase', 'reminder'],
};

const expandedRows = ref([]);

onMounted(async () => {
  loadTable();
});
</script>
<style scoped></style>
