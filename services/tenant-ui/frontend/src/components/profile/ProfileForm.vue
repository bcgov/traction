<template>
  <div v-if="tenant">
    <!-- Tenant ID -->
    <div class="field">
      <label for="tenantId">Tenant ID</label>
      <InputText
        id="tenantId"
        class="w-full"
        readonly
        :value="tenant.tenant_id"
      />
    </div>
    <!-- Wallet ID -->
    <div class="field">
      <label for="walletId">Wallet ID</label>
      <InputText
        id="walletId"
        class="w-full"
        readonly
        :value="tenant.wallet_id"
      />
    </div>
    <!-- Name -->
    <div class="field">
      <label for="nameField">Name</label>
      <InputText
        id="nameField"
        class="w-full"
        readonly
        :value="tenant.tenant_name"
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
