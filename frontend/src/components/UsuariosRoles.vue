<template>
  <div class="users-roles-container">
    <!-- Tabs Header -->
    <div class="tabs-header">
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'users' }" 
        @click="activeTab = 'users'"
      >
        👥 Usuarios
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'roles' }" 
        @click="activeTab = 'roles'"
      >
        🔑 Roles
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'permissions' }" 
        @click="activeTab = 'permissions'"
      >
        🛡️ Permisos por Rol
      </button>
    </div>

    <!-- Tab 1: Users -->
    <div v-if="activeTab === 'users'" class="tab-pane">
      <div class="split-layout">
        <!-- Users List -->
        <div class="glass-panel list-panel">
          <div class="panel-header">
            <h3 class="panel-title">Listado de Usuarios</h3>
          </div>
          <table class="custom-table">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Nombre</th>
                <th>Rol</th>
                <th>Superadmin</th>
                <th>Ámbito</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.username }}</td>
                <td>{{ user.nombre }}</td>
                <td>
                  <span v-if="user.is_superadmin" class="badge badge-superadmin">Superadmin</span>
                  <span v-else-if="user.role_nombre" class="badge badge-rol">{{ user.role_nombre }}</span>
                  <span v-else class="text-muted">Sin Rol</span>
                </td>
                <td>{{ user.is_superadmin ? 'Sí' : 'No' }}</td>
                <td>{{ user.dominio_asignado || 'ALL' }}</td>
                <td>
                  <button @click="editUser(user)" class="btn-action edit-btn">✏️</button>
                  <button @click="confirmDeleteUser(user)" class="btn-action delete-btn">🗑️</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- User Form -->
        <div class="glass-panel form-panel">
          <div class="panel-header">
            <h3 class="panel-title">{{ userForm.id ? 'Editar Usuario' : 'Nuevo Usuario' }}</h3>
          </div>
          <form @submit.prevent="saveUser" class="form-container">
            <div class="form-group">
              <label>Nombre de Usuario (Logon)</label>
              <input v-model="userForm.username" type="text" required class="form-control" placeholder="Legajo o ID" />
            </div>
            <div class="form-group">
              <label>Nombre Completo</label>
              <input v-model="userForm.nombre" type="text" required class="form-control" placeholder="Nombre y Apellido" />
            </div>
            <div class="form-group">
              <label>Contraseña {{ userForm.id ? '(Dejar en blanco para no cambiar)' : '' }}</label>
              <input v-model="userForm.password" type="password" :required="!userForm.id" class="form-control" placeholder="••••••••" />
            </div>
            <div class="form-group">
              <label>Rol asignado</label>
              <select v-model="userForm.role_id" class="form-control" :disabled="userForm.is_superadmin">
                <option :value="null">Sin Rol (Lectura básica)</option>
                <option v-for="role in roles" :key="role.id" :value="role.id">
                  {{ role.nombre }}
                </option>
              </select>
            </div>
            <div class="form-group" v-if="!userForm.is_superadmin">
              <label>Ámbito / Dominio de Activos</label>
              <select v-model="userForm.dominio_asignado" class="form-control">
                <option value="ALL">ALL (Todos los dominios)</option>
                <option value="NETWORK">NETWORK (Red / IT)</option>
                <option value="FACILITIES">FACILITIES (Infraestructura / Energía)</option>
                <option value="SHOPFLOOR">SHOPFLOOR (Planta / OT)</option>
              </select>
            </div>
            <div class="form-group row-checkbox">
              <input type="checkbox" id="is_superadmin" v-model="userForm.is_superadmin" @change="onSuperadminChange" />
              <label for="is_superadmin">Es Superadministrador (Bypass de seguridad total)</label>
            </div>

            <div v-if="userMessage.text" :class="`alert alert-${userMessage.type}`">
              {{ userMessage.text }}
            </div>

            <div class="form-actions">
              <button type="button" @click="resetUserForm" class="btn btn-secondary">Cancelar</button>
              <button type="submit" class="btn btn-primary">Guardar</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Tab 2: Roles -->
    <div v-if="activeTab === 'roles'" class="tab-pane">
      <div class="split-layout">
        <!-- Roles List -->
        <div class="glass-panel list-panel">
          <div class="panel-header">
            <h3 class="panel-title">Listado de Roles</h3>
          </div>
          <table class="custom-table">
            <thead>
              <tr>
                <th>Rol</th>
                <th>Descripción</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="role in roles" :key="role.id">
                <td><strong>{{ role.nombre }}</strong></td>
                <td>{{ role.descripcion }}</td>
                <td>
                  <button @click="editRole(role)" class="btn-action edit-btn">✏️</button>
                  <button @click="confirmDeleteRole(role)" class="btn-action delete-btn">🗑️</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Role Form -->
        <div class="glass-panel form-panel">
          <div class="panel-header">
            <h3 class="panel-title">{{ roleForm.id ? 'Editar Rol' : 'Nuevo Rol' }}</h3>
          </div>
          <form @submit.prevent="saveRole" class="form-container">
            <div class="form-group">
              <label>Nombre del Rol</label>
              <input v-model="roleForm.nombre" type="text" required class="form-control" placeholder="Ej: Operador de Red" />
            </div>
            <div class="form-group">
              <label>Descripción</label>
              <textarea v-model="roleForm.descripcion" class="form-control" placeholder="Descripción de las funciones" rows="3"></textarea>
            </div>

            <div v-if="roleMessage.text" :class="`alert alert-${roleMessage.type}`">
              {{ roleMessage.text }}
            </div>

            <div class="form-actions">
              <button type="button" @click="resetRoleForm" class="btn btn-secondary">Cancelar</button>
              <button type="submit" class="btn btn-primary">Guardar</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Tab 3: Permissions Matrix -->
    <div v-if="activeTab === 'permissions'" class="tab-pane">
      <div class="glass-panel permissions-panel">
        <div class="panel-header-flex">
          <h3 class="panel-title">Matriz de Permisos por Rol</h3>
          <div class="role-selector">
            <label>Seleccionar Rol: </label>
            <select v-model="selectedRoleId" @change="loadRolePermissions" class="form-control inline-select">
              <option :value="null" disabled>Seleccione un Rol...</option>
              <option v-for="role in roles" :key="role.id" :value="role.id">
                {{ role.nombre }}
              </option>
            </select>
          </div>
        </div>

        <div v-if="selectedRoleId" class="matrix-container">
          <p class="matrix-info">Configure qué módulos puede visualizar (Lectura) y modificar/crear (Escritura) este Rol:</p>
          <table class="custom-table permissions-matrix">
            <thead>
              <tr>
                <th>Módulo del Sistema</th>
                <th class="text-center">Permitir Acceso (Lectura)</th>
                <th class="text-center">Permitir Modificaciones (Escritura)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="mod in permissionMatrix" :key="mod.module_name">
                <td>
                  <div class="module-info">
                    <span class="module-icon">{{ getModuleIcon(mod.module_name) }}</span>
                    <div>
                      <span class="module-title">{{ getModuleDisplayName(mod.module_name) }}</span>
                      <span class="module-desc">{{ getModuleDescription(mod.module_name) }}</span>
                    </div>
                  </div>
                </td>
                <td class="text-center">
                  <input type="checkbox" v-model="mod.can_read" @change="onReadChange(mod)" />
                </td>
                <td class="text-center">
                  <input type="checkbox" v-model="mod.can_write" :disabled="!mod.can_read" />
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="permissionMessage.text" :class="`alert alert-${permissionMessage.type}`">
            {{ permissionMessage.text }}
          </div>

          <div class="matrix-actions">
            <button @click="savePermissions" class="btn btn-primary btn-save-perm">Guardar Cambios de Permisos</button>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>⚠️ Seleccione un rol del menú superior para administrar su matriz de accesos.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'UsuariosRoles',
  setup() {
    const activeTab = ref('users')
    const users = ref([])
    const roles = ref([])
    
    // Forms state
    const userForm = ref({
      id: null,
      username: '',
      nombre: '',
      password: '',
      role_id: null,
      is_superadmin: false,
      dominio_asignado: 'ALL'
    })
    
    const roleForm = ref({
      id: null,
      nombre: '',
      descripcion: ''
    })

    // Feedback messages
    const userMessage = ref({ text: '', type: 'success' })
    const roleMessage = ref({ text: '', type: 'success' })
    const permissionMessage = ref({ text: '', type: 'success' })

    // Permissions Matrix state
    const selectedRoleId = ref(null)
    const permissionMatrix = ref([])

    const modulesList = [
      { key: 'dashboard', name: 'Inicio / Indicadores', desc: 'Panel principal, KPIs de stock, alertas y estado general de planta.', icon: '🏠' },
      { key: 'simulator', name: 'Simulador de Impacto', desc: 'Ejecución de simulaciones lógicas de corte eléctrico o red.', icon: '🔮' },
      { key: 'itam', name: 'Depósito e ITAM', desc: 'Administración de inventarios de racks, insumos y descargas de actas de remitos PDF.', icon: '📦' },
      { key: 'crud', name: 'Carga de Datos (CRUD)', desc: 'Formularios y grillas de configuración de las 10 entidades primarias.', icon: '📝' }
    ]

    const loadData = async () => {
      try {
        const usersRes = await axios.get('/api/usuarios')
        users.value = usersRes.data
        
        const rolesRes = await axios.get('/api/roles')
        roles.value = rolesRes.data
      } catch (err) {
        console.error('Error al cargar usuarios y roles:', err)
      }
    }

    onMounted(() => {
      loadData()
    })

    // --- USUARIOS LOGIC ---
    const resetUserForm = () => {
      userForm.value = {
        id: null,
        username: '',
        nombre: '',
        password: '',
        role_id: null,
        is_superadmin: false,
        dominio_asignado: 'ALL'
      }
      userMessage.value = { text: '', type: 'success' }
    }

    const editUser = (user) => {
      userForm.value = {
        id: user.id,
        username: user.username,
        nombre: user.nombre,
        password: '',
        role_id: user.role_id,
        is_superadmin: user.is_superadmin,
        dominio_asignado: user.dominio_asignado || 'ALL'
      }
      userMessage.value = { text: '', type: 'success' }
    }

    const saveUser = async () => {
      userMessage.value = { text: '', type: 'success' }
      try {
        if (userForm.value.id) {
          // Edit
          const payload = {
            username: userForm.value.username,
            nombre: userForm.value.nombre,
            role_id: userForm.value.is_superadmin ? null : userForm.value.role_id,
            is_superadmin: userForm.value.is_superadmin,
            dominio_asignado: userForm.value.is_superadmin ? 'ALL' : userForm.value.dominio_asignado
          }
          if (userForm.value.password) {
            payload.password = userForm.value.password
          }
          await axios.put(`/api/usuarios/${userForm.value.id}`, payload)
          userMessage.value = { text: 'Usuario actualizado correctamente.', type: 'success' }
        } else {
          // Create
          await axios.post('/api/usuarios', userForm.value)
          userMessage.value = { text: 'Usuario creado correctamente.', type: 'success' }
        }
        resetUserForm()
        loadData()
      } catch (err) {
        userMessage.value = { 
          text: err.response?.data?.detail || 'Error al guardar el usuario.', 
          type: 'danger' 
        }
      }
    }

    const confirmDeleteUser = async (user) => {
      if (confirm(`¿Está seguro de eliminar al usuario "${user.nombre}"?`)) {
        try {
          await axios.delete(`/api/usuarios/${user.id}`)
          loadData()
        } catch (err) {
          alert(err.response?.data?.detail || 'Error al eliminar el usuario.')
        }
      }
    }

    const onSuperadminChange = () => {
      if (userForm.value.is_superadmin) {
        userForm.value.role_id = null
      }
    }

    // --- ROLES LOGIC ---
    const resetRoleForm = () => {
      roleForm.value = {
        id: null,
        nombre: '',
        descripcion: ''
      }
      roleMessage.value = { text: '', type: 'success' }
    }

    const editRole = (role) => {
      roleForm.value = {
        id: role.id,
        nombre: role.nombre,
        descripcion: role.descripcion
      }
      roleMessage.value = { text: '', type: 'success' }
    }

    const saveRole = async () => {
      roleMessage.value = { text: '', type: 'success' }
      try {
        if (roleForm.value.id) {
          await axios.put(`/api/roles/${roleForm.value.id}`, roleForm.value)
          roleMessage.value = { text: 'Rol actualizado correctamente.', type: 'success' }
        } else {
          await axios.post('/api/roles', roleForm.value)
          roleMessage.value = { text: 'Rol creado correctamente.', type: 'success' }
        }
        resetRoleForm()
        loadData()
      } catch (err) {
        roleMessage.value = { 
          text: err.response?.data?.detail || 'Error al guardar el rol.', 
          type: 'danger' 
        }
      }
    }

    const confirmDeleteRole = async (role) => {
      if (confirm(`¿Está seguro de eliminar el rol "${role.nombre}"? Se perderán todas sus configuraciones de permisos.`)) {
        try {
          await axios.delete(`/api/roles/${role.id}`)
          if (selectedRoleId.value === role.id) {
            selectedRoleId.value = null
            permissionMatrix.value = []
          }
          loadData()
        } catch (err) {
          alert(err.response?.data?.detail || 'Error al eliminar el rol.')
        }
      }
    }

    // --- PERMISSION MATRIX LOGIC ---
    const loadRolePermissions = () => {
      permissionMessage.value = { text: '', type: 'success' }
      if (!selectedRoleId.value) return
      
      const role = roles.value.find(r => r.id === selectedRoleId.value)
      if (!role) return
      
      // Build matrix based on our modules list
      permissionMatrix.value = modulesList.map(mod => {
        // Find existing configuration for this module in the role modules
        const existing = role.modules?.find(m => m.module_name === mod.key)
        return {
          module_name: mod.key,
          can_read: existing ? existing.can_read : false,
          can_write: existing ? existing.can_write : false
        }
      })
    }

    const onReadChange = (mod) => {
      if (!mod.can_read) {
        mod.can_write = false
      }
    }

    const savePermissions = async () => {
      permissionMessage.value = { text: '', type: 'success' }
      try {
        await axios.put(`/api/roles/${selectedRoleId.value}/permisos`, permissionMatrix.value)
        permissionMessage.value = { text: 'Permisos del Rol guardados correctamente.', type: 'success' }
        loadData() // reload configurations
      } catch (err) {
        permissionMessage.value = { 
          text: err.response?.data?.detail || 'Error al guardar los permisos.', 
          type: 'danger' 
        }
      }
    }

    // Helpers
    const getModuleDisplayName = (key) => modulesList.find(m => m.key === key)?.name || key
    const getModuleDescription = (key) => modulesList.find(m => m.key === key)?.desc || ''
    const getModuleIcon = (key) => modulesList.find(m => m.key === key)?.icon || '⚙️'

    return {
      activeTab,
      users,
      roles,
      userForm,
      roleForm,
      userMessage,
      roleMessage,
      permissionMessage,
      selectedRoleId,
      permissionMatrix,
      resetUserForm,
      editUser,
      saveUser,
      confirmDeleteUser,
      onSuperadminChange,
      resetRoleForm,
      editRole,
      saveRole,
      confirmDeleteRole,
      loadRolePermissions,
      onReadChange,
      savePermissions,
      getModuleDisplayName,
      getModuleDescription,
      getModuleIcon
    }
  }
}
</script>

<style scoped>
.users-roles-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  animation: fadeIn 0.4s ease-out;
}

.split-layout {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 24px;
}

@media (max-width: 992px) {
  .split-layout {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

.panel-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 16px;
  margin-bottom: 20px;
}

.role-selector {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-selector label {
  font-weight: 600;
  color: #a3b8cc;
  font-size: 0.9rem;
}

.inline-select {
  width: 220px;
  padding: 8px 12px;
}

.badge-superadmin {
  background: rgba(220, 53, 69, 0.15);
  color: #ff6b76;
  border: 1px solid rgba(220, 53, 69, 0.3);
}

.badge-rol {
  background: rgba(0, 86, 179, 0.15);
  color: #66b0ff;
  border: 1px solid rgba(0, 86, 179, 0.3);
}

.row-checkbox {
  flex-direction: row !important;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 6px 0;
}

.row-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  margin: 0;
  cursor: pointer;
}

.row-checkbox label {
  cursor: pointer;
  margin: 0;
  font-size: 0.9rem;
  display: inline-block !important;
  text-transform: none !important;
  letter-spacing: normal !important;
  color: var(--text-main) !important;
}

.alert {
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  text-align: left;
}

.alert-success {
  background: rgba(40, 167, 69, 0.12);
  border: 1px solid rgba(40, 167, 69, 0.25);
  color: #55c970;
}

.alert-danger {
  background: rgba(220, 53, 69, 0.12);
  border: 1px solid rgba(220, 53, 69, 0.25);
  color: #ff6b76;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 12px;
}

.matrix-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  animation: fadeIn 0.3s ease-out;
}

.matrix-info {
  font-size: 0.9rem;
  color: #8fa0ba;
  text-align: left;
  margin: 0;
}

.module-info {
  display: flex;
  align-items: center;
  gap: 16px;
  text-align: left;
}

.module-icon {
  font-size: 1.5rem;
  background: rgba(255, 255, 255, 0.04);
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.module-title {
  display: block;
  font-weight: 600;
  color: #ffffff;
  font-size: 0.95rem;
}

.module-desc {
  display: block;
  font-size: 0.8rem;
  color: #8fa0ba;
  margin-top: 2px;
}

.permissions-matrix input[type="checkbox"] {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.permissions-matrix input[type="checkbox"]:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.matrix-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

.btn-save-perm {
  padding: 12px 24px;
  font-size: 0.95rem;
}

.empty-state {
  padding: 60px;
  text-align: center;
  font-size: 1.05rem;
  color: #8fa0ba;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
