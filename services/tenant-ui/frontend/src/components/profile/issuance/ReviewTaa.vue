<template>
  <div>
    <Button
      :label="$t('profile.taa.reviewButton')"
      icon="pi pi-eye"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :header="$t('profile.taa.reviewButton')"
      :modal="true"
      :style="{ minWidth: '600px', maxWidth: '900px' }"
      @update:visible="handleClose"
    >
      <!-- Only disable this lint if html is trusted or purified -->
      <!-- eslint-disable-next-line vue/no-v-html -->
      <div class="taa-html mb-4" v-html="taaText" />
      <Checkbox v-model="accepted" inputId="accepted" :binary="true" />
      <label for="accepted" class="ml-2"> {{ $t('profile.taa.agreeAccept') }} </label>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
// Vue
import { computed, ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';
import Dialog from 'primevue/dialog';
// State
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other libs
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const { taa } = storeToRefs(useTenantStore());

defineEmits(['success']);

// Render the markdown/html for the TAA text
const taaText = computed(() => {
  return taa.value?.taa_record?.text
    ? DOMPurify.sanitize(marked(taa.value?.taa_record?.text))
    : '';
});

// Accepting
const accepted = ref(false);

// Open close dialog
const displayModal = ref(false);
const openModal = async () => {
  // Kick of the loading asyncs (if needed)
  displayModal.value = true;
};
const handleClose = async () => {
  // some logic... maybe we shouldn't close?
  displayModal.value = false;
};
</script>

<style>
.taa-html {
  background-color: #eaeaea;
  border: 1px dashed gray;
  padding: 1em;
}
</style>
