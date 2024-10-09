<template>
  <MainCardContent :title="'Logs'">
    <div id="controls">
      <Button
        v-if="getLogStreamState() === LogStreamState.CLOSED"
        title="Start"
        label="Start"
        icon="pi pi-play"
        class="control"
        @click="startLogStream"
      />
      <Button
        v-if="getLogStreamState() === LogStreamState.OPEN"
        title="Stop"
        label="Stop"
        icon="pi pi-stop"
        class="control"
        @click="stopLogStream"
      />
      <Button
        title="Clear"
        label="Clear"
        icon="pi pi-trash"
        class="control"
        @click="clearLogs"
      />
      <Button
        v-if="getLogOrder() === LogOrder.OLDEST"
        title="Oldest first"
        label="Oldest first"
        icon="pi pi-sort-up"
        class="control"
        @click="reverseLogOrder"
      />
      <Button
        v-else
        title="Newest first"
        label="Newest first"
        icon="pi pi-sort-down"
        class="control"
        @click="reverseLogOrder"
      />
    </div>
    <div id="console" :class="getLogOrder()">
      <code v-for="[timestamp, log] in logs" :key="timestamp">
        {{ log }}
      </code>
    </div>
  </MainCardContent>
</template>

<script setup lang="ts">
import Button from 'primevue/button';

import { LogOrder, LogStreamState, useLogStore } from '@/store/logStore';

import MainCardContent from '@/components/layout/mainCard/MainCardContent.vue';

const {
  logs,
  getLogOrder,
  getLogStreamState,
  startLogStream,
  stopLogStream,
  clearLogs,
  reverseLogOrder,
} = useLogStore();
</script>

<style scoped>
#controls {
  padding-bottom: 1rem;
}

#console {
  overflow-x: scroll;
  display: flex;
  flex-direction: column;
}

#console.oldest {
  flex-direction: column;
}

#console.newest {
  flex-direction: column-reverse;
}

#console > code {
  white-space: nowrap;
  padding-bottom: 0.5rem;
}

.control {
  margin-right: 0.5rem;
}
</style>
