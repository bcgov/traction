import { createWebHistory, createRouter } from 'vue-router';
// Main dashboard
import Dashboard from '@/views/Dashboard.vue';
import About from '@/views/About.vue';

// Tenant
import Profile from '@/views/tenant/Profile.vue';
import Settings from '@/views/tenant/Settings.vue';
// Connections
import MyContacts from '@/views/connections/MyContacts.vue';
// Issuance
import MyIssuedCredentials from '@/views/issuance/MyIssuedCredentials.vue';
import Schemas from '@/views/issuance/Schemas.vue';
// // Verifictation
import MyPresentations from '@/views/verification/MyPresentations.vue';
import PresentationTemplates from '@/views/verification/PresentationTemplates.vue';
// // Holder
import MyHeldCredentials from '@/views/holder/MyHeldCredentials.vue';
// 404
import NotFound from '@/views/NotFound.vue';


const routes = [
  { path: '/:pathMatch(.*)', component: NotFound },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
  },
  {
    path: '/about',
    name: 'About',
    component: About,
  },

  {
    path: '/tenant/',
    children: [
      {
        path: 'profile',
        name: 'Profile',
        component: Profile,
      },
      {
        path: 'settings',
        name: 'Settings',
        component: Settings,
      },
    ],
  },

  {
    path: '/connections/',
    children: [
      {
        path: 'myContacts',
        name: 'MyContacts',
        component: MyContacts,
      },
    ],
  },

  {
    path: '/configuration/',
    children: [
      {
        path: 'schemas',
        name: 'Schemas',
        component: Schemas,
      },
      {
        path: 'presentationTemplates',
        name: 'PresentationTemplates',
        component: PresentationTemplates,
      },
    ],
  },

  {
    path: '/issuance/',
    children: [
      {
        path: 'credentials',
        name: 'MyIssuedCredentials',
        component: MyIssuedCredentials,
      },
    ],
  },

  {
    path: '/verification/',
    children: [
      {
        path: 'verifications',
        name: 'MyPresentations',
        component: MyPresentations,
      },
    ],
  },

  {
    path: '/holder/',
    children: [
      {
        path: 'credentials',
        name: 'MyHeldCredentials',
        component: MyHeldCredentials,
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
