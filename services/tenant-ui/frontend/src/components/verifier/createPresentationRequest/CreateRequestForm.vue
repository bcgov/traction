<template>
  <div>
    <form @submit.prevent="handleSubmit(!v$.$invalid)">
      <!-- Connection -->
      <div class="field">
        <label
          for="selectedConnection"
          :class="{ 'p-error': v$.selectedConnection.$invalid && submitted }"
        >
          {{ $t('verify.connection') }}
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

      <!-- Proof req body -->
      <span>{{ $t('verify.presentationRequestBody') }}</span>
      <JsonEditorVue
        ref="jsonEditorVueRef"
        v-model="proofRequestJson"
        v-bind="JSON_EDITOR_DEFAULTS"
      />

      <!-- Auto Verify -->
      <div class="field mb-0 mt-2">
        <label for="autoVerify">
          {{ $t('verify.autoVerify') }}
          <i
            v-tooltip="$t('verify.autoVerifyHelp')"
            class="pi pi-question-circle"
          />
        </label>
        <InputSwitch id="autoVerify" v-model="v$.autoVerify.$model" />
      </div>

      <!-- Comment -->
      <div class="field">
        <label for="comment">
          {{ $t('verify.comment') }}
        </label>
        <Textarea
          id="comment"
          v-model="v$.comment.$model"
          class="w-full"
          :auto-resize="true"
          rows="1"
        />
      </div>

      <Button
        type="submit"
        :label="$t('common.submit')"
        class="w-full"
        :disabled="loading"
      />
    </form>
  </div>
</template>

<script setup lang="ts">
// Types
import {
  IndyProofRequest,
  V10PresentationSendRequestRequest,
} from '@/types/acapyApi/acapyInterface';

// Vue
import { reactive, ref } from 'vue';
// PrimeVue / Validation / etc
import AutoComplete from 'primevue/autocomplete';
import Button from 'primevue/button';
import InputSwitch from 'primevue/inputswitch';
import ProgressSpinner from 'primevue/progressspinner';
import Textarea from 'primevue/textarea';
// import ProgressSpinner from 'primevue/progressspinner';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { useToast } from 'vue-toastification';
// State
import { storeToRefs } from 'pinia';
import { useConnectionStore, useVerifierStore } from '@/store';
// Other imports
import JsonEditorVue from 'json-editor-vue';
import { JSON_EDITOR_DEFAULTS } from '@/helpers/constants';

const toast = useToast();

// Store values
const { loading } = storeToRefs(useVerifierStore());
const { loading: connectionsLoading, connectionsDropdown } =
  storeToRefs(useConnectionStore());
const verifierStore = useVerifierStore();

// Props
const props = defineProps<{
  existingPresReq?: IndyProofRequest;
}>();

const emit = defineEmits(['closed', 'success']);

// The default placeholder JSON to start with for this form
// (or supplied by parent component)
const proofRequestJson = ref(
  props.existingPresReq
    ? props.existingPresReq
    : ({
        name: 'proof-request',
        nonce: '1234567890',
        version: '1.0',
        requested_attributes: {
          studentInfo: {
            names: ['given_names', 'family_name'],
            restrictions: [
              {
                schema_name: 'student id',
              },
            ],
          },
        },
        requested_predicates: {
          not_expired: {
            name: 'expiry_dateint',
            p_type: '>=',
            p_value: 20230527,
            restrictions: [
              {
                schema_name: 'student id',
              },
            ],
          },
        },
      } as IndyProofRequest)
);

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

// Form Fields
const filteredConnections = ref();
const formFields = reactive({
  autoVerify: false,
  comment: '',
  // This is not good typescript but need an object with fields
  // in a dropdown that displays a string that can be blank. TODO
  selectedConnection: undefined as any,
});
const rules = {
  autoVerify: {},
  comment: {},
  selectedConnection: { required },
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
    // The json control changes to a string for some reason after editing...
    const proofRequest: IndyProofRequest =
      typeof proofRequestJson.value === 'string'
        ? JSON.parse(proofRequestJson.value)
        : proofRequestJson.value;
    // Set up the body with the fields from the form
    const payload: V10PresentationSendRequestRequest = {
      connection_id: formFields.selectedConnection.value,
      auto_verify: false,
      comment: formFields.comment,
      trace: false,
      proof_request: proofRequest,
    };
    await verifierStore.sendPresentationRequest(payload);
    toast.info('Request Sent');
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
