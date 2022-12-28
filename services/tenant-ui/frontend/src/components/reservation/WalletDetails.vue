<template>
  <Card class="info-card mt-4 mb-6">
    <template #title>
      <i class="pi pi-check info-card-icon"></i> <br />
      VALIDATED!
    </template>
    <template #content>
      <p>
        Your reservation is validated successfully. <br />
        Here is your new Wallet ID and Wallet Key associated with the email
        address mentioned while registering.
      </p>

      <div class="field mt-5 w-full">
        <label for="wallet-id">Wallet ID</label>
        <InputText
          id="wallet-id"
          :value="walletId"
          name="reservationId"
          class="w-full"
        />
      </div>

      <div class="field">
        <label for="wallet-key">Wallet Key</label>
        <Password
          id="wallet-key"
          :value="walletKey"
          readonly
          class="w-full"
          input-class="w-full"
          toggle-mask
          :feedback="false"
          placeholder="Password"
        />
      </div>
    </template>
    <template #footer>
      <hr />
      Please save your newly generated wallet id and wallet key in a secure
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

defineProps<{
  walletId: string;
  walletKey: string;
}>();
</script>
