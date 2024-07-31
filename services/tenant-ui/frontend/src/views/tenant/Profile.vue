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
        <ConfirmPopup group="templating">
          <template #message="slotProps">
            <div class="flex-col items-center w-full gap-4 border-b border-surface-200 dark:border-surface-700 p-4 mb-4 pb-0">
              <i :class="slotProps.message.icon" class=""></i>
              <p>{{ slotProps.message.message }}</p>
            </div>
          </template>
        </ConfirmPopup>
        <Button
          class="my-4 w-full"
          @click="showTenentDeletionWarning($event)" label="Delete Tenant"
        />
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
import ConfirmPopup from 'primevue/confirmpopup';
import ProfileForm from '@/components/profile/ProfileForm.vue';
import ProfileFooter from '@/components/profile/ProfileFooter.vue';
import { useToast } from 'vue-toastification';
// State
import { storeToRefs } from 'pinia';
import { useTenantStore } from '@/store';
const tenantStore = useTenantStore();
const { tenant, isIssuer, loading } = storeToRefs(useTenantStore());
import { useConfirm } from "primevue/useconfirm";

const confirm = useConfirm();
const toast = useToast();
const showTenentDeletionWarning = (event: any) => {
  confirm.require({
    message: "WARNING: Deletion of a tenant is permanent. Would you like to proceed?",
    icon: 'pi pi-exclamation-circle',
    accept: () => {
      tenantStore.deleteTenant();
      window.location.href = '/logout';
    },
  })
}
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
