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

      <!-- Plano de Planta Visualizer -->
      <div class="glass-panel" style="margin-top: 1.5rem;">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
          <div>
            <h3 style="font-size: 1.15rem; margin-bottom: 0.25rem; font-weight: bold; color: var(--text-title);">🗺️ Equipos Afectados en Plano de Planta</h3>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin: 0;">Visualiza la distribución física y los equipos caídos (resaltados en rojo pulsante con advertencia).</p>
          </div>
          
          <!-- Plano selector -->
          <div class="flex items-center gap-2">
            <label class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Seleccionar Plano:</label>
            <select v-model="selectedPlanoId" @change="onPlanoChange" class="form-select text-xs" style="width: auto; min-width: 200px; height: 34px;">
              <option :value="null">-- Seleccionar Plano --</option>
              <option v-for="p in planos" :key="p.id" :value="p.id">{{ p.nombre }}</option>
            </select>
          </div>
        </div>

        <div v-if="!selectedPlanoId" class="text-center py-10 bg-slate-50 border border-dashed border-slate-200 rounded-xl text-sm text-slate-500">
          Seleccione un plano de planta para visualizar gráficamente los equipos afectados.
        </div>
        <div v-else-if="loadingPlanoItems" class="text-center py-10 text-sm text-slate-500">
          Cargando mapa y distribución de equipos...
        </div>
        <div v-else class="flex flex-col items-center">
          <!-- Canvas Wrapper -->
          <div 
            class="canvas-wrapper relative border border-slate-200 rounded-xl overflow-auto bg-slate-900 shadow-inner flex items-center justify-center w-full"
            style="min-height: 500px; height: 500px;"
          >
            <div v-if="!currentPlano || !currentPlano.imagen_url" class="text-white text-sm">
              El plano seleccionado no tiene una imagen cargada.
            </div>
            <div 
              v-else
              class="plano-map-canvas relative shadow-lg bg-cover bg-no-repeat bg-center"
              :style="{ 
                width: currentPlano.ancho + 'px', 
                height: currentPlano.alto + 'px',
                backgroundImage: 'url(' + currentPlano.imagen_url + ')',
                minWidth: currentPlano.ancho + 'px',
                minHeight: currentPlano.alto + 'px'
              }"
            >
              <!-- Connectors SVG Overlay -->
              <svg 
                class="absolute inset-0 pointer-events-none w-full h-full"
                :style="{ 
                  width: currentPlano.ancho + 'px', 
                  height: currentPlano.alto + 'px',
                  minWidth: currentPlano.ancho + 'px',
                  minHeight: currentPlano.alto + 'px'
                }"
              >
                <line 
                  v-for="line in connectorLines" 
                  :key="line.id"
                  :x1="line.x1" 
                  :y1="line.y1" 
                  :x2="line.x2" 
                  :y2="line.y2" 
                  :stroke="line.color" 
                  :stroke-width="line.width"
                  :stroke-dasharray="line.dasharray"
                  :class="['connector-line-transition', line.isAffected ? 'connector-line-affected' : '']"
                />
              </svg>
              <!-- Render positioned items -->
              <div 
                v-for="item in planoItems" 
                :key="item.type + '-' + item.id"
                class="absolute select-none flex items-center justify-center"
                :style="{ 
                  left: (item.x - 20) + 'px', 
                  top: (item.y - 20) + 'px',
                  width: '40px',
                  height: '40px'
                }"
              >
                <!-- Badge Pin, flashes red if isItemAffected -->
                <div 
                  :class="[
                    'w-10 h-10 rounded-full flex items-center justify-center text-lg shadow-lg border-2 ring-4 transition transform hover:scale-110 duration-200', 
                    isItemAffected(item) ? 'bg-red-500 text-white border-red-200 ring-red-500/30 affected-pulsing' : getTypeColorClass(item.tipo),
                    isItemAffected(item) ? '' : 'ring-slate-900/10'
                  ]"
                  :title="item.nombre + ' (' + item.tipo + ') - ' + (isItemAffected(item) ? '🔴 AFECTADO (INOPERATIVO)' : '🟢 OPERATIVO')"
                >
                  {{ isItemAffected(item) ? '⚠️' : getTypeIcon(item.tipo) }}
                </div>
                
                <!-- Floating label -->
                <span class="absolute top-11 bg-slate-950/80 text-white text-[9px] font-bold px-1.5 py-0.5 rounded shadow whitespace-nowrap pointer-events-none select-none max-w-[100px] truncate">
                  {{ item.nombre }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="mt-4 flex flex-wrap gap-4 justify-center text-xs text-slate-500">
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-red-500 inline-block affected-pulsing-legend"></span> Equipo Afectado (Sin Alimentación / Caído)</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-amber-500 border border-amber-600 inline-block"></span> 🔋 UPS</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-violet-600 border border-violet-700 inline-block"></span> 🔌 Switch</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-blue-600 border border-blue-700 inline-block"></span> 🗄️ Rack</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-rose-500 border border-rose-600 inline-block"></span> 🖥️ Servidor</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-emerald-600 border border-emerald-700 inline-block"></span> 🛰️ Host</span>
          </div>
        </div>
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

    // Planos integration state
    const planos = ref([])
    const selectedPlanoId = ref(null)
    const planoItems = ref([])
    const loadingPlanoItems = ref(false)

    const currentPlano = computed(() => {
      return planos.value.find(p => p.id === selectedPlanoId.value) || null
    })

    const fetchPlanos = async () => {
      try {
        const res = await axios.get('/api/planos')
        planos.value = res.data
        if (planos.value.length > 0) {
          selectedPlanoId.value = planos.value[0].id
          await fetchPlanoItems(planos.value[0].id)
        }
      } catch (err) {
        console.error("Error loading planos in simulator", err)
      }
    }

    const fetchPlanoItems = async (planoId) => {
      if (!planoId) {
        planoItems.value = []
        return
      }
      loadingPlanoItems.value = true
      try {
        const res = await axios.get(`/api/planos/${planoId}/items`)
        planoItems.value = [
          ...res.data.placed_hosts,
          ...res.data.placed_racks
        ]
      } catch (err) {
        console.error("Error loading plano items in simulator", err)
      } finally {
        loadingPlanoItems.value = false
      }
    }

    const onPlanoChange = async () => {
      await fetchPlanoItems(selectedPlanoId.value)
    }

    const isItemAffected = (item) => {
      if (!resultados.value) return false
      
      if (item.tipo === 'Rack') {
        return resultados.value.racks?.some(r => r.id === item.id)
      } else if (item.tipo === 'UPS') {
        return resultados.value.ups?.some(u => u.id === item.id)
      } else if (item.tipo === 'Switch') {
        return resultados.value.switches?.some(s => s.id === item.id)
      } else if (item.tipo === 'Servidor') {
        return resultados.value.servidores?.some(s => s.id === item.id)
      } else {
        // Generic host
        return resultados.value.hosts?.some(h => h.id === item.id)
      }
    }

    // Helper formatting functions
    const getTypeIcon = (tipo) => {
      switch (tipo) {
        case 'UPS': return '🔋'
        case 'Switch': return '🔌'
        case 'Rack': return '🗄️'
        case 'Servidor': return '🖥️'
        default: return '🛰️'
      }
    }

    const getTypeColorClass = (tipo) => {
      switch (tipo) {
        case 'UPS': return 'bg-amber-500 text-white border-amber-600 shadow-lg shadow-amber-500/20'
        case 'Switch': return 'bg-violet-600 text-white border-violet-700 shadow-lg shadow-violet-500/20'
        case 'Rack': return 'bg-blue-600 text-white border-blue-700 shadow-lg shadow-blue-500/20'
        case 'Servidor': return 'bg-rose-500 text-white border-rose-600 shadow-lg shadow-rose-500/20'
        default: return 'bg-emerald-600 text-white border-emerald-700 shadow-lg shadow-emerald-500/20'
      }
    }

    const connectorLines = computed(() => {
      const lines = []
      const items = planoItems.value
      if (!items || items.length === 0) return lines

      const findItem = (tipo, id) => {
        return items.find(item => {
          if (tipo === 'Rack') {
            return item.tipo === 'Rack' && item.id === id
          } else {
            return item.tipo === tipo && item.id === id
          }
        })
      }

      items.forEach(item => {
        // 1. Rack -> UPS
        if (item.tipo === 'Rack' && item.ups_id) {
          const upsItem = findItem('UPS', item.ups_id)
          if (upsItem) {
            const affected = isItemAffected(item) || isItemAffected(upsItem)
            lines.push({
              id: `rack-ups-${item.id}-${upsItem.id}`,
              x1: item.x,
              y1: item.y,
              x2: upsItem.x,
              y2: upsItem.y,
              color: affected ? '#ef4444' : '#10b981',
              width: affected ? 3 : 2,
              dasharray: affected ? '6,4' : null,
              isAffected: affected
            })
          }
        }

        // 2. Switch -> Rack
        if (item.tipo === 'Switch' && item.rack_id) {
          const rackItem = findItem('Rack', item.rack_id)
          if (rackItem) {
            const affected = isItemAffected(item) || isItemAffected(rackItem)
            lines.push({
              id: `switch-rack-${item.id}-${rackItem.id}`,
              x1: item.x,
              y1: item.y,
              x2: rackItem.x,
              y2: rackItem.y,
              color: affected ? '#ef4444' : '#10b981',
              width: affected ? 3 : 2,
              dasharray: affected ? '6,4' : null,
              isAffected: affected
            })
          }
        }

        // 3. Host/Servidor -> Switch
        if (item.tipo !== 'Switch' && item.tipo !== 'Rack' && item.switch_id) {
          const switchItem = findItem('Switch', item.switch_id)
          if (switchItem) {
            const affected = isItemAffected(item) || isItemAffected(switchItem)
            lines.push({
              id: `host-switch-${item.id}-${switchItem.id}`,
              x1: item.x,
              y1: item.y,
              x2: switchItem.x,
              y2: switchItem.y,
              color: affected ? '#ef4444' : '#10b981',
              width: affected ? 3 : 2,
              dasharray: affected ? '6,4' : null,
              isAffected: affected
            })
          }
        }
      })

      return lines
    })

    onMounted(async () => {
      await cargarEntidades()
      await fetchPlanos()
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
      simularImpacto,
      planos,
      selectedPlanoId,
      planoItems,
      loadingPlanoItems,
      currentPlano,
      onPlanoChange,
      isItemAffected,
      getTypeIcon,
      getTypeColorClass,
      connectorLines
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
.affected-pulsing {
  animation: affectedPulse 1s infinite alternate;
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.8);
}
.affected-pulsing-legend {
  animation: legendPulse 1s infinite alternate;
}
@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}
@keyframes affectedPulse {
  0% { transform: scale(1); border-color: rgba(239, 68, 68, 0.4); }
  100% { transform: scale(1.12); border-color: rgba(239, 68, 68, 1); box-shadow: 0 0 25px rgba(239, 68, 68, 1); }
}
@keyframes legendPulse {
  0% { opacity: 0.5; transform: scale(0.9); }
  100% { opacity: 1; transform: scale(1.1); }
}
.connector-line-transition {
  transition: stroke 0.3s ease, stroke-width 0.3s ease;
}
.connector-line-affected {
  animation: strokeDash 0.8s linear infinite;
}
@keyframes strokeDash {
  to {
    stroke-dashoffset: -20;
  }
}
</style>
