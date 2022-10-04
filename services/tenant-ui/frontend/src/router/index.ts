import { createWebHistory, createRouter } from 'vue-router';
// Main dashboard
import Dashboard from '@/views/Dashboard.vue';
import About from '@/views/About.vue';

// Tenant
import TenantUi from '@/views/TenantUi.vue';
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
// Innkeeper
import InnkeeperUi from '@/views/InnkeeperUi.vue';
import InnkeeperTenants from '@/views/innkeeper/InnkeeperTenants.vue';

const routes = [
  { path: '/:pathMatch(.*)', component: NotFound },

  // Tenant Routes (base / is Tenant side for this app)
  {
    path: '/',
    name: 'TenantUi',
    component: TenantUi,
    children: [
      //Blank route uses dashboard view
      { path: '', name: 'Dashboard', component: Dashboard },

      // About
      {
        path: '/about',
        name: 'About',
        component: About,
      },

      // Tenant - Setup etc
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

      // Tenant - Connections
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

      // Tenant - Schemas, templates etc
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

      // Tenant - Issuer
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

      // Tenant - Verifier
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

      // Tenant - Holder
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
    ],
  },

  // Innkeeper routes
  {
    path: '/innkeeper/',
    name: 'InnkeeperUi',
    component: InnkeeperUi,
    meta: { isInnkeeper: true },
    children: [
      // Blank route uses dashboard view
      { path: '', name: 'InnkeeperTenants', component: InnkeeperTenants },

      // About
      {
        path: 'about',
        name: 'InnkeeperAbout',
        component: About,
        meta: { isInnkeeper: true },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
