<template>
  <Button
    :label="t('reservations.approveRequest')"
    icon="pi pi-check"
    class="p-button-rounded p-button-icon-only p-button-text"
    @click="confirmApprove($event)"
  />
</template>

<script setup lang="ts">
// PrimeVue / etc
import Button from 'primevue/button';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
import { useI18n } from 'vue-i18n';
// State
import { storeToRefs } from 'pinia';
import { useConfigStore } from '@/store';
import { useInnkeeperTenantsStore } from '@/store';
const { config } = storeToRefs(useConfigStore());
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
  name: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(['success']);

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
    const res = await innkeeperTenantsStore.approveReservation(
      props.id,
      props.email,
      props.name
    );
    if (config.value.frontend.showInnkeeperReservationPassword) {
      // Have to handle the dialog up a level or it deletes when the rows re-draw after reload
      emit('success', res.reservation_pwd, props.email);
      toast.success(t('reservations.approved.toast', { email: props.email }));
    } else {
      toast.success(t('reservations.approved.text', { email: props.email }));
    }
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    innkeeperTenantsStore.listReservations();
  }
};
</script>
