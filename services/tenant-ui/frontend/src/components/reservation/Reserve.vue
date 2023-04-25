<template>
  <!-- Request successful -->
  <div v-if="reservationIdResult">
    <ReservationConfirmation
      :id="reservationIdResult"
      :email="formFields.contact_email"
    />
  </div>

  <!-- Submit Request -->
  <div v-else>
    <form @submit.prevent="handleSubmit(!v$.$invalid)">
      <!-- Email -->
      <div class="field mt-5 w-full">
        <label
          for="email"
          :class="{ 'p-error': v$.contact_email.$invalid && submitted }"
        >
          {{ $t('reserve.email') }}
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
          {{ $t('reserve.tenantName') }}
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
          {{ $t('reserve.tenantReason') }}
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
        :label="$t('reserve.submit')"
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
import Textarea from 'primevue/textarea';
import { useToast } from 'vue-toastification';
import { email, required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
// State
import { useReservationStore } from '@/store';
import { storeToRefs } from 'pinia';
import ReservationConfirmation from './ReservationConfirmation.vue';

const toast = useToast();

// Login Form and validation
const formFields = reactive({
  contact_email: '',
  contact_name: '',
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

// State setup
const reservationStore = useReservationStore();
const { loading } = storeToRefs(useReservationStore());

// The reservation return object
const reservationIdResult: any = ref('');

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
  } catch (err) {
    console.error(err);
    toast.error(`Failure making request: ${err}`);
  }
};
</script>
