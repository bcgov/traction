<script setup lang="ts">
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import { ref } from "vue";
const alias = ref("");
const alias1 = ref("");
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
  <hr />
  <div class="row">
    <span class="p-float-label">
      <InputText type="text" v-model="alias1" name="create_schema_name" />
      <label for="create_schema_name">Attribute</label>
    </span>
  </div>
  <Button label="Save"></Button>
</template>
<style scoped>
.row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}
</style>
