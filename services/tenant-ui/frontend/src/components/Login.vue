<template>
  <div class="grid w-screen h-screen">
    <div class="col-12 md:col-6 xl:col-4">
      <div class="px-8">
        <div class="flex justify-content-center pt-4 pb-6">
          <img src="/bc/bc_logo.png" class="logo" />
        </div>

        <div class="py-8">
          <LoginForm />
        </div>
      </div>
    </div>

    <div class="cover-image hidden md:block col-0 md:col-6 xl:col-8 p-0" />
  </div>
</template>

<script setup lang="ts">
// Other Components
import LoginForm from '@/components/LoginForm.vue';
</script>

<style scoped lang="scss">
.cover-image {
  background-image: url('/default-login-image.jpg');
  background-repeat: no-repeat;
  background-size: cover;
}

.logo {
  width: 18em;
}
</style>
