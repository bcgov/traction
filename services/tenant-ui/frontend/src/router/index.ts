import { createWebHistory, createRouter } from 'vue-router';
// Main dashboard
import Dashboard from '@/views/Dashboard.vue';
import About from '@/views/About.vue';

// Tenant
import Profile from '@/views/tenant/Profile.vue';
import Settings from '@/views/tenant/Settings.vue';
// Connections
import AcceptInvitation from '@/views/connections/AcceptInvitation.vue';
import MyContacts from '@/views/connections/MyContacts.vue';
// Issuance
import MyIssuedCredentials from '@/views/issuance/MyIssuedCredentials.vue';
import Schemas from '@/views/issuance/Schemas.vue';
// // Verifictation
import CreatePresentation from '@/views/verification/CreatePresentation.vue';
import MyPresentations from '@/views/verification/MyPresentations.vue';
import PresentationTemplates from '@/views/verification/PresentationTemplates.vue';
// // Holder
import AcceptCredential from '@/views/holder/AcceptCredential.vue';
import MyHeldCredentials from '@/views/holder/MyHeldCredentials.vue';

const routes = [
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
        path: 'acceptInvitation',
        name: 'AcceptInvitation',
        component: AcceptInvitation,
      },
      {
        path: 'myContacts',
        name: 'MyContacts',
        component: MyContacts,
      },
    ],
  },

  {
    path: '/issuance/',
    children: [
      {
        path: 'myIssuedCredentials',
        name: 'MyIssuedCredentials',
        component: MyIssuedCredentials,
      },
      {
        path: 'schemas',
        name: 'Schemas',
        component: Schemas,
      },
    ],
  },

  {
    path: '/verification/',
    children: [
      {
        path: 'myPresentations',
        name: 'MyPresentations',
        component: MyPresentations,
      },
      {
        path: 'createPresentation',
        name: 'CreatePresentation',
        component: CreatePresentation,
      },
      {
        path: 'presentationTemplates',
        name: 'PresentationTemplates',
        component: PresentationTemplates,
      },
    ],
  },

  {
    path: '/holder/',
    children: [
      {
        path: 'myHeldCredentials',
        name: 'MyHeldCredentials',
        component: MyHeldCredentials,
      },
      {
        path: 'acceptCredential',
        name: 'AcceptCredential',
        component: AcceptCredential,
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
