<template>
  <MainCardContent
    :title="$t('credentials.exchanges.exchanges')"
    :refresh-callback="loadCredentials"
  >
    <CredentialsTable
      @accept="acceptOffer"
      @delete="deleteCredential"
      @reject="rejectOffer"
    />
  </MainCardContent>
</template>

<script setup lang="ts">
// Types
import { FormattedHeldCredentialRecord } from '@/helpers/tableFormatters';

// PrimeVue etc
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
// State
import { useHolderStore } from '@/store';
// Other components
import CredentialsTable from './CredentialsTable.vue';
import MainCardContent from '@/components/layout/mainCard/MainCardContent.vue';

const toast = useToast();
const confirm = useConfirm();

// State
const holderStore = useHolderStore();

// Actions for a cred row/card
const acceptOffer = (event: any, data: FormattedHeldCredentialRecord) => {
  if (data.credential_exchange_id) {
    holderStore.acceptCredentialOffer(data.credential_exchange_id).then(() => {
      toast.success(`Credential successfully added to your wallet`);
    });
  }
};
const rejectOffer = (event: any, data: FormattedHeldCredentialRecord) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to reject this credential offer?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      if (data.credential_exchange_id) {
        // Send a problem report then delete the cred exchange record
        await holderStore
          .sendProblemReport(data.credential_exchange_id)
          .catch((err: any) => {
            console.error(`Problem report failed: ${err}`);
            toast.error('Failure sending Problem Report');
          });
        holderStore
          .deleteCredentialExchange(data.credential_exchange_id)
          .then(() => {
            loadCredentials();
            toast.success(`Credential offer rejected`);
          });
      }
    },
  });
};
const deleteCredential = (event: any, data: FormattedHeldCredentialRecord) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to delete this credential exchange record?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      if (data.credential_exchange_id) {
        holderStore
          .deleteCredentialExchange(data.credential_exchange_id)
          .then(() => {
            loadCredentials();
            toast.info(`Credential exchange deleted`);
          });
      }
    },
  });
};

// Get the credential exchange list
const loadCredentials = async () => {
  holderStore.listHolderCredentialExchanges().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};
</script>
