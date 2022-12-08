<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <!-- Email -->
    <div class="field mt-5 w-full">
      <label
        for="email"
        :class="{ 'p-error': v$.contact_email.$invalid && submitted }"
        >Email Address
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
        >{{ v$.contact_email.required.$message }}</small
      >
    </div>

    <!-- FullName -->
    <div class="field mt-5 w-full">
      <label
        for="full-name"
        :class="{ 'p-error': v$.contact_name.$invalid && submitted }"
        >Full Name
      </label>
      <InputText
        id="full-name"
        v-model="v$.contact_name.$model"
        autocomplete="name"
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
        >Phone / Mobile
      </label>
      <InputText
        id="phone"
        v-model="v$.contact_phone.$model"
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
        >Tenant Name
      </label>
      <InputText
        id="tenant-name"
        v-model="v$.tenant_name.$model"
        name="tenant-name"
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
        >Tenant Reason
      </label>
      <Textarea
        id="tenant-reason"
        v-model="v$.tenant_reason.$model"
        name="tenant-reason"
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
      label="Request"
      :disabled="!!loading"
      :loading="!!loading"
    />
  </form>
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
const { loading, reservation } = storeToRefs(useReservationStore());

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;

  if (!isFormValid) {
    return;
  }
  try {
    await reservationStore.makeReservation(formFields);
    toast.success(`Your request was recieved.`);
  } catch (err) {
    console.error(err);
    toast.error(`Failure making request: ${err}`);
  }
};
</script>
