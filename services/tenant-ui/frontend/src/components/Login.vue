<template>
  <div class="traction-login grid w-screen h-screen">
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
          <LoginForm />
        </div>
      </div>
    </div>

    <div class="cover-image hidden md:block col-0 md:col-6 xl:col-8 p-0">
      <span v-if="config.ux.coverImageCopyright" class="copyright">
        {{ config.ux.coverImageCopyright }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import LoginForm from '@/components/LoginForm.vue';
import { useConfigStore } from '@/store';
const { config } = storeToRefs(useConfigStore());
</script>

<style scoped lang="scss">
// See layout.scss for generalized common login layout stuff
// Set the image specific to this component here though
.cover-image {
  background-image: url('/img/default-login-image.jpg');
}
</style>
