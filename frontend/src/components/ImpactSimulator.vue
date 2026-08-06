<template>
  <div class="simulator-container">
    <div class="grid-cols-2">
      <!-- Configuration Panel -->
      <div class="glass-panel">
        <h2 style="margin-bottom: 1.25rem; font-size: 1.25rem;">Configuración del Simulador</h2>
        
        <div class="form-group">
          <label class="form-label">Seleccione el Tipo de Evento a simular:</label>
          <div style="display: flex; flex-direction: column; gap: 0.5rem; margin-top: 0.5rem;">
            <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
              <input type="radio" v-model="tipoCorte" value="Subestación" @change="cargarEntidades" />
              <span>Corte de Subestación</span>
            </label>
            <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
              <input type="radio" v-model="tipoCorte" value="Blindobarra" @change="cargarEntidades" />
              <span>Corte de Blindobarra</span>
            </label>
            <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
              <input type="radio" v-model="tipoCorte" value="UPS" @change="cargarEntidades" />
              <span>Corte de UPS</span>
            </label>
            <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
              <input type="radio" v-model="tipoCorte" value="Rack" @change="cargarEntidades" />
              <span>Caída de Rack Room</span>
            </label>
            <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
              <input type="radio" v-model="tipoCorte" value="Servidor" @change="cargarEntidades" />
              <span>Mantenimiento de Servidor TI</span>
            </label>
          </div>
        </div>

        <div class="form-group" v-if="entidades.length > 0">
          <label class="form-label" for="target-select">Seleccione el Elemento:</label>
          <select id="target-select" class="form-select" v-model="targetId">
            <option v-for="item in entidades" :key="item.id" :value="item.id">
              {{ item.nombre }}
            </option>
          </select>
        </div>
        <div v-else-if="loadingEntidades" class="form-group">
          <p style="color: var(--text-muted); font-size: 0.9rem;">Cargando lista...</p>
        </div>
        <div v-else class="form-group">
          <p style="color: var(--warning); font-size: 0.9rem;">No hay elementos disponibles para simular.</p>
        </div>

        <div v-if="tipoCorte === 'Servidor' && selectedServerInfo" class="server-details-card">
          <h4 style="font-size: 0.9rem; margin-bottom: 0.5rem;">Detalles del Servidor:</h4>
          <ul style="font-size: 0.85rem; color: var(--text-muted); list-style: none; display: flex; flex-direction: column; gap: 0.25rem;">
            <li><strong>OS:</strong> {{ selectedServerInfo.sistema_operativo }}</li>
            <li><strong>Tipo:</strong> {{ selectedServerInfo.tipo_servidor }}</li>
            <li><strong>IP:</strong> {{ selectedServerInfo.ip }}</li>
          </ul>
        </div>

        <button 
          class="btn btn-primary" 
          :disabled="!targetId || loadingSimulation"
          @click="simularImpacto"
          style="margin-top: 1rem;"
        >
          <span v-if="loadingSimulation">Simulando...</span>
          <span v-else>🚨 Simular Impacto</span>
        </button>
      </div>

      <!-- Overview Info Panel -->
      <div class="glass-panel" style="display: flex; flex-direction: column; justify-content: center; gap: 1rem;">
        <h3 style="font-size: 1.2rem; color: var(--brand-accent);">¿Cómo funciona el simulador?</h3>
        <p style="font-size: 0.9rem; color: var(--text-muted);">
          El Gemelo Digital mapea las dependencias lógicas y físicas de la fábrica. 
          Al simular un corte en un nodo crítico (por ejemplo, una Subestación o Blindobarra), el sistema calcula en cascada todos los dispositivos de red sin alimentación, los switches de comunicación inoperativos y los hosts finales de la planta (PLCs, terminales de calidad, cámaras) que perderán conexión de red.
        </p>
        <p style="font-size: 0.9rem; color: var(--text-muted);">
          Para servidores de TI, simula qué sistemas SCADA, MES o de logística se verán interrumpidos y qué procesos de planta o líneas de producción se detendrán como consecuencia directa.
        </p>
      </div>
    </div>

    <!-- Simulation Results -->
    <div v-if="simulacionEjecutada" class="simulation-results-area" style="margin-top: 2rem;">
      <div class="alert alert-warning" style="display: flex; align-items: center; justify-content: space-between;">
        <span>Simulando corte/mantenimiento en: <strong>{{ targetNombre }}</strong> ({{ tipoCorte }})</span>
        <span class="pulse-indicator">● EN SIMULACIÓN</span>
      </div>

      <div class="results-dashboard-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem; margin-top: 1.5rem;">
        
        <!-- Blindobarras -->
        <div v-if="resultados.blindobarras && resultados.blindobarras.length > 0" class="glass-panel" style="padding: 1.25rem;">
          <div class="metric-card" style="margin-bottom: 1rem;">
            <span class="metric-label">⚡ Blindobarras Caídas</span>
            <span class="metric-value">{{ resultados.blindobarras.length }}</span>
          </div>
          <div class="table-container">
            <table class="custom-table">
              <thead>
                <tr><th>Nombre Blindobarra</th></tr>
              </thead>
              <tbody>
                <tr v-for="b in resultados.blindobarras" :key="b.id"><td>{{ b.nombre }}</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- UPSs -->
        <div v-if="resultados.ups && resultados.ups.length > 0" class="glass-panel" style="padding: 1.25rem;">
          <div class="metric-card" style="margin-bottom: 1rem;">
            <span class="metric-label">🔋 UPS Fuera de Servicio</span>
            <span class="metric-value">{{ resultados.ups.length }}</span>
          </div>
          <div class="table-container">
            <table class="custom-table">
              <thead>
                <tr><th>Nombre UPS</th></tr>
              </thead>
              <tbody>
                <tr v-for="u in resultados.ups" :key="u.id"><td>{{ u.nombre }}</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Racks -->
        <div v-if="resultados.racks && resultados.racks.length > 0" class="glass-panel" style="padding: 1.25rem;">
          <div class="metric-card" style="margin-bottom: 1rem;">
            <span class="metric-label">🗄️ Racks Afectados</span>
            <span class="metric-value">{{ resultados.racks.length }}</span>
          </div>
          <div class="table-container">
            <table class="custom-table">
              <thead>
                <tr><th>Nombre Rack</th></tr>
              </thead>
              <tbody>
                <tr v-for="r in resultados.racks" :key="r.id"><td>{{ r.nombre }}</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Switches -->
        <div v-if="resultados.switches && resultados.switches.length > 0" class="glass-panel" style="padding: 1.25rem;">
          <div class="metric-card" style="margin-bottom: 1rem;">
            <span class="metric-label">🔌 Switches Inoperativos</span>
            <span class="metric-value">{{ resultados.switches.length }}</span>
          </div>
          <div class="table-container">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>Switch</th>
                  <th>IP</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="sw in resultados.switches" :key="sw.id">
                  <td>{{ sw.nombre }}</td>
                  <td>{{ sw.ip }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Servidores -->
        <div v-if="resultados.servidores && resultados.servidores.length > 0" class="glass-panel" style="padding: 1.25rem;">
          <div class="metric-card" style="margin-bottom: 1rem;">
            <span class="metric-label">🖥️ Servidores Afectados</span>
            <span class="metric-value">{{ resultados.servidores.length }}</span>
          </div>
          <div class="table-container">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>Servidor</th>
                  <th>IP</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="srv in resultados.servidores" :key="srv.id">
                  <td>{{ srv.nombre }}</td>
                  <td>{{ srv.ip }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Aplicaciones -->
        <div v-if="resultados.aplicaciones && resultados.aplicaciones.length > 0" class="glass-panel" style="padding: 1.25rem;">
          <div class="metric-card" style="margin-bottom: 1rem;">
            <span class="metric-label">📦 Sistemas / Apps Caídas</span>
            <span class="metric-value">{{ resultados.aplicaciones.length }}</span>
          </div>
          <div class="table-container">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>Aplicación</th>
                  <th>Descripción</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in resultados.aplicaciones" :key="app.id">
                  <td><strong>{{ app.nombre }}</strong></td>
                  <td>{{ app.descripcion }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Procesos -->
        <div v-if="resultados.procesos && resultados.procesos.length > 0" class="glass-panel" style="padding: 1.25rem;">
          <div class="metric-card" style="margin-bottom: 1rem;">
            <span class="metric-label">⚙️ Procesos Planta Detenidos</span>
            <span class="metric-value">{{ resultados.procesos.length }}</span>
          </div>
          <div class="table-container">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>Línea / Proceso</th>
                  <th>Sistema Responsable</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="proc in resultados.procesos" :key="proc.nombre_proceso">
                  <td>{{ proc.nombre_proceso }} ({{ proc.linea_produccion }})</td>
                  <td><span class="badge badge-deposito">{{ proc.app_responsable }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Hosts -->
        <div v-if="resultados.hosts && resultados.hosts.length > 0" class="glass-panel" style="padding: 1.25rem; grid-column: 1 / -1;">
          <div class="metric-card" style="margin-bottom: 1rem;">
            <span class="metric-label">🛰️ Hosts de Planta sin Red (AP, PLC, Cámaras)</span>
            <span class="metric-value">{{ resultados.hosts.length }}</span>
          </div>
          <div class="table-container">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>Dispositivo</th>
                  <th>IP</th>
                  <th>Rol</th>
                  <th>Ubicación</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="h in resultados.hosts" :key="h.nombre">
                  <td>{{ h.nombre }}</td>
                  <td>{{ h.ip }}</td>
                  <td>{{ h.rol }}</td>
                  <td>{{ h.ubicacion }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const API_URL = '' 

export default {
  name: 'ImpactSimulator',
  setup() {
    const tipoCorte = ref('Subestación')
    const targetId = ref('')
    const entidades = ref([])
    const loadingEntidades = ref(false)
    const loadingSimulation = ref(false)
    const simulacionEjecutada = ref(false)
    const resultados = ref({})
    
    const targetNombre = computed(() => {
      const match = entidades.value.find(e => e.id === targetId.value)
      return match ? match.nombre : ''
    })

    const selectedServerInfo = computed(() => {
      if (tipoCorte.value !== 'Servidor') return null
      return entidades.value.find(e => e.id === targetId.value) || null
    })

    const cargarEntidades = async () => {
      loadingEntidades.value = true
      entidades.value = []
      targetId.value = ''
      simulacionEjecutada.value = false
      
      try {
        let endpoint = '/api/subestaciones'
        if (tipoCorte.value === 'Blindobarra') {
          endpoint = '/api/blindobarras'
        } else if (tipoCorte.value === 'UPS') {
          endpoint = '/api/ups'
        } else if (tipoCorte.value === 'Rack') {
          endpoint = '/api/racks'
        } else if (tipoCorte.value === 'Servidor') {
          endpoint = '/api/servidores'
        }
        
        const response = await axios.get(`${API_URL}${endpoint}`)
        entidades.value = response.data
        if (entidades.value.length > 0) {
          targetId.value = entidades.value[0].id
        }
      } catch (error) {
        console.error("Error loading entities for simulation", error)
      } finally {
        loadingEntidades.value = false
      }
    }

    const simularImpacto = async () => {
      if (!targetId.value) return
      loadingSimulation.value = true
      simulacionEjecutada.value = false
      
      try {
        const response = await axios.post(`${API_URL}/api/simulator/impact`, {
          tipo_corte: tipoCorte.value,
          target_id: targetId.value
        })
        resultados.value = response.data.resultados
        simulacionEjecutada.value = true
      } catch (error) {
        console.error("Error running simulation", error)
        alert("Ocurrió un error al ejecutar la simulación.")
      } finally {
        loadingSimulation.value = false
      }
    }

    onMounted(() => {
      cargarEntidades()
    })

    return {
      tipoCorte,
      targetId,
      entidades,
      loadingEntidades,
      loadingSimulation,
      simulacionEjecutada,
      resultados,
      targetNombre,
      selectedServerInfo,
      cargarEntidades,
      simularImpacto
    }
  }
}
</script>

<style scoped>
.server-details-card {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background-color: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--panel-border);
  border-radius: 6px;
}
.pulse-indicator {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--warning);
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}
</style>
