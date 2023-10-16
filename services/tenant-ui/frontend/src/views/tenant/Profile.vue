<template>
  <MainCardContent
    :title="$t('tenant.profile.tenantProfile')"
    :refresh-callback="reloadProfileDetails"
  >
    <div v-if="loading" class="flex justify-content-center">
      <ProgressSpinner />
    </div>
    <div v-else-if="tenant">
      <div class="grid">
        <div class="col-fixed" style="width: 50rem">
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
  </MainCardContent>
</template>

<script setup lang="ts">
import Issuance from '@/components/profile/issuance/Issuance.vue';
import MainCardContent from '@/components/layout/mainCard/MainCardContent.vue';
import ProgressSpinner from 'primevue/progressspinner';
import ProfileForm from '@/components/profile/ProfileForm.vue';
import ProfileFooter from '@/components/profile/ProfileFooter.vue';
import { useToast } from 'vue-toastification';
// State
import { storeToRefs } from 'pinia';
import { useTenantStore } from '@/store';
const tenantStore = useTenantStore();
const { tenant, isIssuer, loading } = storeToRefs(useTenantStore());

const toast = useToast();

const reloadProfileDetails = async () => {
  try {
    await Promise.allSettled([
      tenantStore.getTenantConfig(),
      tenantStore.getWriteLedger(),
      tenantStore.getIssuanceStatus(),
    ]);
  } catch (error) {
    toast.error(`Failure getting Issuer info: ${error}`);
  }
};
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
