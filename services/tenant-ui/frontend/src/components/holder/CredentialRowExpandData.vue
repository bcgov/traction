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
import useGetCredential from '@/composables/useGetCredential';

const props = defineProps({
  row: {
    type: null as unknown as PropType<any>,
    required: true,
  },
});

const { loading, item, fetchItemWithAcapy } = useGetCredential();

// ok, let's load up the row with acapy data...
fetchItemWithAcapy(props.row.holder_credential_id);
</script>

<style scoped></style>
