<script setup lang="ts">
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Dropdown from "primevue/dropdown";
import { ref } from "vue";
const schemaName = ref("");
const schemaVersion = ref("");

// Schema types
const options = [
  { name: "Text", code: "String" },
  { name: "Number", code: "Number" },
  { name: "Boolean", code: "Boolean" },
];

/**
 * ## addAttribute
 * Add an attribute to the schema.
 */
const addAttribute = () => {
  attributes.value.push({ name: "", type: "" });
};

/**
 * ## removeAttribute
 * Remove an attribute from the schema.
 */
const removeAttribute = (index: number) => {
  attributes.value.splice(index, 1);
};
/**
 * ## save
 * Save the new schema.
 */
const save = ($emit: any) => {
  // console.log(`Name: ${schemaName.value}`);
  // console.log(`Version: ${schemaVersion.value}`);
  // attributes.value.forEach((attribute) => {
  //   console.log(`${attribute.name} ${(attribute.type as any).code}`);
  // });

  // Emit a custom save event so the parent knows to close the dialog.
  $emit("schemaSave");
};

// Store an array of attributes. Start with an empty attribute
const attributes = ref([{ name: "", type: "" }]);
</script>
<template>
  <div class="row">
    <span class="p-float-label">
      <InputText type="text" v-model="schemaName" name="create_schema_name" />
      <label for="create_schema_name">Name</label>
    </span>
    <span class="p-float-label">
      <InputText
        type="text"
        v-model="schemaVersion"
        name="create_schema_version"
      />
      <label for="create_schema_version">Version Number</label>
    </span>
  </div>
  <hr />
  <div class="row" v-for="(item, index) in attributes">
    <span class="p-float-label">
      <InputText type="text" v-model="item.name" name="create_schema_name" />
      <label for="create_schema_name">Attribute</label>
    </span>
    <Dropdown
      v-model="item.type"
      :options="options"
      optionLabel="name"
      placeholder="Type"
    />
    <button
      class="p-button p-component p-button-icon-only p-button-rounded p-button-danger p-button-text"
      type="button"
      @click="removeAttribute(index)"
    >
      <span class="pi pi-times p-button-icon"></span>
    </button>
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
  <Button label="Save" @click="save($emit)"></Button>
</template>
<style scoped>
.row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  margin: 20px 0;
}
</style>
