<template>
  <div class="grid w-screen h-screen">
    <div class="col-12 md:col-6 xl:col-4">
      <div class="px-8">
        <div class="pt-4 pb-6">
          <img src="/bc/bc_logo.png" class="logo-bc" />

          <img src="/traction-logo-bc-text.svg" class="logo-traction" />
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
import LoginForm from '@/components/LoginForm.vue';
</script>

<style scoped lang="scss">
.logo {
  display: block;
  margin-left: auto;
  margin-right: auto;
}
.logo-bc {
  @extend .logo;
  width: 18em;
}
.logo-traction {
  @extend .logo;
  width: 20em;
}

.cover-image {
  background-image: url('/default-login-image.jpg');
  background-repeat: no-repeat;
  background-size: cover;
}
</style>
