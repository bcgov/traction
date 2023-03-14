<template>
  <h2>Chat with {{ props.connectionName }}</h2>
</template>
<script setup lang="ts">
import { ref, PropType } from 'vue';

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
</script>
