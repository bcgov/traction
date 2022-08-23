<template>
  <div class="row">
    <span class="p-float-label">
      <InputText v-model="schemaId" type="text" name="copy_schema_name" />
      <label for="copy_schema_name">Schema ID</label>
    </span>
  </div>
  <div class="row">
    <Button label="Copy" @click="copy()"></Button>
  </div>
</template>
<script setup lang="ts">
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import { ref } from "vue";
import { useToast } from "vue-toastification";
import { useGovernanceStore } from "@/store";
const toast = useToast();

// Activate two way binding on schemaId
const schemaId = ref("");

const governanceStore = useGovernanceStore();
governanceStore.$onAction(({ name, after, onError }) => {
  if (name == "copySchema") {
    // this is after a successful load of the token...
    after((result) => {
      console.log("copied schema");
      console.log(result);
      if (result != null) {
        toast.info("Schema Copied");
        emit("success");
      }
    });

    // and this called if load throws an error
    onError((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
  }
});

const emit = defineEmits(["success"]);

const copy = async () => {
  const payload = {
    schema_id: `${schemaId.value}`,
    name: null,
    tags: [],
  };

  governanceStore.copySchema(payload).catch(() => {});
};
</script>

<style>
.row {
  display: flex;
  flex-direction: row;
  margin: 10px;
}
.p-dialog-content input {
  min-width: 400px;
}
</style>
