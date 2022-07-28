
<script setup lang="ts">
import { ref } from "vue";
import Button from "primevue/button";
import QrcodeVue from "qrcode.vue";
import Accordion from "primevue/accordion";
import AccordionTab from "primevue/accordiontab";
import { useToast } from "vue-toastification";

const toast = useToast();

const copy_to_clipboard = (content: string) => {
  navigator.clipboard.writeText(content);
  toast("QR Code contents copied to clipboard");
  return;
};
</script>

<template>
  <div class="qr-container" v-if="qr_content">
    <qrcode-vue
      class="qr-image"
      v-if="qr_content"
      :value="qr_content"
      :size="400"
      level="H"
    />
    <Button
      class="clipboard-button"
      label="Copy to Clipboard"
      icon="pi pi-paperclip"
      @click="copy_to_clipboard(qr_content!)"
    ></Button>
    <Accordion class="qr-accordion">
      <AccordionTab header="View Raw Content">
        <p style="word-wrap: break-word">{{ qr_content }}</p>
      </AccordionTab>
    </Accordion>
  </div>
  <span v-else>No Content Found</span>
</template>



<script lang="ts">
export default {
  name: "QRCode",
  props: {
    qr_content: String,
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
