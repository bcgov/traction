<template>
  <div v-if="tenant">
    <!-- Tenant ID -->
    <div class="field">
      <label for="tenantId">{{ $t('profile.tenantId') }}</label>
      <InputText
        id="tenantId"
        class="w-full"
        readonly
        :value="tenant.tenant_id"
      />
    </div>
    <!-- Wallet ID -->
    <div class="field">
      <label for="walletId">{{ $t('common.walletId') }}</label>
      <InputText
        id="walletId"
        class="w-full"
        readonly
        :value="tenant.wallet_id"
      />
    </div>
    <!-- Name -->
    <div class="field">
      <label for="nameField">{{ $t('profile.name') }}</label>
      <InputText
        id="nameField"
        class="w-full"
        readonly
        :value="tenant.tenant_name"
      />
    </div>
    <!-- Email -->
    <div class="field">
      <label for="contactfield">{{ $t('profile.contact') }}</label>
      <InputText
        id="contactfield"
        class="w-full"
        readonly
        :value="tenant.contact_email"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import InputText from 'primevue/inputtext';

import { storeToRefs } from 'pinia';
import { useTenantStore } from '@/store';

// tenant should be loaded by login...
const { tenant } = storeToRefs(useTenantStore());
</script>
