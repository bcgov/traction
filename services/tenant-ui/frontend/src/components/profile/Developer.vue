<template>
  <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
  <h2>{{ $t('profile.config') }}</h2>
  <vue-json-pretty :data="config" />
  <h2>{{ $t('profile.token') }}</h2>
  <Accordion :multiple="true">
    <AccordionTab header="Encoded JWT">
      <div style="display: flex">
        <div style="overflow: auto; width: 100%">
          <!-- Just used p-inputtext to keep styling consistent -->
          <div class="p-inputtext" style="overflow: auto">
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
    <AccordionTab header="Decoded JWT">
      <div style="display: flex">
        <div style="overflow: auto; width: 100%">
          <div class="p-inputtext" style="overflow: auto; display: block">
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
import VueJsonPretty from 'vue-json-pretty';
import 'vue-json-pretty/lib/styles.css';
import { storeToRefs } from 'pinia';
import { useConfigStore, useTokenStore } from '@/store';
import { useToast } from 'vue-toastification';
import { Ref, computed } from 'vue';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import Button from 'primevue/button';
import 'primeicons/primeicons.css';
import jwtDecode from 'jwt-decode';

const toast = useToast();
const { token } = storeToRefs(useTokenStore());
const decodedToken: Ref<unknown> = computed(() => jwtDecode(token.value ?? ''));

// tenant should be loaded by login...
const { config } = storeToRefs(useConfigStore());

const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text);
  toast.info('Copied JWT to clipboard!');
};
const copyEncodedToClipboard = () => copyToClipboard('Bearer ' + token.value);
const copyDecodedToClipboard = () =>
  copyToClipboard(JSON.stringify(decodedToken.value));
</script>
