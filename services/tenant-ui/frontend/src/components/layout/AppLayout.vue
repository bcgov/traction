<template>
  <Suspense>
    <!-- the suspense tag is so we can await any of these components.
         sidebar loads the tenant async -->
    <div class="layout-container">
      <nav class="layout-sidebar">
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
</script>

<style lang="css" scoped>
body {
  margin: 0;
}

.layout-container {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  height: 100vh;
  width: 100%;
}

.layout-sidebar {
  align-self: stretch;
  background-color: #244075;
  color: white;
}

.layout-page {
  width: 100%;
  height: 100vh;
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
