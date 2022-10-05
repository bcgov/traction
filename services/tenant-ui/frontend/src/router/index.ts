import { createWebHistory, createRouter } from 'vue-router';
// 404
import NotFound from '@/views/NotFound.vue';

// Routing sections
import innkeeperRoutes from './innkeeperRoutes';
import tenantRoutes from './tenantRoutes';

const routes = [
  { path: '/:pathMatch(.*)', component: NotFound },

  // Tenant Routes (base / is Tenant side for this app)
  ...tenantRoutes,

  // Innkeeper routes (base is /innkeeper)
  ...innkeeperRoutes,
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
