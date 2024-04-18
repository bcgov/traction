<template>
  <div class="mt-2">
    <div class="flex justify-content-end">
      {{ $t('common.json') }}
      <InputSwitch v-model="showRawJson" class="ml-1" @input="toggleJson" />
    </div>
    <div v-show="!showRawJson">
      <slot></slot>
    </div>
    <div v-show="showRawJson">
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

const showRawJson = ref<boolean>(false);
const valuesJson = ref<string>('');

// Undefined indicates that the conversion was a failure
// note that indication of the error should be handled in the
// toJson and fromJson using libraries like vue-toastification
const props = defineProps<{
  toJson: () => string | undefined;
  fromJson: (jsonRepresentation: string) => T | undefined;
}>();

defineExpose({
  showRawJson,
  valuesJson,
});

const toggleJson = () => {
  if (!showRawJson.value) {
    const res = props.toJson();
    if (res) {
      valuesJson.value = res;
    } else {
      showRawJson.value = !showRawJson.value;
    }
  } else {
    if (!props.fromJson(valuesJson.value)) {
      showRawJson.value = !showRawJson.value;
    }
  }
};
</script>
