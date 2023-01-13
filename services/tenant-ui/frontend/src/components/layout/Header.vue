<template>
  <Toolbar class="traction-header">
    <template #start>
      <div
        class="hamburger"
        @click="toggleSidebar"
        title="Toggle the side menu"
      >
        <i class="pi pi-bars p-toolbar-separator mr-2" />
      </div>
    </template>

    <template #end>
      <LocaleSwitcher />

      <ProfileButton />
    </template>
  </Toolbar>
</template>

<script setup lang="ts">
import Toolbar from 'primevue/toolbar';
import ProfileButton from '@/components/profile/ProfileButton.vue';
import LocaleSwitcher from '../common/LocaleSwitcher.vue';

// State
import { storeToRefs } from 'pinia';
import { useGlobalStateStore } from '@/store/stateStore';

// Whether the sidebar is open or not
const { sidebarOpen } = storeToRefs(useGlobalStateStore());

/**
 * Toggle the sidebar open or closed
 */
const toggleSidebar = () => {
  if (sidebarOpen.value) {
    sidebarOpen.value = false;
  } else {
    sidebarOpen.value = true;
  }
};
</script>

<style scoped>
.hamburger {
  cursor: pointer;
  padding: 0.75rem;
  opacity: 0.5;
}
.hamburger:hover {
  transform: scale(1.2) translate(0, 0.1rem);
  transition: 0.2s ease-in-out;
  opacity: 1;
}
</style>
