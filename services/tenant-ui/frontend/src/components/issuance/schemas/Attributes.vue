<template>
  <h4 style="margin-bottom: 0.5rem; font-weight: normal">
    {{ $t('issue.attributes') }}
  </h4>
  <div v-for="(item, index) in attributes" :key="index" class="flex w-full">
    <InputText
      v-model="item.name"
      type="text"
      name="{{ `attribute_${index}` }}"
      class="mb-5 w-full"
      @keydown.enter.prevent="addAttribute()"
    />
    <div class="flex justify-content-between">
      <button
        class="ml-1 p-button p-component p-button-icon-only p-button-rounded p-button-danger p-button-text p-float-left"
        type="button"
        @click="removeAttribute(index)"
      >
        <span class="pi pi-times p-button-icon"></span>
      </button>
      <button
        v-if="index === 0"
        class="ml-1 p-button p-component p-button-icon-only p-button-rounded p-button-outlined"
        type="button"
        @click="addAttribute"
      >
        <span class="pi pi-plus p-button-icon"></span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
// Libraries
import { ref } from 'vue';
import InputText from 'primevue/inputtext';
// Source
import { Attribute } from '@/types';

const props = withDefaults(
  defineProps<{
    initialAttributes?: Array<Attribute>;
  }>(),
  {
    initialAttributes: () => [],
  }
);

const addAttribute = () => {
  attributes.value = [{ name: '' }, ...attributes.value];
};

const removeAttribute = (index: number) => {
  if (attributes.value.length > 1) {
    attributes.value.splice(index, 1);
  }
};

const attributes = ref<Attribute[]>([{ name: '' }, ...props.initialAttributes]);

defineExpose({
  attributes,
});
</script>
