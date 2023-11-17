<template>
  <p>
    <strong v-if="props.title">
      {{ title }}{{ $t('common.configDelim') }}
    </strong>
    <strong v-else>
      <slot name="title"></slot>{{ $t('common.configDelim') }}
    </strong>

    <span v-if="contentToString">{{ props.content }}</span>
    <slot v-else name="content"></slot>
  </p>
</template>

<script setup lang="ts">
import { computed } from 'vue';

// Can pass in the fields as props, or use slots if more customization needed
const props = withDefaults(
  defineProps<{
    title?: string;
    content?: string | number | boolean;
  }>(),
  {
    title: '',
    content: '',
  }
);
const contentToString = computed(() =>
  typeof props.content === 'boolean' ? props.content.toString() : props.content
);
</script>
