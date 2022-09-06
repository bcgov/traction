<script setup lang="ts">
import { ref } from 'vue';
import Button from 'primevue/button';
import QrcodeVue from 'qrcode.vue';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';

// For notifications
import { useToast } from 'vue-toastification';
const toast = useToast();

const copy_to_clipboard = (content: string) => {
  navigator.clipboard.writeText(content);
  toast.info('URL copied to clipboard');
  return;
};
</script>

<template>
  <div v-if="qrContent" class="qr-container">
    <qrcode-vue
      v-if="qrContent"
      class="qr-image"
      :value="qrContent"
      :size="400"
      level="H"
    />
    <Button
      class="clipboard-button"
      label="Copy to Clipboard"
      icon="pi pi-paperclip"
      @click="copy_to_clipboard(qrContent!)"
    ></Button>
    <Accordion class="qr-accordion">
      <AccordionTab header="View Raw Content">
        <p style="word-wrap: break-word">{{ qrContent }}</p>
      </AccordionTab>
    </Accordion>
  </div>
  <span v-else>No Content Found</span>
</template>

<script lang="ts">
export default {
  name: 'QRCode',
  props: {
    qrContent: {
      type: String,
      default: null,
    },
  },
};
</script>

<style>
.qr-accordion {
  margin-top: 10px;
}

.qr-image {
  display: flex;
  margin-bottom: 25px;
}

.qr-container {
  max-width: 400px;
}

i {
  margin: 10px;
}
</style>
