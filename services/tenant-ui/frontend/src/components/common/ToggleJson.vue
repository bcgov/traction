<template>
  <div class="mt-2">
    <div class="flex justify-content-end">
      {{ $t('common.json') }}
      <InputSwitch v-model="displayAsForm" class="ml-1" @input="toggleJson" />
    </div>
    <div v-show="displayAsForm">
      <slot></slot>
    </div>
    <div v-show="!displayAsForm">
      <Textarea
        id="credentialValuesEdit"
        v-model="valuesJson"
        :auto-resize="true"
        rows="20"
        cols="60"
        class="w-full mt-1"
      />
    </div>
  </div>
</template>

<script setup lang="ts" generic="T">
// Libraries
import { ref } from 'vue';
// Source
import InputSwitch from 'primevue/inputswitch';
import Textarea from 'primevue/textarea';

const displayAsForm = ref<boolean>(true);
const valuesJson = ref<string>('');

// Undefined indicates that the conversion was a failure
// note that indication of the error should be handled in the
// toJson and fromJson using libraries like vue-toastification
const props = defineProps<{
  toJson: () => string | undefined;
  fromJson: (jsonRepresentation: string) => T | undefined;
}>();

defineExpose({
  displayAsForm,
  valuesJson,
});

const toggleJson = () => {
  if (displayAsForm.value) {
    const res = props.toJson();
    if (res) {
      valuesJson.value = res;
    } else {
      displayAsForm.value = !displayAsForm.value;
    }
  } else {
    if (!props.fromJson(valuesJson.value)) {
      displayAsForm.value = !displayAsForm.value;
    }
  }
};
</script>
