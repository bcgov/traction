<template>
  <h2>Chat with {{ props.connectionName }}</h2>
  <!-- TODO cycle through the massageList array and add all the messages-->
</template>
<script setup lang="ts">
// Vue
import { ref, PropType } from 'vue';

// State
import { useMessageStore } from '@/store';

/**
 * This is the interface for the message list.
 */
interface Message {
  connection_id: string;
  content: string;
  created_at: string;
  message_id: string;
  sent_time: string;
  state: string;
  updated_at: string;
}

// Array to contain the messages
const messageList = ref<Array<Message>>([]);
// Connect to the message store
const messageStore = useMessageStore();

/**
 * We are expecting a connection ID and name.
 */
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

/**
 * Get the previous messages for the connection.
 */
messageStore.listMessages(props.connectionId).then((messages) => {
  console.log(messages);
  // TODO: may want to filter out the '_ received your message' entries
  messageList.value = messages;
});
</script>
