<template>
  <h2>Chat with {{ props.connectionName }}</h2>
  <div class="container">
    <div
      class="message"
      v-for="item in messageList"
      :class="item.state === 'received' ? 'theirs' : 'mine'"
    >
      <div class="bubble">
        {{ item.content }}
      </div>
      <div class="time">
        {{ item.sent_time }}
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
// Vue
import { ref, PropType, watch } from 'vue';
import { storeToRefs } from 'pinia';

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
 * Remove unwanted messages. In this case
 * it is the message that is sent to the
 * connection to let us know that the
 * message was received.
 * TBD: This should be done in the backend.
 * @param message of type Message
 * @return boolean
 */
const filterMessages = (message: Message) => {
  if (
    message.content.match(/received your message/) &&
    message.content.match(props.connectionName)
  ) {
    return false;
  } else {
    return true;
  }
};

/**
 * Sort the messages by date. Oldest to newest.
 * @param messageA Message currently looking at
 * @param messageB Message next in line
 * @return number
 */
const sortMessages = (messageA: Message, messageB: Message) => {
  const dateA = new Date(messageA.sent_time);
  const dateB = new Date(messageB.sent_time);
  return dateA.valueOf() - dateB.valueOf();
};

/**
 * Get the previous messages for the connection.
 */
messageStore.listMessages(props.connectionId).then((messages) => {
  messageList.value = messages.filter(filterMessages).sort(sortMessages);
});

const { newMessage } = storeToRefs(useMessageStore());

/**
 * Listen for new messages on the messageStore
 */
watch(newMessage, (newMessage) => {
  const now = new Date();
  const tempMessage: Message = {
    connection_id: '',
    content: newMessage,
    created_at: now.toISOString(),
    message_id: '',
    sent_time: now.toISOString(),
    state: 'sent',
    updated_at: now.toISOString(),
  };
  messageList.value.push(tempMessage);
});
</script>

<style scoped lang="scss">
h2 {
  color: #5d5d5d;
}
.container {
  display: flex;
  flex-direction: column;
}
.bubble {
  border-radius: 1rem;
  padding: 0.75rem 1.5rem 0.75rem 1.5rem;
  margin: 0.5rem;
}
.message {
  max-width: 60%;
  min-width: 20%;
}
.mine {
  align-self: flex-end;
}
.mine .bubble {
  background-color: #d8e6f1;
  color: #8297a6;
}
.theirs {
  align-self: flex-start;
}
.theirs .bubble {
  background-color: #88a6be;
  color: #fff;
}
.time {
  display: none;
}
</style>
