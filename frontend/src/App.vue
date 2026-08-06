<template>
  <div v-if="!currentUser" class="login-container">
    <Login @login-success="onLoginSuccess" />
  </div>
  <div v-else class="app-container">
    <!-- Top Header -->
    <header class="top-header">
      <div class="logo-container">
        <div class="logo-icon">NT</div>
        <h1 class="logo-text">Architect <span>CMDB & ITAM</span></h1>
      </div>
      <div class="user-profile-header">
        <div class="user-avatar">{{ userInitials }}</div>
        <div class="user-info">
          <span class="user-name" :title="currentUser.nombre">{{ currentUser.nombre }}</span>
          <span class="user-role">{{ currentUser.role_nombre || 'Lector' }}</span>
        </div>
        <button @click="handleLogout" class="btn btn-secondary" style="width: auto; padding: 0.4rem 0.8rem; font-size: 0.8rem; margin-left: 1rem;">
          🚪 Salir
        </button>
      </div>
    </header>

    <div class="main-layout">
      <!-- Sidebar Navigation -->
      <aside class="sidebar">
        <nav>
          <div class="sidebar-category">Dashboards</div>
          <ul class="nav-links">
            <li v-if="hasModule('dashboard')">
              <a 
                href="#" 
                class="nav-item" 
                :class="{ active: currentView === 'dashboard' }"
                @click.prevent="switchView('dashboard')"
              >
                <span class="nav-icon">📊</span>
                <span>Inicio / Estadísticas</span>
              </a>
            </li>
          </ul>

          <div class="sidebar-category" v-if="hasModule('simulator') || hasModule('itam')">Operaciones</div>
          <ul class="nav-links">
            <li v-if="hasModule('simulator')">
              <a 
                href="#" 
                class="nav-item" 
                :class="{ active: currentView === 'simulator' }"
                @click.prevent="switchView('simulator')"
              >
                <span class="nav-icon">🔮</span>
                <span>Simulador de Impacto</span>
              </a>
            </li>
            <li v-if="hasModule('itam')">
              <a 
                href="#" 
                class="nav-item" 
                :class="{ active: currentView === 'itam' }"
                @click.prevent="switchView('itam')"
              >
                <span class="nav-icon">📦</span>
                <span>Depósito e ITAM</span>
              </a>
            </li>
          </ul>

          <div class="sidebar-category" v-if="hasModule('crud') || currentUser.is_superadmin || hasModule('usuarios_roles')">Administración</div>
          <ul class="nav-links">
            <li v-if="hasModule('crud')">
              <a 
                href="#" 
                class="nav-item" 
                :class="{ active: currentView === 'crud' }"
                @click.prevent="switchView('crud')"
              >
                <span class="nav-icon">📝</span>
                <span>Carga de Datos (CRUD)</span>
              </a>
            </li>
            <li v-if="currentUser.is_superadmin || hasModule('usuarios_roles')">
              <a 
                href="#" 
                class="nav-item" 
                :class="{ active: currentView === 'usuarios_roles' }"
                @click.prevent="switchView('usuarios_roles')"
              >
                <span class="nav-icon">🛡️</span>
                <span>Usuarios y Roles</span>
              </a>
            </li>
          </ul>
        </nav>
      </aside>

      <!-- Main Content Area -->
      <main class="main-content">
        <div class="header-container">
          <h1 class="header-title">{{ viewTitle }}</h1>
          <p class="header-subtitle">{{ viewSubtitle }}</p>
        </div>

        <!-- Views -->
        <KeepAlive>
          <component :is="activeComponent" />
        </KeepAlive>
      </main>
    </div>

    <!-- Floating settings FAB (inspired by yellow settings cog button in reference image) -->
    <button class="settings-fab" title="Configuración de Interfaz" @click="mostrarMensajeSettings">
      ⚙️
    </button>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import axios from 'axios'
import Dashboard from './components/Dashboard.vue'
import ImpactSimulator from './components/ImpactSimulator.vue'
import ITAMPanel from './components/ITAMPanel.vue'
import DataCRUD from './components/DataCRUD.vue'
import UsuariosRoles from './components/UsuariosRoles.vue'
import Login from './components/Login.vue'

// Set up axios interceptor for 401s globally
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('net_cmdb_token')
      localStorage.removeItem('net_cmdb_user')
      delete axios.defaults.headers.common['Authorization']
      window.location.reload()
    }
    return Promise.reject(error)
  }
)

export default {
  name: 'App',
  components: {
    Dashboard,
    ImpactSimulator,
    ITAMPanel,
    DataCRUD,
    UsuariosRoles,
    Login
  },
  setup() {
    const currentView = ref('dashboard')
    const currentUser = ref(null)

    function setFirstAvailableView() {
      if (hasModule('dashboard')) currentView.value = 'dashboard'
      else if (hasModule('simulator')) currentView.value = 'simulator'
      else if (hasModule('itam')) currentView.value = 'itam'
      else if (hasModule('crud')) currentView.value = 'crud'
      else if (currentUser.value.is_superadmin || hasModule('usuarios_roles')) currentView.value = 'usuarios_roles'
    }

    const hasModule = (moduleName) => {
      if (!currentUser.value) return false
      if (currentUser.value.is_superadmin) return true
      return currentUser.value.modules?.some(m => m.module_name === moduleName && m.can_read)
    }

    const onLoginSuccess = (loginData) => {
      currentUser.value = {
        username: loginData.username,
        nombre: loginData.nombre,
        is_superadmin: loginData.is_superadmin,
        role_nombre: loginData.role_nombre,
        modules: loginData.modules
      }
      setFirstAvailableView()
    }

    const handleLogout = () => {
      localStorage.removeItem('net_cmdb_token')
      localStorage.removeItem('net_cmdb_user')
      delete axios.defaults.headers.common['Authorization']
      currentUser.value = null
      currentView.value = 'dashboard'
    }

    const switchView = (view) => {
      if (hasModule(view) || (view === 'usuarios_roles' && currentUser.value.is_superadmin)) {
        currentView.value = view
      }
    }

    const activeComponent = computed(() => {
      switch (currentView.value) {
        case 'dashboard': return 'Dashboard'
        case 'simulator': return 'ImpactSimulator'
        case 'itam': return 'ITAMPanel'
        case 'crud': return 'DataCRUD'
        case 'usuarios_roles': return 'UsuariosRoles'
        default: return 'Dashboard'
      }
    })

    const viewTitle = computed(() => {
      switch (currentView.value) {
        case 'dashboard': return 'Panel de Inicio'
        case 'simulator': return 'Simulador de Impacto'
        case 'itam': return 'Gestión de Depósito e ITAM'
        case 'crud': return 'Panel de Gestión de Datos (CRUD)'
        case 'usuarios_roles': return 'Seguridad y Accesos'
        default: return 'Panel de Inicio'
      }
    })

    const viewSubtitle = computed(() => {
      switch (currentView.value) {
        case 'dashboard': return 'Resumen general del estado de activos, alertas y subestaciones'
        case 'simulator': return 'Visualización de impacto de caída en cascada de red y energía'
        case 'itam': return 'Control de stock físico de equipos de red, energía y cables de planta'
        case 'crud': return 'Carga, edición y eliminación de elementos y dependencias lógicas'
        case 'usuarios_roles': return 'Matriz de permisos, gestión de roles y cuentas de usuario del sistema'
        default: return ''
      }
    })

    const userInitials = computed(() => {
      if (!currentUser.value || !currentUser.value.nombre) return 'US'
      const parts = currentUser.value.nombre.trim().split(/\s+/)
      if (parts.length >= 2) {
        return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
      }
      return parts[0].substring(0, 2).toUpperCase()
    })

    const mostrarMensajeSettings = () => {
      alert("⚙️ Configuración del Portal: Tema 'Architect' Claro Activo.")
    }

    // Load initial user state from localStorage (placed at bottom to avoid TDZ on hasModule)
    const savedToken = localStorage.getItem('net_cmdb_token')
    const savedUser = localStorage.getItem('net_cmdb_user')
    if (savedToken && savedUser) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`
      try {
        currentUser.value = JSON.parse(savedUser)
        setFirstAvailableView()
      } catch (e) {
        handleLogout()
      }
    }

    return {
      currentView,
      currentUser,
      activeComponent,
      viewTitle,
      viewSubtitle,
      userInitials,
      mostrarMensajeSettings,
      hasModule,
      onLoginSuccess,
      handleLogout,
      switchView
    }
  }
}
</script>

<style>
/* App layout containers and structure are handled globally in style.css */
</style>
