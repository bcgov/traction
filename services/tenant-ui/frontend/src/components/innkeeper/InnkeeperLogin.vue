<template>
  <div class="traction-login grid w-screen flex-grow-1 mt-0">
    <div class="col-12 md:col-6 xl:col-4">
      <div class="px-8">
        <div class="pt-4 pb-6">
          <img src="/img/bc/bc_logo.png" class="logo-bc" />

          <img
            src="/img/logo/traction-logo-bc-text.svg"
            class="logo-traction"
          />
        </div>

        <div class="py-8">
          <InnkeeperLoginForm v-if="config.frontend.showInnkeeperAdminLogin" />
          <div v-if="config.frontend.oidc.active" class="oidc-login">
            <div
              v-if="config.frontend.showInnkeeperAdminLogin"
              class="oidc-choice"
            >
              <hr />
              <span class="mb-0">{{ $t('admin.orSignInWith') }}</span>
            </div>
            <InnkeeperLoginOidc class="mt-0" />
          </div>
        </div>
      </div>
    </div>

    <div class="cover-image hidden md:block col-0 md:col-6 xl:col-8 p-0">
      <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
      <span class="copyright">Photo by Julia Volk on StockSnap</span>
    </div>
  </div>
  <SessionTimeoutModal />
</template>

<script setup lang="ts">
import InnkeeperLoginForm from '@/components/innkeeper/InnkeeperLoginForm.vue';
import InnkeeperLoginOidc from '@/components/innkeeper/InnkeeperLoginOidc.vue';
import SessionTimeoutModal from '../common/SessionTimeoutModal.vue';
// State
import { storeToRefs } from 'pinia';
import { useConfigStore } from '@/store';
const { config } = storeToRefs(useConfigStore());
</script>

<style scoped lang="scss">
// See layout.scss for generalized common login layout stuff
// Set the image specific to this component here though
.cover-image {
  background-image: url('/img/innkeeper/innkeeper-login-image.jpg');
}
</style>
