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
          <Button
            class="my-4 w-full p-danger"
            :style="{ padding: '0.5rem 1rem', fontWeight: 'normal' }"
            severity="danger"
            label="Delete Tenant"
            @click="openModal"
          />
        </div>
        <Dialog
          v-model:visible="displayModal"
          :style="{ minWidth: '500px' }"
          :header="'Delete Tenant'"
          :modal="true"
          @update:visible="handleClose"
        >
          <ConfirmTenantDeletion
            :tenant="tenant"
            api="Tenant"
            @closed="handleClose"
          />
        </Dialog>
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
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import ProfileForm from '@/components/profile/ProfileForm.vue';
import ProfileFooter from '@/components/profile/ProfileFooter.vue';
import ConfirmTenantDeletion from '@/components/innkeeper/tenants/deleteTenant/ConfirmTenantDeletion.vue';
import { ref, computed } from 'vue';
import { useToast } from 'vue-toastification';
// State
import { storeToRefs } from 'pinia';
import { useTenantStore } from '@/store';
const tenantStore = useTenantStore();
const { tenant, isIssuer, loading } = storeToRefs(useTenantStore());
import { useConfirm } from 'primevue/useconfirm';

const confirm = useConfirm();
const toast = useToast();
const displayModal = ref(false);
const openModal = async () => {
  displayModal.value = true;
};
const handleClose = async () => {
  displayModal.value = false;
};
const reloadProfileDetails = async () => {
  try {
    await Promise.allSettled([
      tenantStore.getTenantConfig(),
      tenantStore.getWriteLedger(),
      tenantStore.getIssuanceStatus(),
      tenantStore.getWalletcDids(),
      tenantStore.getTransactions(),
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
