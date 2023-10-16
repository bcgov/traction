<template>
  <Button
    title="Messages"
    icon="pi pi-comments"
    class="p-button-rounded p-button-icon-only p-button-text"
    @click="openSidebar"
  />
  <Sidebar v-model:visible="displaySidebar" position="right" class="lg:w-30rem">
    <MessageConnectionList
      :connection-id="props.connectionId"
      :connection-name="props.connectionName"
    />
    <div
      v-if="stringOrBooleanTruthy(config.frontend.showWritableComponents)"
      class="p-inputgroup flex-1 send-message"
    >
      <InputText
        v-model="message"
        type="text"
        placeholder="Send Message"
        autofocus
        @keydown="onKeydown"
      />
      <Button icon="pi pi-send" @click="sendMessage" />
    </div>
  </Sidebar>
</template>

<script setup lang="ts">
// Vue
import { ref, PropType } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Sidebar from 'primevue/sidebar';
import InputText from 'primevue/inputtext';

// Other Components
import { stringOrBooleanTruthy } from '@/helpers';
import MessageConnectionList from './MessageConnectionList.vue';

// State
import { useMessageStore } from '@/store';
import { storeToRefs } from 'pinia';
import { useConfigStore } from '@/store/configStore';

const { config } = storeToRefs(useConfigStore());

const messageStore = useMessageStore();

// Props
const props = defineProps({
  connectionId: {
    type: String as PropType<string>,
    required: true,
  },
  connectionName: {
    type: String as PropType<string>,
    required: true,
  },
});

const displaySidebar = ref(false);

const message = ref(''); // Store new message

const openSidebar = () => {
  displaySidebar.value = true;
};

/**
 * Send the message.
 */
const sendMessage = () => {
  // No empty messages
  if (message.value.length === 0) return;

  messageStore.sendMessage(props.connectionId, { content: message.value });
  message.value = ''; // Blank the form
};

/**
 * When the user hits enter, send the message.
 * @param event KeyboardEvent
 */
const onKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    sendMessage();
  }
};
</script>

<style lang="scss">
.send-message {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  width: 90% !important;
  margin: 1rem 1rem 2rem 1.6rem;
}
</style>
