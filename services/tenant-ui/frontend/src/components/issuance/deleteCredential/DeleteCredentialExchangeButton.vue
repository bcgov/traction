<template>
  <Button
    :title="t('issue.delete.removeExchange')"
    icon="pi pi-trash"
    class="p-button-rounded p-button-icon-only p-button-text mr-2"
    @click="deleteCredExchange($event)"
  />
</template>

<script setup lang="ts">
// State
import { useIssuerStore } from '@/store';
// PrimeVue/etc
import Button from 'primevue/button';
import { useToast } from 'vue-toastification';
import { useConfirm } from 'primevue/useconfirm';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const toast = useToast();
const confirm = useConfirm();

const issuerStore = useIssuerStore();

// Props
const props = defineProps<{
  credExchId: string;
}>();

// Delete a specific cred excch record
const deleteCredExchange = (event: any) => {
  confirm.require({
    target: event.currentTarget,
    message: t('issue.delete.confirm'),
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      issuerStore
        .deleteCredentialExchange(props.credExchId)
        .then(() => {
          toast.success(t('issue.delete.success'));
        })
        .catch((err) => {
          console.error(err);
          toast.error(`Failure: ${err}`);
        });
    },
  });
};
</script>

<style scoped></style>
