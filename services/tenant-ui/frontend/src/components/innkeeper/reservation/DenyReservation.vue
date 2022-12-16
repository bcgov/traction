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

const approve = async () => {
  try {
    const res = await innkeeperTenantsStore.approveReservation(props.id);
    alert(res.reservation_pwd);
    toast.success(t('reservations.approved.toast', { email: props.email }));
    displayModal.value = true;
  } catch (error) {
    toast.error(`Failure: ${error}`);
  }
};

// Open popup
const displayModal = ref(false);
// const openModal = async (): Promise<void> => {
//   allowClose.value = true;
//   displayModal.value = true;
// };
// // Handle the successful check in and set a flag so that we can't close without our warn-prompt button
// const tenantCreated = async (): Promise<void> => {
//   allowClose.value = false;
//   // Propagate the success up in case anyone else needs to pay attention (even if we're not closing this yet)
//   emit('success');
// };
</script>
