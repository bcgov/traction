<template>
  <div>
    <form @submit.prevent="handleSubmit(!v$.$invalid)">
      <!-- Connection -->
      <div class="field">
        <label
          for="selectedConnection"
          :class="{ 'p-error': v$.selectedConnection.$invalid && submitted }"
        >
          {{ $t('common.connectionName') }}
          <ProgressSpinner v-if="connectionsLoading" />
        </label>

        <AutoComplete
          id="selectedConnection"
          v-model="v$.selectedConnection.$model"
          class="w-full"
          :disabled="connectionsLoading"
          :suggestions="filteredConnections"
          :dropdown="true"
          option-label="label"
          force-selection
          @complete="searchConnections($event)"
        />
        <small
          v-if="v$.selectedConnection.$invalid && submitted"
          class="p-error"
          >{{ v$.selectedConnection.required.$message }}</small
        >
      </div>

      <!-- Message Body -->
      <div class="field">
        <label
          for="msgContent"
          :class="{ 'p-error': v$.msgContent.$invalid && submitted }"
        >
          {{ $t('messages.messageContent') }}
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
// State
import { storeToRefs } from 'pinia';
import { useConnectionStore, useMessageStore } from '@/store';

const toast = useToast();

// Store values
const { loading } = storeToRefs(useMessageStore());
const { loading: connectionsLoading, connectionsDropdown } =
  storeToRefs(useConnectionStore());
const messageStore = useMessageStore();

const emit = defineEmits(['closed', 'success']);

// Form and Validation
const filteredConnections = ref();
const formFields = reactive({
  msgContent: '',
  selectedConnection: undefined as any,
});
const rules = {
  selectedConnection: { required },
  msgContent: { required },
};
const v$ = useVuelidate(rules, formFields);

// Autocomplete setup
// These can maybe be generalized into a util function (for all dropdown searches)
const searchConnections = (event: any) => {
  if (!event.query.trim().length) {
    filteredConnections.value = [...(connectionsDropdown as any).value];
  } else {
    filteredConnections.value = (connectionsDropdown.value as any).filter(
      (connection: any) => {
        return connection.label
          .toLowerCase()
          .includes(event.query.toLowerCase());
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
    const conn_id = formFields.selectedConnection.value;
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
