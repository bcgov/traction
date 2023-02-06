<template>
  <!-- Reservation lookup form -->
  <form
    v-if="status !== RESERVATION_STATUSES.SHOW_WALLET"
    @submit.prevent="handleSubmit(!$v.$invalid)"
  >
    <!-- Email -->
    <div class="field mt-5 w-full">
      <label for="email" :class="{ 'p-error': $v.email.$invalid && submitted }"
        >Enter your Email Address of request
      </label>
      <InputText
        id="email"
        v-model="$v.email.$model"
        type="text"
        option-label="label"
        autocomplete="email"
        name="email"
        autofocus
        class="w-full"
        :class="{
          'p-invalid':
            ($v.email.$invalid && submitted) ||
            status === RESERVATION_STATUSES.NOT_FOUND,
        }"
      />
      <span v-if="$v.email.$error && submitted">
        <span v-for="(error, index) of $v.email.$errors" :key="index">
          <small class="p-error block">{{ error.$message }}</small>
        </span>
      </span>
      <small v-else-if="$v.email.$invalid && submitted" class="p-error">{{
        $v.email.required.$message
      }}</small>
    </div>

    <!-- Reservation Id -->
    <div class="field mt-5 w-full">
      <label
        for="reservation-id"
        :class="{ 'p-error': $v.reservationId.$invalid && submitted }"
        >Enter your Reservation ID
      </label>
      <InputText
        id="reservation-id"
        v-model="$v.reservationId.$model"
        name="reservationId"
        class="w-full"
        :class="{
          'p-invalid':
            ($v.reservationId.$invalid && submitted) ||
            status === RESERVATION_STATUSES.NOT_FOUND,
        }"
      />
      <small v-if="$v.reservationId.$invalid && submitted" class="p-error">{{
        $v.reservationId.required.$message
      }}</small>
    </div>

    <Button type="submit" class="w-full my-2" label="Check Status" />
  </form>

  <!-- Statuses to check -->
  <div v-if="loading" class="flex justify-content-center">
    <ProgressSpinner />
  </div>
  <div v-else>
    <Approved v-if="status === RESERVATION_STATUSES.APPROVED" />
    <CheckedIn v-else-if="status === RESERVATION_STATUSES.CHECKED_IN" />
    <Denied v-else-if="status === RESERVATION_STATUSES.DENIED" />
    <Pending v-else-if="status === RESERVATION_STATUSES.REQUESTED" />
    <NotFound v-else-if="status === RESERVATION_STATUSES.NOT_FOUND" />
    <ShowWallet v-else-if="status === RESERVATION_STATUSES.SHOW_WALLET" />
  </div>
</template>

<script setup lang="ts">
// Vue
import { ref, reactive } from 'vue';
// PrimeVue/Validation/etc
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import ProgressSpinner from 'primevue/progressspinner';
import { useToast } from 'vue-toastification';
import { email, required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
// State
import { useReservationStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other Components
import Approved from './status/Approved.vue';
import CheckedIn from './status/CheckedIn.vue';
import Denied from './status/Denied.vue';
import NotFound from './status/NotFound.vue';
import Pending from './status/Pending.vue';
import ShowWallet from './status/ShowWallet.vue';
import { RESERVATION_STATUSES } from '@/helpers/constants';

const toast = useToast();

// State setup
const reservationStore = useReservationStore();
const { loading, status } = storeToRefs(useReservationStore());

// Login Form and validation
const formFields = reactive({
  email: '',
  reservationId: '',
});
const rules = {
  email: { required, email },
  reservationId: { required },
};
const $v = useVuelidate(rules, formFields, { $scope: false });

// Form submission
const submitted = ref(false);

const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;

  if (!isFormValid) {
    return;
  }
  try {
    await reservationStore.checkReservation(
      formFields.reservationId,
      formFields.email
    );
  } catch (err) {
    toast.error(`Failure checking status: ${err}`);
  } finally {
    submitted.value = false;
  }
};
</script>
