<template>
  <Button
    :label="t('reservations.approveRequest')"
    icon="pi pi-check"
    class="p-button-rounded p-button-icon-only p-button-text"
    @click="confirmApprove($event)"
  />
  <Dialog
    v-model:visible="displayModal"
    :header="t('reservations.approved.title')"
    :modal="true"
    :closable="allowClose"
  >
    <p v-html="$t('reservations.approved.text', { email: props.email })"></p>
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
const innkeeperTenantsStore = useInnkeeperTenantsStore();

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

// Approve reservation
const confirmApprove = (event: any) => {
  console.log('here');
  confirm.require({
    target: event.currentTarget,
    message: `Approve reservation for ${props.email}?`,
    header: 'Confirmation',
    icon: 'pi pi-question-circle',
    accept: () => {
      approve();
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
const openModal = async (): Promise<void> => {
  allowClose.value = true;
  displayModal.value = true;
};
// Handle the successful check in and set a flag so that we can't close without our warn-prompt button
const tenantCreated = async (): Promise<void> => {
  allowClose.value = false;
  // Propagate the success up in case anyone else needs to pay attention (even if we're not closing this yet)
  emit('success');
};
const allowClose = ref(true);
</script>
