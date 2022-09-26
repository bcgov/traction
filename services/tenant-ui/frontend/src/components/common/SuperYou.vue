<!--
  For "Super" users... that means you fellow Dev. This tool allows
  for easy interactions with the API without going through
  Swagger or messing around with Curl.
-->
<template>
  <Button
    icon="pi pi-bolt"
    class="p-button-rounded p-button-outlined"
    title="Custom API Call"
    @click="toggleModal"
  ></Button>
  <Dialog
    v-model:visible="displayModal"
    header="Custom API Call"
    :modal="true"
    @show="setupDialog"
  >
    <div id="json-input"></div>
    <Button @click="submit" type="submit" label="Submit" class="mt-5 w-full" />
  </Dialog>
</template>
<script setup lang="ts">
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { ref, onMounted } from 'vue';
import { useTenantApi } from '@/store/tenantApi';
import { JSONEditor } from 'vanilla-jsoneditor';

const displayModal = ref(false);

/** #toggleModal
 * Open and close the modal
 */
const toggleModal = () => {
  displayModal.value
    ? (displayModal.value = false)
    : (displayModal.value = true);
};

/**
 * This component should accept a JSON object
 * and a url to send it to.
 */
const props = defineProps({
  apiUrl: {
    type: String,
    required: true,
  },
  templateJson: {
    type: Object,
    required: true,
  },
});

/**
 * The JSON editor likes to consume the following format.
 */
let content = {
  text: undefined,
  json: props.templateJson,
};

const setupDialog = () => {
  const editor = new JSONEditor({
    target: document.getElementById('json-input'),
    props: {
      content,
      mainMenuBar: false,
      mode: 'text',
      statusBar: false,
      navigationBar: false,
      indentation: 2,
      tabSize: 2,
      onChange: (updatedContent) => (content = updatedContent),
    },
  });
};

/**
 * Send the JSON to the API
 */
const submit = () => {
  const payload = content.json || JSON.parse(content.text);
};
</script>

<style></style>
