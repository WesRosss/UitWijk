import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

// Import views
const HomeView = () => import('@/views/HomeView.vue')
const LoginView = () => import('@/views/auth/LoginView.vue')
const RegisterView = () => import('@/views/auth/RegisterView.vue')
const ForgotPasswordView = () => import('@/views/auth/ForgotPasswordView.vue')
const ResetPasswordView = () => import('@/views/auth/ResetPasswordView.vue')

const DashboardView = () => import('@/views/DashboardView.vue')
const ProfileView = () => import('@/views/ProfileView.vue')
const SettingsView = () => import('@/views/SettingsView.vue')

// Matches
const MatchesView = () => import('@/views/matches/MatchesView.vue')
const MatchDetailView = () => import('@/views/matches/MatchDetailView.vue')
const CreateMatchView = () => import('@/views/matches/CreateMatchView.vue')
const EditMatchView = () => import('@/views/matches/EditMatchView.vue')

// Teams
const TeamsView = () => import('@/views/teams/TeamsView.vue')
const TeamDetailView = () => import('@/views/teams/TeamDetailView.vue')
const CreateTeamView = () => import('@/views/teams/CreateTeamView.vue')
const EditTeamView = () => import('@/views/teams/EditTeamView.vue')

// Users (Admin only)
const UsersView = () => import('@/views/users/UsersView.vue')
const UserDetailView = () => import('@/views/users/UserDetailView.vue')
const CreateUserView = () => import('@/views/users/CreateUserView.vue')
const EditUserView = () => import('@/views/users/EditUserView.vue')

// Availability
const AvailabilityView = () => import('@/views/AvailabilityView.vue')

// Assignments
const AssignmentsView = () => import('@/views/AssignmentsView.vue')

// Notifications
const NotificationsView = () => import('@/views/NotificationsView.vue')

// 404 Not Found
const NotFoundView = () => import('@/views/NotFoundView.vue')

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false, requiresGuest: true }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { requiresAuth: false, requiresGuest: true }
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: ForgotPasswordView,
    meta: { requiresAuth: false, requiresGuest: true }
  },
  {
    path: '/reset-password/:token',
    name: 'reset-password',
    component: ResetPasswordView,
    meta: { requiresAuth: false, requiresGuest: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsView,
    meta: { requiresAuth: true }
  },
  
  // Matches routes
  {
    path: '/matches',
    name: 'matches',
    component: MatchesView,
    meta: { requiresAuth: true }
  },
  {
    path: '/matches/create',
    name: 'create-match',
    component: CreateMatchView,
    meta: { requiresAuth: true, requiresCoordinator: true }
  },
  {
    path: '/matches/:id',
    name: 'match-detail',
    component: MatchDetailView,
    meta: { requiresAuth: true }
  },
  {
    path: '/matches/:id/edit',
    name: 'edit-match',
    component: EditMatchView,
    meta: { requiresAuth: true, requiresCoordinator: true }
  },
  
  // Teams routes
  {
    path: '/teams',
    name: 'teams',
    component: TeamsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/teams/create',
    name: 'create-team',
    component: CreateTeamView,
    meta: { requiresAuth: true, requiresCoordinator: true }
  },
  {
    path: '/teams/:id',
    name: 'team-detail',
    component: TeamDetailView,
    meta: { requiresAuth: true }
  },
  {
    path: '/teams/:id/edit',
    name: 'edit-team',
    component: EditTeamView,
    meta: { requiresAuth: true, requiresCoordinator: true }
  },
  
  // Users routes (Admin only)
  {
    path: '/users',
    name: 'users',
    component: UsersView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/users/create',
    name: 'create-user',
    component: CreateUserView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/users/:id',
    name: 'user-detail',
    component: UserDetailView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/users/:id/edit',
    name: 'edit-user',
    component: EditUserView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  
  // Availability
  {
    path: '/availability',
    name: 'availability',
    component: AvailabilityView,
    meta: { requiresAuth: true }
  },
  
  // Assignments
  {
    path: '/assignments',
    name: 'assignments',
    component: AssignmentsView,
    meta: { requiresAuth: true }
  },
  
  // Notifications
  {
    path: '/notifications',
    name: 'notifications',
    component: NotificationsView,
    meta: { requiresAuth: true }
  },
  
  // 404 Not Found
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFoundView,
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation guard for authentication
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if user is authenticated
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Redirect to login page
    return next({
      name: 'login',
      query: { redirect: to.fullPath }
    })
  }
  
  // Check if user is guest (for auth pages)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    // Redirect to dashboard
    return next({ name: 'dashboard' })
  }
  
  // Check for admin role
  if (to.meta.requiresAdmin && authStore.isAuthenticated) {
    if (!authStore.user?.role || authStore.user.role !== 'admin') {
      return next({ name: 'dashboard' })
    }
  }
  
  // Check for coordinator role
  if (to.meta.requiresCoordinator && authStore.isAuthenticated) {
    if (!authStore.user?.role || !['admin', 'coordinator'].includes(authStore.user.role)) {
      return next({ name: 'dashboard' })
    }
  }
  
  // Continue to the route
  next()
})

// Navigation guard for page titles
router.afterEach((to) => {
  // Set page title
  const defaultTitle = 'Tennis Team Website'
  const pageTitle = to.meta.title || defaultTitle
  document.title = `${pageTitle} | ${defaultTitle}`
})

export default router