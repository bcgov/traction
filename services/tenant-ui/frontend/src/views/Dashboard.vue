<template>
  <div class="surface-section px-4 py-8 md:px-6 lg:px-8 text-center">
    <div class="center-boxed">
      <div class="img-holder">
        <img src="/img/logo/traction-logo-5.svg" />
      </div>
    </div>
    <div class="mt-3 mb-3 font-bold text-2xl">
      <span class="text-900">{{ $t('dashboard.greeting') }}</span>
    </div>
  </div>
</template>

<style>
.center-boxed {
  display: flex;
  align-items: center;
  justify-content: center;
}

.img-holder {
  width: 300px;
  height: 300px;
}
</style>
