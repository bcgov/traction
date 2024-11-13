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

      <h3>{{ $t('profile.taa.mechanism') }}</h3>
      <div
        v-for="(value, key) in taa.aml_record?.aml"
        :key="key"
        class="flex mb-2"
      >
        <RadioButton
          v-model="selectedMechanism"
          :input-id="`${key}`"
          name="pizza"
          :value="key"
          :disabled="submitting || !accepted"
        />
        <label :for="`${key}`" class="ml-2">{{ value }}</label>
      </div>

      <Button
        class="w-full mt-4"
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
import RadioButton from 'primevue/radiobutton';
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

// Render the markdown/html for the TAA text
const taaText = computed(() => {
  const markdown = marked.parse(taa.value?.taa_record?.text) as string;
  return taa.value?.taa_record?.text ? DOMPurify.sanitize(markdown) : '';
});

// Mechanism dropdown
const defaultMechanism = 'click_agreement';
const selectedMechanism = ref(defaultMechanism);

// Accepting
const accepted = ref(false);
const submitting = ref(false);
const submit = async () => {
  submitting.value = true;
  try {
    await tenantStore.acceptTaa({
      mechanism: selectedMechanism.value,
      text: taa.value?.taa_record?.text,
      version: taa.value?.taa_record?.version,
    });
    toast.success('TAA Accepted');
    displayModal.value = false;
  } catch (err) {
    console.error(err);
    toast.error(`Failure accepting TAA: ${err}`);
  } finally {
    submitting.value = false;
  }
};

// Open close dialog
const displayModal = ref(false);
const openModal = async () => {
  selectedMechanism.value = defaultMechanism;
  accepted.value = false;
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
