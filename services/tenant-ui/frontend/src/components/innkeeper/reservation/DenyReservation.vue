<template>
  <Button
    :label="t('reservations.denyRequest')"
    icon="pi pi-trash"
    class="p-button-rounded p-button-icon-only p-button-text"
    @click="confirmDeny($event)"
  />
  <Dialog
    v-model:visible="displayModal"
    :header="t('reservations.denyRequest')"
    :modal="true"
  >
    <p>
      {{ t('reservations.denied.reasonText') }}
    </p>

    <form @submit.prevent="deny()">
      <!-- Reason -->
      <div class="field">
        <InputText id="reason" v-model="reason" class="w-full" />
      </div>
      <Button
        type="submit"
        :label="t('reservations.denyRequest')"
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
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
import { useI18n } from 'vue-i18n';
// State
import { useInnkeeperTenantsStore } from '@/store';
import { storeToRefs } from 'pinia';
import InputText from 'primevue/inputtext';
const innkeeperTenantsStore = useInnkeeperTenantsStore();
const { loading } = storeToRefs(useInnkeeperTenantsStore());

const confirm = useConfirm();
const { t } = useI18n();
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
});

// Deny reservation
const displayModal = ref(false);
const reason = ref('');
const confirmDeny = (event: any) => {
  confirm.require({
    target: event.currentTarget,
    message: `Are you sure you want to deny this reservation for ${props.email}?`,
    header: 'Deny Reservation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      displayModal.value = true;
    },
  });
};

const deny = async () => {
  try {
    await innkeeperTenantsStore.denyReservation(props.id, {
      state_notes: reason.value,
    });
    toast.success(`Reservation for ${props.email} Denied`);
    displayModal.value = false;
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    innkeeperTenantsStore.listReservations();
  }
};
</script>
