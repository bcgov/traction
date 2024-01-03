<template>
  <Button
    :title="$t('tenants.settings.restoreTenant')"
    icon="pi pi-undo"
    class="p-button-rounded p-button-icon-only p-button-text"
    @click="confirmAction($event)"
  />
</template>

<script setup lang="ts">
// PrimeVue / etc
import Button from 'primevue/button';
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
  name: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(['success']);

const confirmAction = (event: any) => {
  confirm.require({
    target: event.currentTarget,
    message: t('tenants.settings.restoreConfirm', [props.name]),
    header: 'Confirmation',
    icon: 'pi pi-question-circle',
    accept: () => {
      approve();
    },
  });
};

const approve = async () => {
  try {
    await innkeeperTenantsStore.restoreTenant(props.id);
    toast.success(t('tenants.settings.restoreSuccess', [props.name]));
  } catch (error) {
    toast.error(`Failure: ${error}`);
  }
};
</script>
