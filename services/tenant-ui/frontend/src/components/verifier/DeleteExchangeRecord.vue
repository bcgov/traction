<template>
  <Button
    :title="$t('verify.delete')"
    icon="pi pi-trash"
    class="p-button-rounded p-button-icon-only p-button-text"
    @click="deleteRecord($event)"
  />
</template>

<script setup lang="ts">
// Vue
import { PropType } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
// State
import { useVerifierStore } from '@/store';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const confirm = useConfirm();
const toast = useToast();

const verifierStore = useVerifierStore();

// Props
const props = defineProps({
  recordId: {
    type: String as PropType<string>,
    required: true,
  },
});

// Delete the connection record by connection id
const deleteRecord = (event: any) => {
  confirm.require({
    target: event.currentTarget,
    message: t('verify.deleteConfirmation'),
    header: t('common.confirmation'),
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      doDelete();
    },
  });
};
const doDelete = () => {
  verifierStore
    .deleteRecord(props.recordId)
    .then(() => {
      toast.success(t('verify.deleteSuccess'));
    })
    .catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
};
</script>
