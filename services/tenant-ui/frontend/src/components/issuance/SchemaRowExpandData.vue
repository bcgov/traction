<template>
  <RowExpandData :loading="loading" :data="item"> </RowExpandData>
</template>

<script async setup lang="ts">
// Vue
import { PropType } from 'vue';
// PrimeVue
// State
// Other components
import RowExpandData from '../common/RowExpandData.vue';
import useGetSchema from '@/composables/useGetSchema';

const props = defineProps({
  row: {
    type: null as unknown as PropType<any>,
    required: true,
  },
});

const { loading, item, fetchItemWithAcapy } = useGetSchema();

// ok, let's load up the contact with acapy data...
fetchItemWithAcapy(props.row.schema_template_id);
</script>

<style scoped></style>
