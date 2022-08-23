<script setup lang="ts">
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Dropdown from "primevue/dropdown";
import { ref } from "vue";
import { useToast } from "vue-toastification";
import { useGovernanceStore } from "../../store";
import { storeToRefs } from "pinia";

// For notifications
import { useToast } from "vue-toastification";
const toast = useToast();

const schemaName = ref("");
const schemaVersion = ref("");

const toast = useToast();

const emit = defineEmits(["success"]);

const governanceStore = useGovernanceStore();
governanceStore.$onAction(({ name, after, onError }) => {
  if (name == "createSchemaTemplate") {
    // this is after a successful load of the token...
    after((result) => {
      console.log("created schema template");
      console.log(result);
      if (result != null && result["schema_id"]) {
        toast.info("Schema Template Created");
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

// use the loading state from the store to disable the button...
const { loading } = storeToRefs(useGovernanceStore());

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

const submit_new_schema = async () => {
  // build the correct payload...

  const justAttributeNames = attributes.value.map(
    (attribute) => attribute.name
  );

  const payload = {
    schema_definition: {
      schema_name: schemaName.value,
      schema_version: schemaVersion.value,
      attributes: justAttributeNames,
    },
    name: schemaName.value,
    tags: [],
  };


  //send it off...
  governanceStore.createSchemaTemplate(payload).catch(() => {});
};

// Store an array of attributes. Start with an empty attribute
const attributes = ref([{ name: "", type: "" }]);
</script>
<template>
  <div class="row">
    <span class="p-float-label">
      <InputText v-model="schemaName" type="text" name="create_schema_name" />
      <label for="create_schema_name">Name</label>
    </span>
    <span class="p-float-label">
      <InputText
        v-model="schemaVersion"
        type="text"
        name="create_schema_version"
      />
      <label for="create_schema_version">Version Number</label>
    </span>
  </div>
  <hr />
  <div v-for="(item, index) in attributes" class="row">
    <span class="p-float-label">
      <InputText v-model="item.name" type="text" name="create_schema_name" />
      <label for="create_schema_name">Attribute</label>
    </span>
    <Dropdown
      v-model="item.type"
      :options="options"
      option-label="name"
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
  <Button
    label="Save"
    :disabled="!!loading"
    :loading="!!loading"
    @click="submit_new_schema"
  ></Button>
</template>
<style scoped>
.row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  margin: 20px 0;
}
</style>
