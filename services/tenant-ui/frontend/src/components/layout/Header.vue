<template>
  <Toolbar class="traction-header">
    <template #start>
      <div
        class="hamburger"
        title="Toggle the side menu"
        @click="toggleSidebar"
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
import { useCommonStore } from '@/store/commonStore';

// Whether the sidebar is open or not
const { sidebarOpen } = storeToRefs(useCommonStore());

/**
 * Toggle the sidebar open or closed
 */
const toggleSidebar = () => {
  if (sidebarOpen.value === null) {
    /* This is the first click so check current page size */
    if (window.innerWidth > 1000) {
      sidebarOpen.value = false;
    } else {
      sidebarOpen.value = true;
    }
  } else if (sidebarOpen.value) {
    /* If the sidebar is open, close it */
    sidebarOpen.value = false;
  } else {
    /* If the sidebar is closed, open it */
    sidebarOpen.value = true;
  }
};
</script>

<style scoped>
/* Make the hamburger button slightly reactive */
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
