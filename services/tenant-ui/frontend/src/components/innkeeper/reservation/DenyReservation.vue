<template>
  <Button
    :label="$t('reservations.denyRequest')"
    icon="pi pi-trash"
    class="p-button-rounded p-button-icon-only p-button-text"
    @click="confirmDeny"
  />
  <Dialog
    v-model:visible="displayModal"
    :style="{ minWidth: '600px' }"
    :header="$t('reservations.denyRequest')"
    :modal="true"
  >
    <form @submit.prevent="deny()">
      <!-- Reason -->
      <div class="field">
        <label for="reason"> {{ $t('reservations.denied.reasonText') }} </label>
        <InputText
          id="reason"
          v-model="reason"
          class="w-full"
          @keydown.enter.prevent
        />
      </div>
      <Button
        type="submit"
        :label="$t('reservations.denyRequest')"
        class="mt-5 w-full"
        :disabled="loading"
        :loading="loading"
      />
    </form>
  </Dialog>
</template>

<script setup lang="ts">
// Vue
import { ref } from 'vue';
// PrimeVue / etc
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { useToast } from 'vue-toastification';
// State
import { useInnkeeperTenantsStore } from '@/store';
import { storeToRefs } from 'pinia';
import InputText from 'primevue/inputtext';
const innkeeperTenantsStore = useInnkeeperTenantsStore();
const { loading } = storeToRefs(useInnkeeperTenantsStore());

const toast = useToast();

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
  email: {
    type: String,
    required: true,
  },
  name: {
    type: String,
    required: true,
  },
});

// Deny reservation
const displayModal = ref(false);
const reason = ref('');
const confirmDeny = () => {
  displayModal.value = true;
};

const deny = async () => {
  try {
    await innkeeperTenantsStore.denyReservation(
      props.id,
      props.email,
      props.name,
      {
        state_notes: reason.value,
      }
    );
    toast.success(`Reservation for ${props.email} Denied`);
    displayModal.value = false;
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    innkeeperTenantsStore.listReservations();
  }
};
</script>
