<template>
  <div class="field">
    <label
      :for="fieldName"
      :class="{
        'p-error':
          advancedIsError(v$, fieldName) ||
          (v$[fieldName].$invalid && submitted),
      }"
      >{{ label }}</label
    >
    <InputText
      :id="fieldName"
      v-model="v$[fieldName].$model"
      :disabled="loading"
      class="w-full"
      :class="{
        'p-invalid':
          advancedIsError(v$, fieldName) ||
          (v$[fieldName].$invalid && submitted),
      }"
      :placeholder="placeholder"
      :style="centerPlaceholder ? 'text-align: center' : 'text-align: left'"
    />
    <span v-if="v$[fieldName].$error && submitted">
      <span v-for="(error, index) of v$[fieldName].$errors" :key="index">
        <small class="p-error"> {{ error.$message }} </small>
      </span>
    </span>
    <small v-else-if="v$[fieldName].$invalid && submitted" class="p-error">{{
      v$[fieldName].required.$message
    }}</small>
  </div>
</template>

<script setup lang="ts">
import { Validation } from '@vuelidate/core';
import InputText from 'primevue/inputtext';
import { PropType } from 'vue';

const props = defineProps({
  centerPlaceholder: {
    type: Boolean,
    required: false,
    default: false,
  },
  advancedIsError: {
    type: Function,
    required: false,
    default: () => {},
  },
  fieldName: {
    type: String,
    required: false,
    default: '',
  },
  label: {
    type: String,
    required: false,
    default: '',
  },
  loading: {
    type: Boolean,
    required: false,
    default: false,
  },
  placeholder: {
    type: String,
    required: false,
    default: '',
  },
  submitted: {
    type: Boolean,
    required: false,
    default: false,
  },
  validation: {
    type: Object as PropType<Validation>,
    required: true,
  },
});

const v$ = props.validation;
</script>
