<template>
  <div>
    <form @submit.prevent="handleSubmit(!v$.$invalid)">
      <!-- Contact -->
      <div class="field">
        <label
          for="selectedContact"
          :class="{ 'p-error': v$.selectedContact.$invalid && submitted }"
        >
          Contact Name
          <ProgressSpinner v-if="contactLoading" />
        </label>

        <AutoComplete
          id="selectedContact"
          v-model="v$.selectedContact.$model"
          class="w-full"
          :disabled="contactLoading"
          :suggestions="filteredContacts"
          :dropdown="true"
          option-label="label"
          force-selection
          @complete="searchContacts($event)"
        />
        <small
          v-if="v$.selectedContact.$invalid && submitted"
          class="p-error"
          >{{ v$.selectedContact.required.$message }}</small
        >
      </div>

      <!-- Message Body -->
      <div class="field">
        <label
          for="msgContent"
          :class="{ 'p-error': v$.msgContent.$invalid && submitted }"
        >
          {{ t('messages.messageContent') }}
        </label>
        <Textarea
          id="inviteUrl"
          v-model="v$.msgContent.$model"
          class="w-full"
          :class="{ 'p-invalid': v$.msgContent.$invalid && submitted }"
          :auto-resize="true"
          rows="3"
        />
        <span v-if="v$.msgContent.$error && submitted">
          <span v-for="(error, index) of v$.msgContent.$errors" :key="index">
            <small class="p-error block">{{ error.$message }}</small>
          </span>
        </span>
        <small v-else-if="v$.msgContent.$invalid && submitted" class="p-error">
          {{ v$.msgContent.required.$message }}
        </small>
      </div>

      <Button
        type="submit"
        label="Send Message"
        class="mt-5 w-full"
        :disabled="loading"
      />
    </form>
  </div>
</template>

<script setup lang="ts">
// Vue
import { reactive, ref } from 'vue';
// PrimeVue / Validation / etc
import AutoComplete from 'primevue/autocomplete';
import Button from 'primevue/button';
import Textarea from 'primevue/textarea';
import ProgressSpinner from 'primevue/progressspinner';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { useToast } from 'vue-toastification';
import { useI18n } from 'vue-i18n';
// State
import { storeToRefs } from 'pinia';
import { useContactsStore, useMessageStore } from '@/store';

const toast = useToast();
const { t } = useI18n();

// Store valuesloading
const { loading } = storeToRefs(useMessageStore());
const { loading: contactLoading, contactsDropdown } = storeToRefs(
  useContactsStore()
);
const messageStore = useMessageStore();

const emit = defineEmits(['closed', 'success']);

// Form and Validation
const filteredContacts = ref();
const formFields = reactive({
  msgContent: '',
  // This is not good typescript but need an object with fields
  // in a dropdown that displays a string that can be blank. TODO
  selectedContact: undefined as any,
});
const rules = {
  selectedContact: { required },
  msgContent: { required },
};
const v$ = useVuelidate(rules, formFields);

// Autocomplete setup
// These can maybe be generalized into a util function (for all dropdown searches)
const searchContacts = (event: any) => {
  if (!event.query.trim().length) {
    filteredContacts.value = [...(contactsDropdown as any).value];
  } else {
    filteredContacts.value = (contactsDropdown.value as any).filter(
      (contact: any) => {
        return contact.label.toLowerCase().includes(event.query.toLowerCase());
      }
    );
  }
};

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;

  if (!isFormValid) {
    return;
  }
  try {
    const payload = {
      content: formFields.msgContent,
    };

    // call store
    const conn_id = formFields.selectedContact.conn_id;
    await messageStore.sendMessage(conn_id, payload);
    toast.info('Message Sent');
    emit('success');
    // close up on success
    emit('closed');
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};
</script>
