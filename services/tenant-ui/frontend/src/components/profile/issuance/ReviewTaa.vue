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

      <p>
        <Checkbox
          v-model="accepted"
          inputId="accepted"
          :binary="true"
          :disabled="submitting"
        />
        <label for="accepted" class="ml-2">
          {{ $t('profile.taa.agreeAccept') }}
        </label>
      </p>

      <Button
        @click="submit"
        class="w-full"
        :disabled="!accepted"
        :loading="submitting"
        label="Submit"
      />
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
import { useToast } from 'vue-toastification';
// State
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other libs
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const toast = useToast();

const tenantStore = useTenantStore();
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
const submitting = ref(false);
const submit = async () => {
  submitting.value = true;
  try {
    await tenantStore.acceptTaa({
      mechanism: 'tenant-ui',
      text: taa.value?.taa_record?.text,
      version: taa.value?.taa_record?.version,
    });
    toast.success('TAA Accepted');
  } catch (err) {
    console.error(err);
    toast.error(`Failure accepting TAA: ${err}`);
  } finally {
    submitting.value = false;
    displayModal.value = false;
  }
};

// Open close dialog
const displayModal = ref(false);
const openModal = async () => {
  displayModal.value = true;
};
</script>

<style>
.taa-html {
  background-color: #eaeaea;
  border: 1px dashed gray;
  padding: 1em;
}
</style>
