<template>
  <Card class="info-card mt-4 mb-6">
    <template #title>
      <i class="pi pi-check-circle info-card-icon"></i> <br />
      {{ $t('reservations.validated!') }}
    </template>
    <template #content>
      <!-- If the user has just completed their password validation, to show the wallet details -->
      <p>
        {{ $t('reservations.reservationValidated') }} <br />
        {{ $t('reservations.walletIdAndWalletKey') }}
      </p>

      <div class="field mt-5 w-full">
        <label for="wallet-id">{{ $t('common.walletId') }}</label>
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
        <label for="wallet-key">{{ $t('reservations.walletKey') }}</label>
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
      {{ $t('reservations.saveWalletIdAndWalletKey') }}
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
