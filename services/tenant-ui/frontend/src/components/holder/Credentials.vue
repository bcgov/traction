<template>
  <MainCardContent
    :title="
      cardView
        ? $t('common.credentials')
        : $t('credentials.exchanges.exchanges')
    "
    :refresh-callback="loadCredentials"
  >
    <template #buttons>
      <Button
        v-if="cardView"
        icon="pi pi-table"
        :title="$t('credentials.exchanges.viewTable')"
        text
        rounded
        @click="cardView = false"
      />
      <Button
        v-else
        icon="pi pi-th-large"
        :title="$t('credentials.exchanges.viewCard')"
        text
        rounded
        @click="cardView = true"
      />
    </template>

    <CredentialsCards
      v-if="cardView"
      @accept="acceptOffer"
      @delete="deleteCredential"
      @reject="rejectOffer"
    />
    <CredentialsTable
      v-else
      @accept="acceptOffer"
      @delete="deleteCredential"
      @reject="rejectOffer"
    />
  </MainCardContent>
</template>

<script setup lang="ts">
// Types
import { FormattedHeldCredentialRecord } from '@/helpers/tableFormatters';

// Vue
import { ref } from 'vue';
// PrimeVue etc
import Button from 'primevue/button';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
// State
import { useHolderStore } from '@/store';
// Other components
import CredentialsCards from './CredentialsCards.vue';
import CredentialsTable from './CredentialsTable.vue';
import MainCardContent from '@/components/layout/mainCard/MainCardContent.vue';

const toast = useToast();
const confirm = useConfirm();

// State
const holderStore = useHolderStore();

// Table/card view toggle
const cardView = ref(false);

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
