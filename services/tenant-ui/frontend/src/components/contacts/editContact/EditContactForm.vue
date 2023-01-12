<template>
  <div v-if="loading" class="flex justify-content-center">
    <ProgressSpinner />
  </div>
  <form v-else @submit.prevent="handleSubmit(!v$.$invalid)">
    <!-- Alias -->
    <div class="field">
      <label for="alias" :class="{ 'p-error': v$.alias.$invalid && submitted }">
        Contact Alias
      </label>
      <InputText
        v-model="v$.alias.$model"
        :class="{ 'p-invalid': v$.alias.$invalid && submitted }"
        type="text"
        name="alias"
        autofocus
      />
      <small v-if="v$.alias.$invalid && submitted" class="p-error">
        {{ v$.alias.required.$message }}
      </small>
    </div>

    <Button type="submit" label="Submit" class="mt-3 w-full" />

    <div v-if="item" class="flex justify-content-end mb-0 mt-3">
      <small>
        Contact Last Updated: {{ formatDateLong(item.updated_at) }}
      </small>
    </div>
  </form>
</template>

<script setup lang="ts">
// Vue
import { onMounted, reactive, ref, PropType } from 'vue';
// State/etc
import { useContactsStore } from '../../../store';
import useGetItem from '@/composables/useGetItem';
import { formatDateLong } from '@/helpers';
import { API_PATH } from '@/helpers/constants';
// PrimeVue / Validation
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import ProgressSpinner from 'primevue/progressspinner';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { useToast } from 'vue-toastification';

// Props
const props = defineProps({
  contactId: {
    type: String as PropType<string>,
    required: true,
  },
});

const contactsStore = useContactsStore();
const emit = defineEmits(['closed', 'success']);
const toast = useToast();

// Validation
const formFields = reactive({
  alias: '',
});
const rules = {
  alias: { required },
};
const v$ = useVuelidate(rules, formFields);

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;
  if (!isFormValid) {
    return;
  }

  try {
    // await contactsStore.updateContact(props.contactId, formFields.alias);
    emit('success');
    // close up on success
    emit('closed');
    toast.info('Contact Updated');
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};

// Get the latest details about this contact when opening
const { loading, item, fetchItem } = useGetItem(API_PATH.CONNECTIONS);
onMounted(async () => {
  try {
    await fetchItem(props.contactId);
    console.log(item.value.alias);
    formFields.alias = item.value.alias;
  } catch (error: any) {
    toast.error(`Failure: ${error}`);
  }
});
</script>
