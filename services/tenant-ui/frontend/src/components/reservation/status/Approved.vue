<template>
  <!-- Approved and ready to get wallet details with PW -->
  <Card class="info-card mt-4 mb-6">
    <template #title>
      <i class="pi pi-thumbs-up info-card-icon"></i> <br />
      {{ $t('reservations.approved!') }}
    </template>
    <template #content>
      <p>
        {{
          $t('reservations.sentPasswordOn', [
            formatDateLong(reservation.updated_at),
          ])
        }}
      </p>
      <p>
        {{ $t('reservations.enterPassword') }}
      </p>

      <form @submit.prevent="handleSubmit(!v$.$invalid)">
        <div class="field">
          <Password
            v-model="v$.password.$model"
            class="w-full"
            input-class="w-full"
            toggle-mask
            :feedback="false"
            placeholder="Password"
          />
          <small v-if="v$.password.$invalid && submitted" class="p-error">
            {{ v$.password.required.$message }}
          </small>
          <Button
            type="submit"
            label="Validate"
            class="w-full mt-3"
            :loading="loading"
          />
          <Message v-if="showError" severity="error" :closable="false">
            {{ errorMessage }}
          </Message>
        </div>
      </form>
      <p>
        {{ $t('reservations.passwordValid48Hours') }}
      </p>
    </template>
    <template #footer>
      <hr />
      {{ $t('reservations.checkJunkFolder') }}
    </template>
  </Card>
</template>

<script setup lang="ts">
// Vue
import { reactive, ref } from 'vue';
// PrimeVue/Validation/etc
import Button from 'primevue/button';
import Card from 'primevue/card';
import Message from 'primevue/message';
import Password from 'primevue/password';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { useToast } from 'vue-toastification';
// Other Components
import { formatDateLong } from '@/helpers';
// State
import { useReservationStore } from '@/store';
import { storeToRefs } from 'pinia';

const toast = useToast();

const reservationStore = useReservationStore();
const { reservation } = storeToRefs(useReservationStore());

const showError = ref(false);

const errorMessage = ref('An error occurred'); // Default error message

// Validation
const formFields = reactive({
  password: '',
});
const rules = {
  password: { required },
};

const v$ = useVuelidate(rules, formFields, { $scope: false });

// Password form submission
const submitted = ref(false);
const loading = ref(false); // Need a separate loading state for the button
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;
  loading.value = true;

  if (!isFormValid) {
    loading.value = false;
    return;
  }

  try {
    await reservationStore.checkIn(
      reservation.value.reservation_id,
      formFields.password
    );
  } catch (error: any) {
    /**
     * If error is 401, check if the reservation is expired.
     * If not expired, show the incorrect password error.
     * Otherwise send the error to Toast
     */
    const resp = error.response;
    const exp = resp.data.match(/expired/i);
    if (resp.status === 401 && exp) {
      errorMessage.value = 'Reservation has expired.';
      showError.value = true;
    } else if (resp.status === 401) {
      errorMessage.value = 'Incorrect password. Please try again.';
      showError.value = true;
    } else {
      toast.error(resp.data);
    }
  } finally {
    submitted.value = false;
    loading.value = false;
  }
};
</script>
