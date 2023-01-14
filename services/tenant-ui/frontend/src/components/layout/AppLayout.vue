<template>
  <Suspense>
    <!-- the suspense tag is so we can await any of these components.
         sidebar loads the tenant async -->
    <div class="layout-container">
      <nav class="layout-sidebar" :class="calcOpen()">
        <Sidebar />
      </nav>
      <div class="layout-page">
        <header class="layout-header">
          <Header />
        </header>
        <main class="layout-content">
          <Card>
            <template #content>
              <router-view />
            </template>
          </Card>
        </main>
        <footer class="bottom-0 layout-footer">
          <Footer />
        </footer>
      </div>
    </div>
  </Suspense>
</template>

<script setup lang="ts">
import Card from 'primevue/card';
import Header from './Header.vue';
import Footer from './Footer.vue';
import Sidebar from './Sidebar.vue';

// State
import { storeToRefs } from 'pinia';
import { useGlobalStateStore } from '@/store/stateStore';

const { sidebarOpen } = storeToRefs(useGlobalStateStore());

const calcOpen = () => {
  if (sidebarOpen.value === null) {
    // Use media queries
    return null;
  } else if (sidebarOpen.value) {
    // Default width
    return 'open';
  } else {
    return 'closed'; // Mobile width
  }
};
</script>

<style lang="scss" scoped>
/* By default the small title is hidden, and the large title is shown */
:deep(.sidebar-app-title.small) {
  display: none;
  font-size: 2rem;
}

/* When the sidebar is closed */
@mixin closed {
  :deep(.p-menuitem-text) {
    display: none;
  }
  :deep(.p-menuitem-icon) {
    font-size: 2rem !important;
    margin-left: 0.5rem;
  }
  :deep(.sidebar-app-title) {
    display: none;
  }
  :deep(.sidebar-app-title.small) {
    display: block;
  }
}

/* When the sidebar is open */
@mixin open {
  :deep(.p-menuitem-text) {
    display: '';
  }
  :deep(.p-menuitem-icon) {
    font-size: '';
    margin-left: '';
  }
  :deep(.sidebar-app-title) {
    display: '';
  }
  :deep(.sidebar-app-title.small) {
    display: '';
  }
}

/*
 If the user has not selected a sidebar state, then use media queries to
  determine the state.
 */
.layout-sidebar:not(.open, .closed) {
  @media (max-width: 1000px) {
    min-width: 6rem !important;
    width: 6rem;
    @include closed;
  }
}

/*
 If the user has selected a sidebar state, then use that state.
 */
.layout-sidebar.closed {
  min-width: 6rem !important;
  width: 6rem;
  @include closed;
}
.layout-sidebar.open {
  min-width: '';
  width: '';
  @include open;
}

.layout-sidebar {
  transition: width 0.2s ease-in-out;
  transition: min-width 0.2s ease-in-out;
}
</style>
