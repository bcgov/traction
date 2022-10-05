<template>
  <Suspense>
    <!-- the suspense tag is so we can await any of these components-->
    <div class="layout-container">
      <nav class="layout-sidebar">
        <Sidebar />
      </nav>
      <div class="layout-page">
        <header class="layout-header"></header>
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
import Footer from '../Footer.vue';
import Sidebar from './Sidebar.vue';
</script>

<style lang="scss" scoped>
// Since a lot of this is copy from the Tenant layout it could be extracted to global
// except we don't have finalized UX for Innkeeper side yet so it might change a bunch or not
body {
  margin: 0;
}

.layout-container {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  min-height: 100vh;
  width: 100%;
}

.layout-sidebar {
  align-self: stretch;
  background-color: $tenant-ui-primary-color;
  color: $tenant-ui-text-on-primary;
  min-width: 20em;
}

.layout-page {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-header {
  flex: 0;
  background-color: white;
}

.layout-content {
  flex: 1;
  background-color: #e4e4e4;
  padding: 0.5em;
}
</style>
