<template>
  <h3 class="mt-0">Messages</h3>
  <!-- <DataTable
    :loading="loading"
    :paginator="true"
    :rows="10"
    :value="{ data: [] }"
    selection-mode="single"
  >
  </DataTable> -->
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

const confirm = useConfirm();
const toast = useToast();

const loadTable = async () => {
  console.log('load table');
};

onMounted(async () => {
  loadTable();
});

////////////////////////////////
// TBD: Temp data
const loading = ref(false);
////////////////////////////////
</script>
<style scoped></style>
