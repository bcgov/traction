<template>
  <Suspense>
    <!-- the suspense tag is so we can await any of these components-->
    <div class="layout-container innkeeper-layout">
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
import Footer from '../Footer.vue';
import Sidebar from './Sidebar.vue';
import Header from './Header.vue';
</script>
