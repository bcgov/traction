<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <!-- Email -->
    <div class="field mt-5 w-full">
      <label for="email" :class="{ 'p-error': v$.email.$invalid && submitted }"
        >Enter your Email Address of request
      </label>
      <InputText
        id="email"
        v-model="v$.email.$model"
        type="text"
        option-label="label"
        autocomplete="email"
        name="email"
        autofocus
        class="w-full"
      />
      <span v-if="v$.email.$error && submitted">
        <span v-for="(error, index) of v$.email.$errors" :key="index">
          <small class="p-error block">{{ error.$message }}</small>
        </span>
      </span>
      <small v-else-if="v$.email.$invalid && submitted" class="p-error">{{
        v$.email.required.$message
      }}</small>
    </div>

    <!-- Reservation Id -->
    <div class="field mt-5 w-full">
      <label
        for="reservation-id"
        :class="{ 'p-error': v$.reservationId.$invalid && submitted }"
        >Enter your Reservation ID
      </label>
      <InputText
        id="reservation-id"
        v-model="v$.reservationId.$model"
        name="reservationId"
        class="w-full"
      />
      <small v-if="v$.reservationId.$invalid && submitted" class="p-error">{{
        v$.reservationId.required.$message
      }}</small>
    </div>

    <Button
      type="submit"
      class="w-full mt-5"
      label="Check Status"
    />
  </form>
</template>

<script setup lang="ts">
//Vue
import { ref, reactive } from 'vue';
// PrimeVue/Validation/etc
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import { useToast } from 'vue-toastification';
import { email, required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
// State
import { useReservationStore } from '@/store';
import { storeToRefs } from 'pinia';

const toast = useToast();

// Login Form and validation
const formFields = reactive({
  email: '',
  reservationId: '',
});
const rules = {
  email: { required, email },
  reservationId: { required },
};
const v$ = useVuelidate(rules, formFields);

// State setup
// TODO: IMPLEMENT THIS

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;

  if (!isFormValid) {
    return;
  }
  try {
    // TODO: IMPLEMENT THIS
  } catch (err) {
    console.error(err);
    toast.error(`Failure checking status: ${err}`);
  }
};
</script>
