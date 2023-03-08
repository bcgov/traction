<template>
  <div>
    <DataTable :value="props.attributes" class="attributeTable" striped-rows>
      <Column field="name" header="Code"></Column>
      <Column field="value" header="Name"></Column>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
// Types
import { CredAttrSpec } from '@/types/acapyApi/acapyInterface';

// Primevue
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';

const props = defineProps<{
  attributes: CredAttrSpec[];
}>();
</script>

<style lang="scss" scoped>
// Custom 'table' for attribute list, see global scss for primevue table overrides
.attributeTable:deep(table) {
  .p-datatable-thead {
    display: none;
  }
  tr:first-of-type {
    border-top: 1px $tenant-ui-panel-border-color solid !important;
  }
}
</style>
