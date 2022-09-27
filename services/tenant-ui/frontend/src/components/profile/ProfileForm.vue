<template>
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
    <InputText id="nameField" class="w-full" readonly :value="tenant.name" />
  </div>
  <!-- Public DID -->
  <div class="field">
    <label for="publicDid">Public DID</label>
    <InputText
      id="publicDid"
      class="w-full"
      readonly
      :value="tenant.public_did"
    />
  </div>
  <!-- Public DID Status -->
  <div class="field">
    <label for="publicDidStatus">Public DID Status</label>
    <InputText
      id="publicDidStatus"
      class="w-full"
      readonly
      :value="tenant.public_did_status"
    />
  </div>
  <!-- Make Issuer -->
  <h5 class="mb-0">Issuer</h5>
  <Issuance />
  <!-- Issuer Status -->
  <div class="field mt-3">
    <label for="issStatus">Issuer Status</label>
    <InputText
      id="issStatus"
      class="w-full"
      readonly
      :value="tenant.issuer_status"
    />
  </div>
</template>

<script setup lang="ts">
import InputText from 'primevue/inputtext';
import Issuance from '@/components/common/Issuance.vue';

import { storeToRefs } from 'pinia';
import { useTenantStore } from '@/store';

// tenant should be loaded by login...
const { tenant } = storeToRefs(useTenantStore());
</script>
