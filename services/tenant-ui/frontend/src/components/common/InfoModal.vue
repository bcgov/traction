<template>
  <div>
    <span class="pi pi-info-circle" @click="openModal" />
    <Dialog
      v-model:visible="displayModal"
      :header="header"
      :modal="true"
      @update:visible="handleClose"
    >
      <vue-json-pretty :data="object" />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
// Vue
import { PropType, ref } from 'vue';
// PrimeVue
import Dialog from 'primevue/dialog';
// State

// Other Imports
import { useToast } from 'vue-toastification';
import VueJsonPretty from 'vue-json-pretty';
import 'vue-json-pretty/lib/styles.css';

// State setup

const toast = useToast();

const displayModal = ref(false);
const openModal = async () => {
  // Kick of the loading asyncs (if needed)
  displayModal.value = true;
};
const handleClose = async () => {
  // some logic... maybe we shouldn't close?
  displayModal.value = false;
};

const props = defineProps({
  object: {
    type: Object as PropType<any>,
    required: true,
  },
  header: {
    type: String as PropType<string>,
    required: false,
    default: 'Information',
  },
});
</script>
