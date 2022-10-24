<template>
  <h3 class="mt-0">Messages</h3>
  <DataTable
    :loading="loading"
    :paginator="true"
    :rows="10"
    :value="messages"
    selection-mode="single"
    data-key="message_id"
  >
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
  </DataTable>
</template>
<script setup lang="ts">
// Vue
import { onMounted, ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
// State
import { useMessageStore } from '@/store';
import { storeToRefs } from 'pinia';
import { nextDay } from 'date-fns';

// Other components
import { formatDateLong } from '@/helpers';

const confirm = useConfirm();
const toast = useToast();

const messageStore = useMessageStore();

const { loading, messages, selectedMessage } = storeToRefs(useMessageStore());
console.log('loading', loading);
console.log('messages', messages);
console.log('selectedMessage', selectedMessage);

const loadTable = async () => {
  messageStore
    .listMessages()
    .then((stuff: any) => {
      console.log('stuff', stuff);
    })
    .catch((err: any) => {
      toast.error(`Failure: ${err}`);
    });
};

onMounted(async () => {
  loadTable();
});
</script>
<style scoped></style>
