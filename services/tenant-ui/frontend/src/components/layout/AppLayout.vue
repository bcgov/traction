<template>
    <div class='layout-container'>
        <nav class='layout-sidebar'>
            <Sidebar />
        </nav>
        <div class='layout-page'>
            <header class='layout-header'>
                <Header />
            </header>
            <main class='layout-content'>
                This is the main content
            </main>
            <footer class='layout-footer'>
                This is the footer
            </footer>
        </div>
    </div>
</template>

<script setup lang="ts">
import Header from "./Header.vue";
import Sidebar from "./Sidebar.vue";

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
}

.layout-page {
    width: 100%;
    display: flex;
    flex-direction: column;
}

.layout-header {
    flex: 1;
}

.layout-content {
    flex: 1;
    background-color: yellow;
}

.layout-footer {
    flex: 0;
    background-color: grey;
}
</style>