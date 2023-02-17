<!--
  For "Super" users... that means you fellow Dev. This tool allows
  for easy interactions with the API without going through
  Swagger or messing around with Curl.
-->
<template>
  <Button
    :icon="`pi ${icon}`"
    :class="text ? '' : 'p-button-rounded p-button-outlined'"
    :label="text"
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
    <Button type="submit" label="Submit" class="mt-5 w-full" @click="submit" />
  </Dialog>
</template>
<script setup lang="ts">
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { ref } from 'vue';
import { useAcapyApi } from '@/store/acapyApi';
import { JSONEditor } from 'vanilla-jsoneditor';
import { useToast } from 'vue-toastification';

// Switch for displaying the modal
const displayModal = ref(false);

// For notifications
const toast = useToast();

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
  icon: {
    type: String,
    required: false,
    default: 'pi-bolt',
  },
  text: {
    type: String,
    required: false,
    default: '',
  },
});

/**
 * The JSON editor likes to consume the following format.
 */
let content: any = {
  text: undefined,
  json: props.templateJson,
};

const setupDialog = () => {
  const editor = new JSONEditor({
    /* eslint-disable-next-line */
    target: document.getElementById('json-input')!, // Not sure how else to do this
    props: {
      content,
      mainMenuBar: false,
      mode: 'text' as any, // Maybe a bug in the types?
      statusBar: false,
      navigationBar: false,
      indentation: 2,
      tabSize: 2,
      onChange: (updatedContent) => (content = updatedContent),
    },
  });
};

const emit = defineEmits(['success']);

/**
 * Send the JSON to the API
 */
const submit = () => {
  const payload = content.json || JSON.parse(content.text);
  useAcapyApi()
    .postHttp(props.apiUrl, payload)
    .then((response) => {
      toast.info('Success!');
      emit('success');
    })
    .catch((error) => {
      toast.error(`Something went wrong... ${error}`);
    })
    .finally(() => {
      toggleModal();
    });
};
</script>
