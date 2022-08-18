<template>
  <div class="row">
    <span class="p-float-label">
      <InputText type="text" v-model="schemaId" name="copy_schema_name" />
      <label for="copy_schema_name">Schema ID</label>
    </span>
  </div>
  <div class="row">
    <Button label="Copy" @click="copy($emit)"></Button>
  </div>
</template>
<script setup lang="ts">
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import { ref } from "vue";
// TODO: Import Axios

const copy = (emit: any) => {
  emit("schemaCopy");
  console.log(schemaId.value);
  // TODO: Make a request to the API to copy the schema
};

const schemaId = ref("");
</script>

<style>
.row {
  display: flex;
  flex-direction: row;
  margin: 10px;
}
</style>
