<template>
  <Button
    :title="$t('apiKey.delete')"
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
import { useInnkeeperTenantsStore } from '@/store';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const confirm = useConfirm();
const toast = useToast();

const innkeeperTenantsStore = useInnkeeperTenantsStore();

// Props
const props = defineProps({
  recordId: {
    type: String as PropType<string>,
    required: true,
  },
});

// Delete the API key by the ID
const deleteRecord = (event: any) => {
  confirm.require({
    target: event.currentTarget,
    message: t('apiKey.deleteConfirmation'),
    header: t('common.confirmation'),
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      doDelete();
    },
  });
};
const doDelete = () => {
  innkeeperTenantsStore
    .deleteApiKey(props.recordId)
    .then(() => {
      toast.success(t('apiKey.deleteSuccess'));
    })
    .catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
};
</script>
