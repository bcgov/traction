<template>
  <h3 class="mt-0">Contacts</h3>

  <DataTable
    v-model:selection="selectedContact"
    v-model:expandedRows="expandedRows"
    :loading="loading"
    :value="contacts"
    :paginator="true"
    :rows="10"
    selection-mode="single"
    data-key="contact_id"
    @row-expand="onRowExpand"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start">
          <CreateContact />
          <AcceptInvitation class="ml-4" />
        </div>
        <div class="flex justify-content-end">
          <Button
            icon="pi pi-refresh"
            class="p-button-rounded p-button-outlined"
            title="Refresh Table"
            @click="loadTable"
          />
        </div>
      </div>
    </template>
    <template #empty> No records found. </template>
    <template #loading> Loading data. Please wait... </template>
    <Column :expander="true" header-style="width: 3rem" />
    <Column :sortable="false" header="Actions">
      <template #body="{ data }">
        <Button
          title="Delete Contact"
          icon="pi pi-times-circle"
          class="p-button-rounded p-button-icon-only p-button-text"
          @click="deleteContact($event, data)"
        />
      </template>
    </Column>
    <Column :sortable="true" field="alias" header="Name" />
    <Column field="role" header="Role" />
    <Column field="status" header="Status" />
    <Column field="created_at" header="Created at">
      <template #body="{ data }">
        {{ formatDateLong(data.created_at) }}
      </template>
    </Column>
    <template #expansion="{ data: row }">
      <RowExpandData :loading="contactLoading" :data="contact">
        <template v-slot:details="item">
          <div>
            <ul>
              <!-- red is showing data that is in the table collection -->
              <li style="color: red">{{ row.contact_id }}</li>
              <!-- green is showing data that was fetched and loaded into the expand data component -->
              <li style="color: green">{{ item.acapy.connection }}</li>
            </ul>
          </div>
        </template>
      </RowExpandData>
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
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
// State
import { useContactsStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import AcceptInvitation from './acceptInvitation/AcceptInvitation.vue';
import CreateContact from './createContact/CreateContact.vue';
import { formatDateLong } from '@/helpers';
import RowExpandData from '../common/RowExpandData.vue';
import useGetContact from '@/composables/useGetContact';

const confirm = useConfirm();
const toast = useToast();

const contactsStore = useContactsStore();

const { loading, contacts, selectedContact } = storeToRefs(useContactsStore());
const { loading: contactLoading, contact, getFullContact } = useGetContact();

const loadTable = async () => {
  contactsStore.listContacts().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};

onMounted(async () => {
  loadTable();
});

const deleteContact = (event: any, schema: any) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to delete this contact?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      doDelete(schema);
    },
  });
};
const doDelete = (schema: any) => {
  contactsStore
    .deleteContact(schema)
    .then(() => {
      toast.success(`Contact successfully deleted`);
    })
    .catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
};

const expandedRows = ref([]);
const onRowExpand = async (event: any) => {
  await getFullContact(event.data.contact_id);
};
</script>

<style scoped>
fieldset {
  display: flex;
  align-items: center;
  justify-content: center;
}

.create-contact {
  float: right;
  margin: 3rem 1rem 0 0;
}
.p-datatable-header input {
  padding-left: 3rem;
}
</style>
