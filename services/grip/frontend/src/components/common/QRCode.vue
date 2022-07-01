
<script setup lang="ts">
import { ref } from "vue";
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
    <Accordion>
      <AccordionTab header="View Raw Content">
        <i @click="copy_to_clipboard(qr_content)" class="pi pi-paperclip"></i>
        <!-- {{ qr_content }} -->
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
.qr-image {
  display: flex;
  margin: 20;
}
.qr-container {
  max-width: 400px;
}
i {
  margin: 10;
}
</style>
