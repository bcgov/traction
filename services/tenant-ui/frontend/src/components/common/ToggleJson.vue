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

<script setup lang="ts">
// Libraries
import { ref, defineExpose } from 'vue';
import InputText from 'primevue/inputtext';
// Source
import InputSwitch from 'primevue/inputswitch';
import Textarea from 'primevue/textarea';
import { useI18n } from 'vue-i18n';

const showRawJson = ref<boolean>(false);
const valuesJson = ref<Object>({});

// TODO expose a way to get the final results as the object
// representation for submitting schemas and issuing credentials
const props = defineProps<{
  toJson: () => string;
  fromJson: (jsonRepresentation: Object) => undefined;
}>();

defineExpose({
  showRawJson,
  valuesJson,
});

const toggleJson = () => {
  try {
    if (showRawJson.value) {
      valuesJson.value = props.toJson();
    } else {
      props.fromJson(valuesJson.value);
    }
  } catch (e) {
    showRawJson.value = !showRawJson.value;
  }
};
</script>
