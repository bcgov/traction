<template>
  <Card class="info-card mt-4 mb-6">
    <template #title>
      <i class="pi pi-check-circle info-card-icon"></i> <br />
      VALIDATED!
    </template>
    <template #content>
      <!-- If the user has just completed their password validation, to show the wallet details -->
      <p>
        Your reservation is validated successfully. <br />
        Here is your new Wallet ID and Wallet Key associated with the email
        address mentioned while registering.
      </p>

      <div class="field mt-5 w-full">
        <label for="wallet-id">Wallet ID</label>
        <div class="p-inputgroup">
          <InputText
            id="wallet-id"
            readonly
            :value="walletId"
            name="wallet-id"
            class="w-full"
          />
          <Button
            icon="pi pi-copy"
            title="Copy to clipboard"
            class="p-button-secondary"
            @click="copyWalletId"
          />
        </div>
      </div>

      <div class="field">
        <label for="wallet-key">Wallet Key</label>
        <div class="p-inputgroup">
          <Password
            id="wallet-key"
            v-model="walletKey"
            readonly
            class="w-full"
            input-class="w-full"
            toggle-mask
            :feedback="false"
            placeholder="Password"
          />
          <Button
            icon="pi pi-copy"
            title="Copy to clipboard"
            class="p-button-secondary"
            @click="copyWalletKey"
          />
        </div>
      </div>
    </template>
    <template #footer>
      <hr />
      Please save your newly generated Wallet ID and Wallet Key in a secure
      location. You will loose the data once this window is closed or you go
      back to sign-in. We will never share these information over the email nor
      do we re-issue upon request.
    </template>
  </Card>
</template>

<script setup lang="ts">
// PrimeVue/Validation/etc
import Card from 'primevue/card';
import Password from 'primevue/password';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
// State
import { useReservationStore } from '@/store';
import { storeToRefs } from 'pinia';

// Notifications
import { useToast } from 'vue-toastification';
const toast = useToast();

const { walletId, walletKey } = storeToRefs(useReservationStore());

/**
 * Copy wallet ID to clipboard
 */
const copyWalletId = () => {
  navigator.clipboard.writeText(walletId.value);
  toast.info('Copied wallet ID to clipboard!');
};
/**
 * Copy wallet key to clipboard
 */
const copyWalletKey = () => {
  navigator.clipboard.writeText(walletKey.value);
  toast.info('Copied Wallet Key to clipboard!');
};
</script>
