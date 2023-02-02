<template>
  <h3 class="mt-0">Tenant Profile</h3>

  <div v-if="loading" class="flex justify-content-center">
    <ProgressSpinner />
  </div>
  <div v-else-if="tenant">
    <div class="grid">
      <div class="col-fixed w-30rem">
        <ProfileForm />
        <Issuance />
      </div>
      <div class="col text-right">
        <img v-if="isIssuer" src="/img/badges/issuer.png" />
      </div>
    </div>
    <hr class="mb-4" />
    <ProfileFooter />
  </div>
</template>

<script setup lang="ts">
import Issuance from '@/components/profile/issuance/Issuance.vue';
import ProgressSpinner from 'primevue/progressspinner';
import ProfileForm from '@/components/profile/ProfileForm.vue';
import ProfileFooter from '@/components/profile/ProfileFooter.vue';
// State
import { storeToRefs } from 'pinia';
import { useTenantStore } from '@/store';
const { tenant, isIssuer, loading } = storeToRefs(useTenantStore());
</script>

<style scoped lang="scss">
hr {
  height: 1px;
  background-color: rgb(186, 186, 186);
  border: 0;
}
img {
  width: 6em;
}
</style>
