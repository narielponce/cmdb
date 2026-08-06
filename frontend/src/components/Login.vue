<template>
  <div class="login-wrapper">
    <div class="login-card glass-card">
      <div class="login-logo">
        <div class="logo-icon">NT</div>
        <div class="logo-text">CMDB & ITAM</div>
      </div>
      <h2 class="login-title">Control de Acceso</h2>
      <p class="login-subtitle">Gestión de Infraestructura de Red</p>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">Usuario</label>
          <input 
            type="text" 
            id="username" 
            v-model="username" 
            placeholder="Ingrese su legajo o usuario" 
            required 
            class="form-control"
            :disabled="loading"
          />
        </div>
        
        <div class="form-group">
          <label for="password">Contraseña</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            placeholder="••••••••" 
            required 
            class="form-control"
            :disabled="loading"
          />
        </div>
        
        <div v-if="error" class="login-error">
          <span>⚠️</span> {{ error }}
        </div>
        
        <button type="submit" class="btn btn-primary btn-block btn-login" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Iniciar Sesión</span>
        </button>
      </form>
      
      <div class="login-footer">
        <p>NetTrack CMDB & ITAM Operations v2.0</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'

export default {
  name: 'Login',
  emits: ['login-success'],
  setup(props, { emit }) {
    const username = ref('')
    const password = ref('')
    const error = ref('')
    const loading = ref(false)

    const handleLogin = async () => {
      loading.value = true
      error.value = ''
      try {
        const response = await axios.post('/api/auth/login', {
          username: username.value,
          password: password.value
        })
        
        const data = response.data
        // Store JWT token and user info
        localStorage.setItem('net_cmdb_token', data.access_token)
        localStorage.setItem('net_cmdb_user', JSON.stringify({
          username: data.username,
          nombre: data.nombre,
          is_superadmin: data.is_superadmin,
          modules: data.modules
        }))
        
        // Configure default auth header for axios
        axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
        
        emit('login-success', data)
      } catch (err) {
        console.error(err)
        if (err.response && err.response.data && err.response.data.detail) {
          error.value = err.response.data.detail
        } else {
          error.value = 'Error al conectar con el servidor de autenticación.'
        }
      } finally {
        loading.value = false
      }
    }

    return {
      username,
      password,
      error,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  width: 100vw;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 9999;
  background: linear-gradient(135deg, #f1f4f6 0%, #d8e2eb 100%);
  overflow: hidden;
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
  background-color: #ffffff;
  animation: fadeIn 0.6s ease-out;
  position: relative;
}

.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #3f6ad8, #30c5d2);
  border-radius: 12px 12px 0 0;
}

.login-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  gap: 12px;
}

.logo-icon {
  background: radial-gradient(circle, #30c5d2 0%, #3f6ad8 100%);
  color: white;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.25rem;
  box-shadow: 0 0 10px rgba(63, 106, 216, 0.2);
}

.logo-text {
  font-size: 1.35rem;
  font-weight: 700;
  color: #1f2937;
  letter-spacing: -0.025em;
}

.login-title {
  text-align: center;
  font-size: 1.5rem;
  color: #3f4254;
  margin: 0 0 8px 0;
  font-weight: 700;
}

.login-subtitle {
  text-align: center;
  font-size: 0.875rem;
  color: #6c757d;
  margin: 0 0 32px 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #5e6278;
  text-align: left;
}

.form-control {
  background: #ffffff;
  border: 1px solid #ced4da;
  border-radius: 6px;
  padding: 12px 16px;
  color: #495057;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  width: 100%;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: #3f6ad8;
  box-shadow: 0 0 0 3px rgba(63, 106, 216, 0.15);
}

.login-error {
  background: rgba(217, 37, 80, 0.1);
  border: 1px solid rgba(217, 37, 80, 0.2);
  color: #d92550;
  padding: 12px;
  border-radius: 6px;
  font-size: 0.875rem;
  text-align: left;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-login {
  padding: 14px;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 6px;
  margin-top: 10px;
  transition: all 0.3s ease;
  cursor: pointer;
  box-sizing: border-box;
  width: 100%;
  background-color: #3f6ad8;
  color: #ffffff;
  border: none;
  box-shadow: 0 4px 10px rgba(63, 106, 216, 0.2);
}

.btn-login:hover:not(:disabled) {
  background-color: #2f56b8;
  transform: translateY(-1.5px);
  box-shadow: 0 6px 15px rgba(63, 106, 216, 0.3);
}

.login-footer {
  text-align: center;
  margin-top: 40px;
  font-size: 0.75rem;
  color: #8892a0;
}

.spinner {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
