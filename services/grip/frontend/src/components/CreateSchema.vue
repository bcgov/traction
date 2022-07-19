<script setup lang="ts">
import Button from "primevue/button";
import InputText from "primevue/inputtext";
// import Divider from "primevue/divider";
import { ref } from "vue";
const alias = ref("");
</script>
<template>
  <div class="row">
    <span class="p-float-label">
      <InputText type="text" v-model="alias" name="create_schema_name" />
      <label for="create_schema_name">Name</label>
    </span>
    <span class="p-float-label">
      <InputText type="text" v-model="alias" name="create_schema_version" />
      <label for="create_schema_version">Version Number</label>
    </span>
  </div>
  <!-- <Divider align="right" type="dashed">
    <div class="inline-flex align-items-center">
      <i class="pi pi-user mr-2"></i>
      <b>Attributes</b>
    </div>
  </Divider> -->
  <!-- <Divider></Divider> -->
  <hr />
</template>
<style scoped>
.row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}
</style>
