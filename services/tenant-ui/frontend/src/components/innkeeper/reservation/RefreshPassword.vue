<template>
  <Button
    :label="$t('reservations.refreshPassword')"
    class="p-button-rounded p-button-text"
    icon="pi pi-refresh"
    @click="refresh"
  />
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
import { useConfigStore } from '@/store';
import { useI18n } from 'vue-i18n';
const { config } = storeToRefs(useConfigStore());
const toast = useToast();
const { t } = useI18n();

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
const emit = defineEmits(['success']);
const displayModal = ref(false);
const reason = ref('');

const refresh = async () => {
  try {
    const res = await innkeeperTenantsStore.refreshCheckInPassword(
      props.id,
      props.email,
      {
        state_notes: reason.value,
      }
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
