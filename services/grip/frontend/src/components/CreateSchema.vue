<script setup lang="ts">
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Dropdown from "primevue/dropdown";
import { ref } from "vue";
const alias = ref("");
const alias1 = ref("");
const alias2 = ref("");

// Schema types
const options = [
  { name: "Text", code: "String" },
  { name: "Number", code: "Number" },
  { name: "Boolean", code: "Boolean" },
];

const addAttribute = () => {
  console.log(alias.value);
  console.log(alias1.value);
  console.log(alias2.value);
  console.log(selectedOption.value);
};

const selectedOption = ref(null);

// Store the selected option
// TODO: This needs to be turned into an array that
//   grows and shrinks with the number of attributes.
</script>
<template>
  <div class="row">
    <span class="p-float-label">
      <InputText type="text" v-model="alias" name="create_schema_name" />
      <label for="create_schema_name">Name</label>
    </span>
    <span class="p-float-label">
      <InputText type="text" v-model="alias1" name="create_schema_version" />
      <label for="create_schema_version">Version Number</label>
    </span>
  </div>
  <hr />
  <div class="row">
    <span class="p-float-label">
      <InputText type="text" v-model="alias2" name="create_schema_name" />
      <label for="create_schema_name">Attribute</label>
    </span>
    <Dropdown
      v-model="selectedOption"
      :options="options"
      optionLabel="name"
      placeholder="Type"
    />
  </div>
  <div style="float: right">
    <button
      class="p-button p-component p-button-icon-only p-button-rounded p-button-outlined"
      type="button"
      @click="addAttribute"
    >
      <span class="pi pi-plus p-button-icon"></span>
    </button>
  </div>
  <br />
  <br />
  <hr />
  <Button label="Save"></Button>
</template>
<style scoped>
.row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  margin: 20px 0;
}
</style>
