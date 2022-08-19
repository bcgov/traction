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
import { ref, inject } from "vue";
import axios from "axios";

// For notifications
import { useToast } from "vue-toastification";
const toast = useToast();

// Store
const store: any = inject("store");

// Activate two way binding on schemaId
const schemaId = ref("");

const copy = (emit: any) => {
  const url = "/api/traction/tenant/v1/governance/schema_templates/import/";

  const headers = {
    Authorization: `Bearer ${store.state.token}`,
    "Content-Type": "application/json",
  };

  const payload = {
    schema_id: `${schemaId.value}`,
    name: "string",
    tags: [],
  };

  axios
    .post(url, payload, { headers })
    .then((res) => {
      console.log("success: ", res);
      toast.info("Schema copied successfully");
    })
    .catch((err) => {
      console.log("error: ", err);
      toast.error(`Error copying schema: ${err}`);
    })
    .finally(() => {
      // Emit a custom copy event so the parent knows to close the dialog.
      emit("schemaCopy");
    });
};
</script>

<style>
.row {
  display: flex;
  flex-direction: row;
  margin: 10px;
}
</style>
