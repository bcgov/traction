<template>
  <!-- Request successful -->
  <div v-if="reservationIdResult">
    <div v-if="loading" class="flex flex-column align-items-center">
      <ProgressSpinner />
      <p>{{ $t('reservations.loadingCheckIn') }}</p>
    </div>
    <div v-else>
      <!-- If auto-approve on, the confirmation will come right up -->
      <ShowWallet v-if="status === RESERVATION_STATUSES.SHOW_WALLET" />
      <ReservationConfirmation
        v-else
        :id="reservationIdResult"
        :email="formFields.contact_email"
        :pwd="reservationPwdResult"
      />
    </div>
  </div>

  <!-- Submit Request -->
  <div v-else>
    <form>
      <json-forms
        :schema="formDataSchema"
        :uischema="formUISchema"
        :renderers="renderers"
        :data="data"
        @change="onChange"
      ></json-forms>
      <Button
        type="button"
        class="w-full mt-5"
        :label="$t('common.submit')"
        :disabled="!!loading"
        :loading="!!loading"
        @click="handleSubmit2(data)"
      />
    </form>

    <!-- TODO: Replace this with the form schema logic -->
    <form @submit.prevent="handleSubmit(!v$.$invalid)">
      <!-- Email -->
      <div class="field mt-5 w-full">
        <label
          for="email"
          :class="{ 'p-error': v$.contact_email.$invalid && submitted }"
        >
          {{ $t('common.emailAddress') }}
        </label>
        <InputText
          id="email"
          v-model="v$.contact_email.$model"
          type="text"
          option-label="label"
          autocomplete="email"
          name="email"
          autofocus
          class="w-full"
        />
        <span v-if="v$.contact_email.$error && submitted">
          <span v-for="(error, index) of v$.contact_email.$errors" :key="index">
            <small class="p-error block">{{ error.$message }}</small>
          </span>
        </span>
        <small
          v-else-if="v$.contact_email.$invalid && submitted"
          class="p-error"
        >
          {{ v$.contact_email.required.$message }}
        </small>
      </div>

      <!-- FullName -->
      <div class="field mt-5 w-full">
        <label
          for="full-name"
          :class="{ 'p-error': v$.contact_name.$invalid && submitted }"
        >
          {{ $t('reserve.fullName') }}
        </label>
        <InputText
          id="full-name"
          v-model="v$.contact_name.$model"
          type="text"
          option-label="label"
          autocomplete="full-name"
          name="fullName"
          class="w-full"
        />
        <small v-if="v$.contact_name.$invalid && submitted" class="p-error">{{
          v$.contact_name.required.$message
        }}</small>
      </div>

      <!-- Phone -->
      <div class="field mt-5 w-full">
        <label
          for="phone"
          :class="{ 'p-error': v$.contact_phone.$invalid && submitted }"
        >
          {{ $t('reserve.phone') }}
        </label>
        <InputText
          id="phone"
          v-model="v$.contact_phone.$model"
          type="text"
          option-label="label"
          autocomplete="phone"
          name="phone"
          class="w-full"
        />
        <small v-if="v$.contact_phone.$invalid && submitted" class="p-error">{{
          v$.contact_phone.required.$message
        }}</small>
      </div>

      <!-- Tenant Name -->
      <div class="field mt-5 w-full">
        <label
          for="tenant-name"
          :class="{ 'p-error': v$.tenant_name.$invalid && submitted }"
        >
          {{ $t('common.tenantName') }}
        </label>
        <InputText
          id="tenant-name"
          v-model="v$.tenant_name.$model"
          type="text"
          option-label="label"
          name="tenantName"
          class="w-full"
        />
        <small v-if="v$.tenant_name.$invalid && submitted" class="p-error">{{
          v$.tenant_name.required.$message
        }}</small>
      </div>

      <!-- Tenant Reason -->
      <div class="field mt-5 w-full">
        <label
          for="tenant-reason"
          :class="{ 'p-error': v$.tenant_reason.$invalid && submitted }"
        >
          {{ $t('common.tenantReason') }}
        </label>
        <Textarea
          id="tenant-reason"
          v-model="v$.tenant_reason.$model"
          option-label="label"
          name="tenantReason"
          class="w-full"
          :auto-resize="true"
          rows="2"
        />
        <small v-if="v$.tenant_reason.$invalid && submitted" class="p-error">{{
          v$.tenant_reason.required.$message
        }}</small>
      </div>

      <Button
        type="submit"
        class="w-full mt-5"
        :label="$t('common.submit')"
        :disabled="!!loading"
        :loading="!!loading"
      />
    </form>
  </div>
</template>

<script setup lang="ts">
//Vue
import { ref, reactive } from 'vue';
// PrimeVue/Validation/etc
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import ProgressSpinner from 'primevue/progressspinner';
import Textarea from 'primevue/textarea';
import { useToast } from 'vue-toastification';
import { email, required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { JsonForms, JsonFormsChangeEvent } from '@jsonforms/vue';
import { vanillaRenderers } from '@jsonforms/vue-vanilla';
// State
import { useConfigStore, useOidcStore, useReservationStore } from '@/store';
import { storeToRefs } from 'pinia';
// Components
import { RESERVATION_STATUSES } from '@/helpers/constants';
import ShowWallet from './status/ShowWallet.vue';
import ReservationConfirmation from './ReservationConfirmation.vue';
import axios from 'axios';

const toast = useToast();

// State setup
const reservationStore = useReservationStore();
const { config } = storeToRefs(useConfigStore());
const { loading, status } = storeToRefs(useReservationStore());
const { user } = storeToRefs(useOidcStore());

// The reservation return object
const reservationIdResult: any = ref('');
const reservationPwdResult: any = ref('');

// This stores the form data.
const data: any = ref({});

// Make sure the data object is updated when the form changes.
const onChange = function (event: JsonFormsChangeEvent) {
  data.value = event.data;
};

const formDataSchema: any = ref({});
const formUISchema: any = ref({});

axios
  .get('forms/reservation.json')
  .then((response) => {
    formDataSchema.value = response.data.formDataSchema;
    formUISchema.value = response.data.formUISchema;
  })
  .catch((error) => {
    console.error('Could not get the form configuration', error);
  });

const renderers = [...vanillaRenderers];

// Login Form and validation
const formFields = reactive({
  contact_email: config.value.frontend.showOIDCReservationLogin
    ? user.value.profile.email
    : '',
  contact_name: config.value.frontend.showOIDCReservationLogin
    ? user.value.profile.name
    : '',
  contact_phone: '',
  tenant_name: '',
  tenant_reason: '',
});
const rules = {
  contact_email: { required, email },
  contact_name: { required },
  contact_phone: { required },
  tenant_name: { required },
  tenant_reason: { required },
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
    const res = await reservationStore.makeReservation(formFields);
    reservationIdResult.value = res.reservation_id;
    reservationPwdResult.value = res.reservation_pwd
      ? res.reservation_pwd
      : undefined;
  } catch (err) {
    console.error(err);
    toast.error(`Failure making request: ${err}`);
  }
};
const handleSubmit2 = (event: any) => {
  console.log('handleSubmit2 event', event);
};
</script>
<style scoped lang="scss">
:deep(.control) {
  margin-bottom: 0.5rem;
  input,
  textarea {
    width: 100%;
    border-radius: 5px;
    border: 1px solid #ced4da;
    padding: 0.45rem;
    color: #495057;
    font-family: Inter, Avenir, Helvetica, Arial, sans-serif;
    font-size: 1rem;
  }
  input:hover,
  input:focus,
  textarea:hover,
  textarea:focus {
    border-color: #2b3f51;
  }
  input:focus,
  textarea:focus {
    box-shadow: 0 0 0.3rem 0.1rem #87a6c1;
  }
  input:focus-visible,
  textarea:focus-visible {
    outline: none;
  }
  .error {
    font-weight: 200;
    color: red;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
  }
}
</style>
