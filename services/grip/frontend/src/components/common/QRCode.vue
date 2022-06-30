
<script setup lang="ts">
import QrcodeVue from "qrcode.vue";
import Accordion from "primevue/accordion";
import AccordionTab from "primevue/accordiontab";
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
      <AccordionTab header="QR Code Content">
        {{ qr_content }}
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
</style>
