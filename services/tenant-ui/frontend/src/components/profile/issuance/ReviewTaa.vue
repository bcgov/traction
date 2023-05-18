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
      <p class="my-0">
        {{ $t('profile.taa.version') }}
        <strong>{{ taa?.taa_record?.version }}</strong>
      </p>
      <p class="mt-0">
        {{ $t('profile.taa.ratification') }}
        <strong>
          {{ formatUnixDate(taa?.taa_record?.ratification_ts) }}
        </strong>
      </p>
      <!-- Only disable this lint if html is trusted or purified -->
      <!-- eslint-disable-next-line vue/no-v-html -->
      <div class="taa-html mb-4" v-html="taaText" />

      <p>
        <Checkbox
          v-model="accepted"
          input-id="accepted"
          :binary="true"
          :disabled="submitting"
        />
        <label for="accepted" class="ml-2">
          {{ $t('profile.taa.agreeAccept') }}
        </label>
      </p>

      <div class="field">
        <label for="selectedMechanism">{{ $t('profile.taa.mechanism') }}</label>
        <Dropdown
          id="selectedMechanism"
          v-model="selectedMechanism"
          :options="mechanisms"
          :disabled="submitting || !accepted"
        />
      </div>

      <Button
        class="w-full"
        :disabled="!accepted"
        :loading="submitting"
        label="Submit"
        @click="submit"
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
import Dropdown from 'primevue/dropdown';
import { useToast } from 'vue-toastification';
// State
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other libs
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { formatUnixDate } from '@/helpers';

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

// Mechanism dropdown
const selectedMechanism = ref('click_agreement');
const mechanisms = computed(() => Object.keys(taa.value?.aml_record?.aml));

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
const handleClose = async () => {
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
