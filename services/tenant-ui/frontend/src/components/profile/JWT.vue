<template>
  <h2>{{ $t('profile.token') }}</h2>
  <Accordion :multiple="true">
    <AccordionTab :header="$t('common.encodedJwt')">
      <div class="flex">
        <div class="overflow-auto w-full">
          <!-- Just used p-inputtext to keep styling consistent -->
          <div class="p-inputtext overflow-auto">
            {{ token }}
          </div>
        </div>
        <Button
          icon="pi pi-copy"
          outlined
          text
          @click="copyEncodedToClipboard"
        />
      </div>
    </AccordionTab>
    <AccordionTab :header="$t('common.decodedJwt')">
      <div class="flex">
        <div class="overflow-auto w-full">
          <div class="p-inputtext overflow-auto">
            {{ decodedToken }}
          </div>
        </div>
        <Button
          icon="pi pi-copy"
          outlined
          text
          @click="copyDecodedToClipboard"
        />
      </div>
    </AccordionTab>
  </Accordion>
</template>

<script setup lang="ts">
import { Ref, computed } from 'vue';
import { useTokenStore } from '@/store';
import { storeToRefs } from 'pinia';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import Button from 'primevue/button';
import 'primeicons/primeicons.css';
import jwtDecode from 'jwt-decode';
import { useToast } from 'vue-toastification';

const toast = useToast();
const { token } = storeToRefs(useTokenStore());
const decodedToken: Ref<unknown> = computed(() => jwtDecode(token.value ?? ''));

const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text);
  toast.info('Copied JWT to clipboard!');
};
const copyEncodedToClipboard = () => copyToClipboard('Bearer ' + token.value);
const copyDecodedToClipboard = () =>
  copyToClipboard(JSON.stringify(decodedToken.value));
</script>
