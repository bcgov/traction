<template>
  <Button
    title="Messages"
    icon="pi pi-comments"
    class="p-button-rounded p-button-icon-only p-button-text"
    @click="openSidebar"
  />
  <Sidebar v-model:visible="displaySidebar" position="right" class="lg:w-30rem">
    <MessageContactList
      :connection-id="props.connectionId"
      :connection-name="props.connectionName"
    />
    <div class="p-inputgroup flex-1 send-message">
      <InputText
        type="text"
        v-model="message"
        placeholder="Send Message"
        autofocus
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

// Components
import MessageContactList from './MessageContactList.vue';

// State
import { useMessageStore } from '@/store';
import { storeToRefs } from 'pinia';

const messageStore = useMessageStore();
const { loading, messages, selectedMessage } = storeToRefs(useMessageStore());
messageStore.sendMessage('test', { content: 'test' });

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

const message = ref('');

const openSidebar = () => {
  displaySidebar.value = true;
};

const sendMessage = () => {
  console.log(`Send Message ${message.value} to ${props.connectionId}`);
  messageStore.sendMessage(props.connectionId, { content: message.value });
};
</script>

<style>
.send-message {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  width: 90%;
  margin: 1rem 1rem 2rem 1.6rem;
}
</style>
