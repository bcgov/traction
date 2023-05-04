<template>
  <div class="border-round border-1 surface-border p-4 surface-card">
    <div class="flex mb-3">
      <Skeleton shape="circle" size="4rem" class="mr-2"></Skeleton>
      <div>
        <Skeleton width="10rem" class="mb-2"></Skeleton>
        <Skeleton width="5rem" class="mb-2"></Skeleton>
      </div>
    </div>
    <Skeleton width="100%" height="150px"></Skeleton>
    <div class="flex justify-content-end mt-3">
      <Skeleton class="mr-3" width="8rem" height="2rem"></Skeleton>
      <Skeleton width="8rem" height="2rem"></Skeleton>
    </div>
  </div>
</template>

<script setup lang="ts">
// This uses the sample code here for a "card" skeleton
// https://primevue.org/skeleton/#card

import Skeleton from 'primevue/skeleton';
</script>
