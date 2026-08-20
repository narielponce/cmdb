<template>
  <div class="dashboard-container">
    <!-- Top KPI Grid -->
    <div class="grid-cols-3 metric-grid">
      <!-- KPI 1 -->
      <div class="metric-card navy">
        <div class="metric-header">
          <span class="metric-label">Total de Activos ITAM</span>
          <div class="metric-icon-wrapper">
            <span>📦</span>
          </div>
        </div>
        <div class="metric-value">{{ loading ? '...' : stats.total_activos_itam }}</div>
        <div class="metric-delta delta-green">
          <span>Activos</span>
          <span class="delta-desc">en el sistema</span>
        </div>
      </div>

      <!-- KPI 2 -->
      <div class="metric-card blue-gradient">
        <div class="metric-header">
          <span class="metric-label">Subestaciones Activas</span>
          <div class="metric-icon-wrapper">
            <span>⚡</span>
          </div>
        </div>
        <div class="metric-value">{{ loading ? '...' : stats.subestaciones_activas }}</div>
        <div class="metric-delta delta-green">
          <span>100%</span>
          <span class="delta-desc">operativas</span>
        </div>
      </div>

      <!-- KPI 3 -->
      <div class="metric-card green-gradient">
        <div class="metric-header">
          <span class="metric-label">Equipos en Depósito</span>
          <div class="metric-icon-wrapper">
            <span>🏢</span>
          </div>
        </div>
        <div class="metric-value">{{ loading ? '...' : stats.equipos_en_deposito }}</div>
        <div class="metric-delta delta-green">
          <span>Listo para desplegar</span>
        </div>
      </div>
    </div>

    <!-- Main Dashboard Grid -->
    <div class="grid-cols-2 dashboard-main-grid">
      <!-- System Health and Infrastructure Status -->
      <div class="glass-panel status-panel">
        <div class="panel-header">
          <h3 class="panel-title">⚡ Estado de Subestaciones e Infraestructura</h3>
          <span class="pulse-indicator"></span>
        </div>
        
        <div class="status-list">
          <div class="status-item">
            <div class="status-info">
              <span class="status-name">Subestación Industrial A</span>
              <span class="status-sub">Alimentación principal activa</span>
            </div>
            <span class="badge badge-produccion">🟢 Operativo</span>
          </div>

          <div class="status-item">
            <div class="status-info">
              <span class="status-name">Subestación Logística B</span>
              <span class="status-sub">Operando sin pérdidas</span>
            </div>
            <span class="badge badge-produccion">🟢 Operativo</span>
          </div>

          <div class="status-item">
            <div class="status-info">
              <span class="status-name">UPS Central Sala Racks</span>
              <span class="status-sub">Batería baja - Cambio requerido</span>
            </div>
            <span class="badge badge-warning-custom">🟡 Mantenimiento</span>
          </div>

          <div class="status-item">
            <div class="status-info">
              <span class="status-name">Switch Core Distribución</span>
              <span class="status-sub">Tráfico normal - 10 Gbps</span>
            </div>
            <span class="badge badge-produccion">🟢 Operativo</span>
          </div>

          <div class="status-item">
            <div class="status-info">
              <span class="status-name">Subestación Administración C</span>
              <span class="status-sub">Inspección programada para mañana</span>
            </div>
            <span class="badge badge-deposito">🟢 Listo</span>
          </div>
        </div>
      </div>

      <!-- Recent Alerts and Logs -->
      <div class="glass-panel alerts-panel">
        <div class="panel-header">
          <h3 class="panel-title">🚨 Alertas Recientes e Incidentes</h3>
        </div>

        <div class="alert-list">
          <div class="alert-log-item log-critical">
            <span class="log-dot"></span>
            <div class="log-content">
              <div class="log-title">Alerta de Temperatura Alta</div>
              <div class="log-meta">Rack Principal 02 • Hace 10 mins</div>
            </div>
          </div>

          <div class="alert-log-item log-warning">
            <span class="log-dot"></span>
            <div class="log-content">
              <div class="log-title">Reemplazo de Baterías de UPS Expirando</div>
              <div class="log-meta">UPS Sala Racks • Hace 2 horas</div>
            </div>
          </div>

          <div class="alert-log-item log-info">
            <span class="log-dot"></span>
            <div class="log-content">
              <div class="log-title">Ingreso a Depósito: 10x Patch Cords Cat6</div>
              <div class="log-meta">Registrado por: Ariel M. • Hace 1 día</div>
            </div>
          </div>

          <div class="alert-log-item log-info">
            <span class="log-dot"></span>
            <div class="log-content">
              <div class="log-title">Simulación de Impacto Ejecutada</div>
              <div class="log-meta">Prueba de corte en Subestación A • Hace 2 días</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions Section -->
    <div class="glass-panel quick-actions-panel">
      <h3 class="panel-title" style="margin-bottom: 1.25rem;">⚡ Accesos Rápidos de Gestión</h3>
      <div class="actions-grid">
        <div class="action-card" @click="$emit('navigate', 'simulator')">
          <span class="action-icon">🔮</span>
          <div class="action-details">
            <h4>Simular Caída de Red</h4>
            <p>Evalúa el impacto de caída en cascada antes de realizar mantenimiento.</p>
          </div>
        </div>

        <div class="action-card" @click="$emit('navigate', 'itam')">
          <span class="action-icon">📥</span>
          <div class="action-details">
            <h4>Registrar Entrada</h4>
            <p>Añade nuevos equipos, cables o insumos al depósito central.</p>
          </div>
        </div>

        <div class="action-card" @click="$emit('navigate', 'crud')">
          <span class="action-icon">📝</span>
          <div class="action-details">
            <h4>Gestionar CMDB</h4>
            <p>Crea, edita o elimina subestaciones, racks, UPS y servidores.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'Dashboard',
  emits: ['navigate'],
  setup() {
    const stats = ref({
      total_activos_itam: 0,
      equipos_en_deposito: 0,
      subestaciones_activas: 0
    })

    const loading = ref(false)

    const fetchStats = async () => {
      loading.value = true
      try {
        const response = await axios.get('/api/dashboard/stats')
        stats.value = response.data
      } catch (error) {
        console.error("Error al cargar estadísticas de inicio:", error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchStats()
    })

    return {
      stats,
      loading
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.metric-grid {
  margin-top: 0.5rem;
}

.glass-card {
  position: relative;
  background-color: var(--panel-bg);
  border: 1px solid var(--panel-border);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all var(--transition-fast);
}

.glass-card:hover {
  transform: translateY(-2px);
  border-color: var(--primary);
  box-shadow: 0 4px 20px var(--accent-glow);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.metric-icon {
  font-size: 1.5rem;
}

.delta-desc {
  color: var(--text-muted);
  margin-left: 0.25rem;
  font-weight: normal;
}

/* Main Grid Layout */
.dashboard-main-grid {
  margin-bottom: 0.5rem;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.panel-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-main);
}

/* Pulse indicator for live simulation state */
.pulse-indicator {
  width: 10px;
  height: 10px;
  background-color: var(--success);
  border-radius: 50%;
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  animation: pulse 1.6s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(16, 185, 129, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
  }
}

/* Status list */
.status-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--panel-border);
  border-radius: 8px;
  transition: background-color var(--transition-fast);
}

.status-item:hover {
  background-color: rgba(255, 255, 255, 0.04);
}

.status-info {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.status-name {
  font-weight: 500;
  font-size: 0.92rem;
  color: var(--text-main);
}

.status-sub {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.badge-warning-custom {
  background-color: rgba(245, 158, 11, 0.15);
  color: var(--warning);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

/* Alert log list */
.alert-list {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.alert-log-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  border-left: 3px solid transparent;
  background-color: rgba(255, 255, 255, 0.01);
  text-align: left;
}

.log-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 0.35rem;
  flex-shrink: 0;
}

.log-content {
  display: flex;
  flex-direction: column;
}

.log-title {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-main);
}

.log-meta {
  font-size: 0.78rem;
  color: var(--text-muted);
}

/* Alert categories styles */
.log-critical {
  border-left-color: var(--danger);
  background-color: rgba(239, 68, 68, 0.03);
}
.log-critical .log-dot {
  background-color: var(--danger);
}

.log-warning {
  border-left-color: var(--warning);
  background-color: rgba(245, 158, 11, 0.03);
}
.log-warning .log-dot {
  background-color: var(--warning);
}

.log-info {
  border-left-color: var(--primary);
  background-color: rgba(0, 122, 255, 0.03);
}
.log-info .log-dot {
  background-color: var(--primary);
}

/* Quick Actions Cards */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.25rem;
}

.action-card {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem;
  background-color: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--panel-border);
  border-radius: 8px;
  transition: all var(--transition-fast);
  text-align: left;
  cursor: pointer;
}

.action-card:hover {
  background-color: rgba(0, 122, 255, 0.05);
  border-color: var(--primary);
  transform: translateY(-1px);
}

.action-icon {
  font-size: 1.75rem;
  line-height: 1;
}

.action-details h4 {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 0.25rem;
}

.action-details p {
  font-size: 0.8rem;
  color: var(--text-muted);
  line-height: 1.4;
}
</style>
