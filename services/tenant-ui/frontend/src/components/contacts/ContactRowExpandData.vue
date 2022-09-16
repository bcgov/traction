<template>
  <RowExpandData :loading="loading" :data="item">
    <template #details="acapyItem">
      <div>
        <ul>
          <!-- red is showing data that is in the table collection -->
          <li style="color: red">{{ row.contact_id }}</li>
          <!-- green is showing data that was fetched and loaded into the expand data component -->
          <li style="color: green">{{ acapyItem?.acapy.connection }}</li>
        </ul>
      </div>
    </template>
  </RowExpandData>
</template>

<script async setup lang="ts">
// Vue
import { PropType } from 'vue';
// PrimeVue
// State
// Other components
import RowExpandData from '../common/RowExpandData.vue';
import useGetContact from '@/composables/useGetContact';

const props = defineProps({
  row: {
    type: null as unknown as PropType<any>,
    required: true,
  },
});

const { loading, item, fetchItemWithAcapy } = useGetContact();

// ok, let's load up the contact with acapy data...
fetchItemWithAcapy(props.row.contact_id);
</script>

<style scoped></style>
