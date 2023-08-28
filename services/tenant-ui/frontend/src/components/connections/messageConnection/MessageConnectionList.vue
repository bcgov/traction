<template>
  <div class="title">
    <h2>
      {{ $t('connect.message.messageConnection', [props.connectionName]) }}
    </h2>
  </div>
  <div class="container">
    <div
      v-for="item in messageList"
      :key="item.message_id"
      :class="item.state === 'received' ? 'theirs' : 'mine'"
      class="message"
    >
      <div class="bubble">
        {{ item.content }}
      </div>
      <div class="time" :class="{ display: item.displayTime }">
        {{ formatTime(item.sent_time) }}
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
// Vue
import { ref, PropType, watch, onUpdated, onMounted } from 'vue';
import { storeToRefs } from 'pinia';

// State
import { useMessageStore } from '@/store';

// Other components
import { MESSAGES } from '@/helpers/constants';
import { Message } from '@/store/messageStore';

/**
 * formatTime
 * Format the time to be displayed in the chat window.
 * @param time string
 */
const formatTime = (time: string) => {
  const date: any = new Date(time);
  const now: any = new Date();
  if (now - date > MESSAGES.TIME_LONG) {
    const options = {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    };
    return date.toLocaleDateString('en-CA', options);
  } else {
    return date.toLocaleTimeString();
  }
};

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
  if (message.content.match(/received your message/)) {
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
 * Run through all the messages and flag as to whether
 * the time should be displayed or not.
 * @param message Message
 * @param index number
 * @param wholeArray Array<Message>
 * @return Message
 */
const displayTime = (
  message: Message,
  index: number,
  wholeArray: Array<Message>
) => {
  // If the last item in the array just return the message
  if (index === wholeArray.length - 1) {
    message.displayTime = true;
    return message;
  }

  // These are the dates we care about
  const dateA = new Date(message.sent_time); // Current message
  const dateB = new Date(wholeArray[index + 1].sent_time); // Next message
  const now = new Date(); // Now

  // If older then a day then set the flag
  let old = false;
  if (now.valueOf() - dateA.valueOf() > MESSAGES.TIME_LONG) {
    old = true;
  } else {
    old = false;
  }

  /**
   * If this message is older then a day and the next
   * message is yet another day ahead then display the time.
   */
  if (old && dateB.valueOf() - dateA.valueOf() > MESSAGES.TIME_LONG) {
    message.displayTime = true;
  }

  /**
   * If the message is not older then a day yet the next
   * message is more then 10 minutes ahead then display the time.
   */
  if (!old && dateB.valueOf() - dateA.valueOf() > MESSAGES.TIME_SHORT) {
    message.displayTime = true;
  }

  return message;
};

/**
 * Get the previous messages for the connection.
 */
messageStore.listMessages(props.connectionId).then((messages) => {
  messageList.value = messages
    .filter(filterMessages)
    .sort(sortMessages)
    .map(displayTime);
});

const { newMessage } = storeToRefs(useMessageStore());

/**
 * Listen for new messages on the messageStore
 */
watch(newMessage, (newContent) => {
  const now = new Date();
  const tempMessage: Message = {
    connection_id: '',
    content: newContent,
    created_at: now.toISOString(),
    message_id: '',
    sent_time: now.toISOString(),
    state: 'sent',
    updated_at: now.toISOString(),
    displayTime: false,
  };
  messageList.value.push(tempMessage);
});

let mounted = false;

onMounted(() => {
  mounted = true;
});

/**
 * Scroll to the bottom of the chat window whenever
 * a new message is added.
 */
onUpdated(() => {
  const chat = document.querySelector('.p-sidebar-content');

  if (!chat) return; // Guard clause
  if (mounted) {
    // If first render no animation
    chat.scrollTop = chat.scrollHeight;
    mounted = false;
  } else {
    // Fancy animation
    chat.scrollTo({ top: chat.scrollHeight, behavior: 'smooth' });
  }
});
</script>

<style scoped lang="scss">
h2 {
  color: #5d5d5d;
}
.title {
  position: absolute;
  background-color: #fff;
  width: 100%;
}
.container {
  margin: 5rem 0 5rem 0;
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
  color: #617786;
}
.theirs {
  align-self: flex-start;
}
.theirs .bubble {
  background-color: #6e889e;
  color: #fff;
}
.time {
  font-size: 0.75rem;
  color: #818181;
  margin-top: -0.5rem;
  display: none;
}
.mine .time {
  text-align: right;
}

.time.display {
  display: block;
}
</style>
