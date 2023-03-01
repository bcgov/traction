<template>
  <div>
    <DataTable :value="attributeRows" class="attributeTable">
      <Column field="key" header="Code"></Column>
      <Column field="value" header="Name"></Column>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';

const props = defineProps<{
  attributes: Record<string, string>;
}>();

const attributeRows = computed(() => {
  return props.attributes
    ? Object.keys(props.attributes).map((k) => ({
        key: k,
        value: props.attributes[k],
      }))
    : [];
});
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
