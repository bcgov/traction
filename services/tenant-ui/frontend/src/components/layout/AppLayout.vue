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
          <Card :class="{ cardExpanded: cardExpanded }">
            <template #content>
              <ExpandButton />

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
// PrimeVue
import Card from 'primevue/card';
// Layout Components
import Header from './Header.vue';
import Footer from './Footer.vue';
import Sidebar from './Sidebar.vue';
import ExpandButton from './mainCard/ExpandButton.vue';

// State
import { storeToRefs } from 'pinia';
import { useCommonStore } from '@/store/commonStore';

const { cardExpanded, sidebarOpenClass } = storeToRefs(useCommonStore());
</script>

<style scoped lang="scss">
.cardExpanded {
  position: fixed;
  top: 10px;
  left: 10px;
  height: calc(100% - 20px);
  width: calc(100% - 20px);
  overflow: auto;

  border: 1px solid lightgray;
}
</style>
