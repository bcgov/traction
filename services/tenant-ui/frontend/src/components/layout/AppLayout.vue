<template>
  <Suspense>
    <!-- the suspense tag is so we can await any of these components.
         sidebar loads the tenant async -->
    <div class="layout-container">
      <nav class="layout-sidebar" :class="sidebarOpenClass">
        <Sidebar />
      </nav>
      <div class="layout-page">
        <header class="layout-header">
          <Header />
        </header>
        <main class="layout-content">
          <MainCard>
            <router-view />
          </MainCard>
        </main>
        <footer class="bottom-0 layout-footer">
          <Footer />
        </footer>
      </div>
    </div>
  </Suspense>
</template>

<script setup lang="ts">
// Layout Components
import Footer from './Footer.vue';
import Header from './Header.vue';
import MainCard from './mainCard/MainCard.vue';
import Sidebar from './Sidebar.vue';

// State
import { storeToRefs } from 'pinia';
import { useCommonStore } from '@/store/commonStore';

const { sidebarOpenClass } = storeToRefs(useCommonStore());
</script>
