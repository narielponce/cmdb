<template>
  <div class="itam-container">
    <!-- Subnavigation Tabs inside ITAM -->
    <div class="tabs-header">
      <button class="tab-btn" :class="{ active: activeTab === 'inventory' }" @click="activeTab = 'inventory'">
        🔍 Consolidado de Equipos
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'operations' }" @click="activeTab = 'operations'">
        📥 / 📤 Operaciones
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'consumibles' }" @click="activeTab = 'consumibles'">
        🧵 Consumibles
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'history' }" @click="activeTab = 'history'">
        📊 Historial de Movimientos
      </button>
    </div>

    <!-- TAB 1: Consolidado de Equipos -->
    <div v-if="activeTab === 'inventory'">
      <div class="glass-panel">
        <h3 style="margin-bottom: 1rem; font-size: 1.2rem;">🔍 Estado de Equipos Críticos (Switches / UPS / APs / Cámaras)</h3>
        
        <!-- Filters -->
        <div style="display: flex; gap: 2rem; margin-bottom: 1.5rem; flex-wrap: wrap;">
          <div class="form-group" style="margin-bottom: 0; min-width: 250px;">
            <label class="form-label">Filtrar por ubicación física:</label>
            <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
              <label style="display: flex; align-items: center; gap: 0.25rem; cursor: pointer;">
                <input type="radio" v-model="filtroUbicacion" value="todos" />
                <span>Mostrar Todos</span>
              </label>
              <label style="display: flex; align-items: center; gap: 0.25rem; cursor: pointer;">
                <input type="radio" v-model="filtroUbicacion" value="deposito" />
                <span>En Depósito</span>
              </label>
              <label style="display: flex; align-items: center; gap: 0.25rem; cursor: pointer;">
                <input type="radio" v-model="filtroUbicacion" value="produccion" />
                <span>En Producción</span>
              </label>
            </div>
          </div>
          
          <div class="form-group" style="margin-bottom: 0; flex-grow: 1;">
            <label class="form-label">Filtrar por tipo de equipo:</label>
            <div style="display: flex; gap: 1rem; margin-top: 0.5rem; flex-wrap: wrap;">
              <label v-for="tipo in tiposEquipos" :key="tipo" style="display: flex; align-items: center; gap: 0.25rem; cursor: pointer;">
                <input type="checkbox" v-model="filtrosTipos" :value="tipo" />
                <span>{{ tipo }}</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Inventory List -->
        <div class="table-container" v-if="filteredInventory.length > 0">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Tipo Equipo</th>
                <th>Nombre</th>
                <th>Marca</th>
                <th>Modelo</th>
                <th>Nro Serie</th>
                <th>IP</th>
                <th>Ubicación / Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in paginatedInventory" :key="item.serial + item.nombre">
                <td>{{ item.tipo_equipo }}</td>
                <td><strong>{{ item.nombre }}</strong></td>
                <td>{{ item.marca }}</td>
                <td>{{ item.modelo }}</td>
                <td>{{ item.serial }}</td>
                <td>{{ item.ip || '-' }}</td>
                <td>
                  <span class="badge" :class="item.ubicacion_estado === '🟢 En Producción' ? 'badge-produccion' : 'badge-deposito'">
                    {{ item.ubicacion_estado }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Controles de Paginación -->
        <div v-if="filteredInventory.length > 0" class="flex flex-col sm:flex-row justify-between items-center gap-4 mt-4 bg-slate-50 p-4 rounded-xl border border-slate-200 shadow-sm">
          <div class="text-sm text-slate-600 font-medium">
            Mostrando {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, filteredInventory.length) }} de {{ filteredInventory.length }} registros
          </div>
          <div class="flex items-center gap-1">
            <button 
              @click="currentPage > 1 && (currentPage--)" 
              :disabled="currentPage === 1"
              class="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:pointer-events-none transition text-sm font-medium shadow-sm"
            >
              ◀ Anterior
            </button>
            
            <button 
              v-for="p in visiblePages" 
              :key="p"
              @click="currentPage = p"
              :class="['px-3 py-1.5 rounded-lg text-sm font-semibold transition shadow-sm', p === currentPage ? 'bg-primary text-white' : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50']"
            >
              {{ p }}
            </button>

            <button 
              @click="currentPage < totalPages && (currentPage++)" 
              :disabled="currentPage === totalPages"
              class="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:pointer-events-none transition text-sm font-medium shadow-sm"
            >
              Siguiente ▶
            </button>
          </div>
          <div class="flex items-center gap-2 text-sm text-slate-600 font-medium">
            Filas por página:
            <select v-model="pageSize" class="rounded-lg border border-slate-200 bg-white px-2 py-1.5 text-slate-700 font-semibold shadow-sm focus:outline-none focus:ring-2 focus:ring-primary/20">
              <option :value="5">5</option>
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
            </select>
          </div>
        </div>
        <div v-else-if="loadingInventory" style="text-align: center; padding: 2rem; color: var(--text-muted);">
          Cargando inventario consolidado...
        </div>
        <div v-else style="text-align: center; padding: 2rem; color: var(--warning);">
          No se encontraron equipos con los filtros seleccionados.
        </div>
      </div>
    </div>

    <!-- TAB 2: Operaciones (Ingreso / Despliegue / Consumibles) -->
    <div v-if="activeTab === 'operations'">
      <div v-if="!canWrite" class="glass-panel" style="text-align: center; padding: 4rem;">
        <span style="font-size: 3rem;">🔒</span>
        <h3 style="margin-top: 1rem; color: var(--text-main);">Acceso Restringido</h3>
        <p style="color: var(--text-muted); max-width: 500px; margin: 0.5rem auto 0 auto;">
          Tu rol actual no posee permisos de escritura para realizar ingresos o egresos de equipamiento en depósito.
          Contacta al administrador para solicitar acceso.
        </p>
      </div>
      <div v-else class="grid-cols-2">
      <!-- Ingreso a Depósito -->
      <div class="glass-panel">
        <h3 style="margin-bottom: 1rem; font-size: 1.15rem; color: var(--brand-accent);">📥 Registrar Ingreso al Depósito</h3>
        <form @submit.prevent="registrarIngreso" enctype="multipart/form-data">
          <div class="form-group">
            <label class="form-label" for="ingreso-tipo">Tipo de Activo:</label>
            <select id="ingreso-tipo" class="form-select" v-model="ingresoForm.tipo_activo">
              <option value="🔌 Switch">🔌 Switch</option>
              <option value="🌐 Access Point (AP)">🌐 Access Point (AP)</option>
              <option value="🔋 UPS">🔋 UPS</option>
              <option value="🖥️ Host/Otro">🖥️ Host/Otro</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label" for="ingreso-nombre">Nombre Identificador (Hostname):</label>
            <input id="ingreso-nombre" type="text" class="form-input" v-model="ingresoForm.nombre" placeholder="Ej: SW-CO-09" required />
          </div>
          <div class="form-group">
            <label class="form-label" for="ingreso-marca">Marca:</label>
            <input id="ingreso-marca" type="text" class="form-input" v-model="ingresoForm.marca" placeholder="Ej: Cisco" />
          </div>
          <div class="form-group">
            <label class="form-label" for="ingreso-modelo">Modelo:</label>
            <input id="ingreso-modelo" type="text" class="form-input" v-model="ingresoForm.modelo" placeholder="Ej: Catalyst 9300" />
          </div>
          <div class="form-group">
            <label class="form-label" for="ingreso-serial">Número de Serie (Único):</label>
            <input id="ingreso-serial" type="text" class="form-input" v-model="ingresoForm.serial" placeholder="Ej: SN12345" required />
          </div>
          <div class="form-group">
            <label class="form-label">Adjuntar remito escaneado (PDF/Imagen):</label>
            <input type="file" @change="onFileChange" accept="application/pdf,image/*" style="margin-top: 0.5rem;" />
          </div>

          <button type="submit" class="btn btn-primary" :disabled="submittingIngreso">
            <span v-if="submittingIngreso">Registrando...</span>
            <span v-else>Ingresar a Depósito</span>
          </button>
        </form>
      </div>

      <!-- Salida/Despliegue a Planta y Consumibles -->
      <div style="display: flex; flex-direction: column; gap: 1.5rem;">
        <!-- Desplegar Equipo a Planta -->
        <div class="glass-panel">
          <h3 style="margin-bottom: 1rem; font-size: 1.15rem; color: var(--brand-accent);">📤 Desplegar Equipo a Planta (Salida)</h3>
          
          <div v-if="equiposDeposito.length === 0" style="padding: 1rem 0; color: var(--text-muted); font-size: 0.9rem;">
            No hay equipos en depósito disponibles para salir a planta.
          </div>
          <form v-else @submit.prevent="desplegarEquipo">
            <div class="form-group">
              <label class="form-label" for="salida-equipo">Seleccione el Equipo a Retirar:</label>
              <select id="salida-equipo" class="form-select" v-model="desplegarForm.equipoNombre" @change="onDesplegarEquipoChange">
                <option v-for="eq in equiposDeposito" :key="eq.nombre" :value="eq.nombre">
                  {{ eq.tipo_equipo }} | {{ eq.nombre }} (S/N: {{ eq.serial || 'S/N' }})
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label class="form-label" for="salida-destino">Destino en Planta:</label>
              <select id="salida-destino" class="form-select" v-model="desplegarForm.destino_id">
                <option v-for="dest in destinosFiltrados" :key="dest.id" :value="dest.id">
                  {{ dest.nombre }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label" for="salida-operador">Operador que entrega (Tu usuario):</label>
              <input id="salida-operador" type="text" class="form-input" v-model="desplegarForm.operador" required />
            </div>

            <div class="form-group">
              <label class="form-label" for="salida-responsable">Responsable que retira (Nombre completo):</label>
              <input id="salida-responsable" type="text" class="form-input" v-model="desplegarForm.responsable" required />
            </div>

            <button type="submit" class="btn btn-primary" :disabled="submittingDespliegue">
              <span v-if="submittingDespliegue">Procesando...</span>
              <span v-else>Autorizar Salida y Generar Acta</span>
            </button>
          </form>
        </div>

        <!-- Salida de Insumos -->
        <div class="glass-panel">
          <h3 style="margin-bottom: 1rem; font-size: 1.15rem; color: var(--brand-accent);">📤 Registrar Salida de Insumos</h3>
          
          <div v-if="consumiblesDisponibles.length === 0" style="padding: 1rem 0; color: var(--text-muted); font-size: 0.9rem;">
            No hay consumibles con stock disponible en depósito.
          </div>
          <form v-else @submit.prevent="retirarConsumible">
            <div class="form-group">
              <label class="form-label" for="insumo-select">Seleccione el Insumo a Retirar:</label>
              <select id="insumo-select" class="form-select" v-model="insumosForm.consumible_id" @change="onInsumoChange">
                <option v-for="c in consumiblesDisponibles" :key="c.id" :value="c.id">
                  {{ c.marca }} {{ c.modelo }} ({{ c.ubicacion }} - [Disponible: {{ c.cantidad }}])
                </option>
              </select>
            </div>

            <div class="form-group" v-if="insumosForm.consumible_id">
              <label class="form-label" for="insumo-cantidad">Cantidad a Entregar (Máx: {{ selectedInsumoStock }}):</label>
              <input id="insumo-cantidad" type="number" class="form-input" v-model.number="insumosForm.cantidad" min="1" :max="selectedInsumoStock" required />
            </div>

            <div class="form-group">
              <label class="form-label" for="insumo-operador">Operador de IT (Tu usuario):</label>
              <input id="insumo-operador" type="text" class="form-input" v-model="insumosForm.operador" required />
            </div>

            <div class="form-group">
              <label class="form-label" for="insumo-responsable">Responsable que recibe (Nombre completo):</label>
              <input id="insumo-responsable" type="text" class="form-input" v-model="insumosForm.responsable" required />
            </div>

            <button type="submit" class="btn btn-primary" :disabled="submittingInsumo">
              <span v-if="submittingInsumo">Procesando...</span>
              <span v-else>Autorizar Salida de Insumos</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>

    <!-- TAB 3: Stock y gestión de Consumibles -->
    <div v-if="activeTab === 'consumibles'">
      <div class="glass-panel">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
          <h3 style="font-size: 1.2rem;">📊 Catálogo e Insumos por Cantidad</h3>
          <button v-if="canWrite" class="btn btn-secondary" style="max-width: 150px; padding: 0.5rem;" @click="agregarFilaConsumible">
            ➕ Agregar Insumo
          </button>
        </div>

        <!-- Filtros y Búsqueda de Consumibles -->
        <div style="display: flex; gap: 1.5rem; margin-bottom: 1.5rem; flex-wrap: wrap; align-items: flex-end;">
          <div class="form-group" style="margin-bottom: 0; min-width: 280px; flex-grow: 1;">
            <label class="form-label" for="search-consumible">Buscar insumo (Marca o Modelo):</label>
            <input 
              id="search-consumible" 
              type="text" 
              class="form-input" 
              v-model="searchConsumibles" 
              placeholder="Ej: Cisco, Fiber, Patchcord..." 
              style="margin-top: 0.25rem;"
            />
          </div>
          <div class="form-group" style="margin-bottom: 0; min-width: 200px;">
            <label class="form-label" for="category-consumible">Filtrar por Categoría:</label>
            <select 
              id="category-consumible" 
              class="form-select" 
              v-model="categoryFilterConsumibles"
              style="margin-top: 0.25rem;"
            >
              <option value="todos">Todas las categorías</option>
              <option value="Patchcord CO">Patchcord CO</option>
              <option value="Patchcord FO">Patchcord FO</option>
              <option value="TransceptorSFP">TransceptorSFP</option>
              <option value="Conector">Conector</option>
              <option value="Herramienta">Herramienta</option>
              <option value="Otro">Otro</option>
            </select>
          </div>
        </div>

        <div class="table-container" v-if="filteredConsumibles.length > 0">
          <table class="custom-table" :class="{ 'readonly-mode': !canWrite }">
            <thead>
              <tr>
                <th>Marca</th>
                <th>Modelo / Medida</th>
                <th>Categoría</th>
                <th>Cant.</th>
                <th>Ubicación</th>
                <th>St. Mín.</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in paginatedConsumibles" :key="item.id || index">
                <td>
                  <input type="text" class="editable-cell" v-model="item.marca" @change="item.editado = true" />
                </td>
                <td>
                  <input type="text" class="editable-cell" v-model="item.modelo" @change="item.editado = true" />
                </td>
                <td>
                  <select class="editable-cell" v-model="item.tipo" @change="item.editado = true">
                    <option value="Patchcord CO">Patchcord CO</option>
                    <option value="Patchcord FO">Patchcord FO</option>
                    <option value="TransceptorSFP">TransceptorSFP</option>
                    <option value="Conector">Conector</option>
                    <option value="Herramienta">Herramienta</option>
                    <option value="Otro">Otro</option>
                  </select>
                </td>
                <td>
                  <input type="number" class="editable-cell" v-model.number="item.cantidad" @change="item.editado = true" />
                </td>
                <td>
                  <select class="editable-cell" v-model="item.ubicacion" @change="item.editado = true">
                    <option value="Dep. ITP">Dep. ITP</option>
                    <option value="Dep. Network">Dep. Network</option>
                    <option value="Depósito Principal">Depósito Principal</option>
                  </select>
                </td>
                <td>
                  <input type="number" class="editable-cell" v-model.number="item.stock_minimo" @change="item.editado = true" />
                </td>
                <td>
                  <div class="crud-actions" v-if="canWrite">
                    <button class="crud-btn" title="Guardar Fila" @click="guardarFilaConsumible(item)">
                      💾
                    </button>
                    <button class="crud-btn" title="Eliminar Fila" @click="eliminarFilaConsumible(item)">
                      🗑️
                    </button>
                  </div>
                  <span v-else style="font-size: 0.9rem; color: var(--text-muted);" title="Solo Lectura">🔒</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else-if="loadingConsumibles" style="text-align: center; padding: 2rem; color: var(--text-muted);">
          Cargando consumibles...
        </div>
        <div v-else style="text-align: center; padding: 2rem; color: var(--warning);">
          No se encontraron consumibles con los filtros seleccionados.
        </div>

        <!-- Controles de Paginación para Consumibles -->
        <div v-if="filteredConsumibles.length > 0" class="flex flex-col sm:flex-row justify-between items-center gap-4 mt-4 bg-slate-50 p-4 rounded-xl border border-slate-200 shadow-sm">
          <div class="text-sm text-slate-600 font-medium">
            Mostrando {{ (currentConsumiblesPage - 1) * consumiblesPageSize + 1 }} - {{ Math.min(currentConsumiblesPage * consumiblesPageSize, filteredConsumibles.length) }} de {{ filteredConsumibles.length }} registros
          </div>
          <div class="flex items-center gap-1">
            <button 
              @click="currentConsumiblesPage > 1 && (currentConsumiblesPage--)" 
              :disabled="currentConsumiblesPage === 1"
              class="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:pointer-events-none transition text-sm font-medium shadow-sm"
            >
              ◀ Anterior
            </button>
            
            <button 
              v-for="p in visibleConsumiblesPages" 
              :key="p"
              @click="currentConsumiblesPage = p"
              :class="['px-3 py-1.5 rounded-lg text-sm font-semibold transition shadow-sm', p === currentConsumiblesPage ? 'bg-primary text-white' : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50']"
            >
              {{ p }}
            </button>

            <button 
              @click="currentConsumiblesPage < totalConsumiblesPages && (currentConsumiblesPage++)" 
              :disabled="currentConsumiblesPage === totalConsumiblesPages"
              class="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:pointer-events-none transition text-sm font-medium shadow-sm"
            >
              Siguiente ▶
            </button>
          </div>
          <div class="flex items-center gap-2 text-sm text-slate-600 font-medium">
            Filas por página:
            <select v-model="consumiblesPageSize" class="rounded-lg border border-slate-200 bg-white px-2 py-1.5 text-slate-700 font-semibold shadow-sm focus:outline-none focus:ring-2 focus:ring-primary/20">
              <option :value="5">5</option>
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 4: Historial de Movimientos -->
    <div v-if="activeTab === 'history'">
      <div class="glass-panel">
        <h3 style="margin-bottom: 1rem; font-size: 1.2rem;">📊 Registro de Auditoría y Movimientos</h3>
        
        <div class="table-container" v-if="historial.length > 0">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Operador</th>
                <th>Movimiento</th>
                <th>Detalle / Acta</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in historial" :key="log.id">
                <td style="white-space: nowrap;">{{ formatearFecha(log.fecha) }}</td>
                <td>{{ log.operador }}</td>
                <td>
                  <span class="badge" :class="log.tipo_movimiento.includes('Ingreso') ? 'badge-produccion' : 'badge-deposito'">
                    {{ log.tipo_movimiento }}
                  </span>
                </td>
                <td>
                  <span v-html="renderizarDetalle(log.detalle)"></span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else-if="loadingHistorial" style="text-align: center; padding: 2rem; color: var(--text-muted);">
          Cargando auditoría...
        </div>
        <div v-else style="text-align: center; padding: 2rem; color: var(--warning);">
          No se registran movimientos en el historial.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

export default {
  name: 'ITAMPanel',
  setup() {
    const activeTab = ref('inventory')
    const canWrite = ref(false)

    const loadUserPermissions = () => {
      const savedUser = localStorage.getItem('net_cmdb_user')
      if (savedUser) {
        const user = JSON.parse(savedUser)
        canWrite.value = user.is_superadmin || user.modules?.some(m => m.module_name === 'itam' && m.can_write)
      }
    }
    
    // Inventory List State
    const inventory = ref([])
    const loadingInventory = ref(false)
    const filtroUbicacion = ref('todos')
    const filtrosTipos = ref(["🔌 Switch", "🔋 UPS", "📶 Access Point", "📷 Cámara IP"])

    // Pagination State
    const currentPage = ref(1)
    const pageSize = ref(10)

    const totalPages = computed(() => Math.ceil(filteredInventory.value.length / pageSize.value) || 1)

    const paginatedInventory = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredInventory.value.slice(start, end)
    })

    const visiblePages = computed(() => {
      const pages = []
      const maxVisible = 5
      let start = Math.max(1, currentPage.value - 2)
      let end = Math.min(totalPages.value, start + maxVisible - 1)
      if (end - start + 1 < maxVisible) {
        start = Math.max(1, end - maxVisible + 1)
      }
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    watch([filtroUbicacion, filtrosTipos], () => {
      currentPage.value = 1
    }, { deep: true })

    watch(activeTab, () => {
      currentPage.value = 1
      currentConsumiblesPage.value = 1
    })
    const tiposEquipos = ["🔌 Switch", "🔋 UPS", "📶 Access Point", "📷 Cámara IP", "⚙️ Host Industrial"]

    // Consumibles State
    const stockConsumibles = ref([])
    const loadingConsumibles = ref(false)
    const searchConsumibles = ref('')
    const categoryFilterConsumibles = ref('todos')
    const currentConsumiblesPage = ref(1)
    const consumiblesPageSize = ref(10)

    watch([searchConsumibles, categoryFilterConsumibles], () => {
      currentConsumiblesPage.value = 1
    })

    // History State
    const historial = ref([])
    const loadingHistorial = ref(false)

    // Deploy Destinations
    const racks = ref([])
    const switches = ref([])

    // Forms State
    const ingresoForm = ref({
      tipo_activo: '🔌 Switch',
      nombre: '',
      marca: '',
      modelo: '',
      serial: '',
      archivo_remito: null
    })
    const submittingIngreso = ref(false)

    const desplegarForm = ref({
      equipoNombre: '',
      destino_id: '',
      operador: 'Operador IT',
      responsable: ''
    })
    const submittingDespliegue = ref(false)

    const insumosForm = ref({
      consumible_id: '',
      cantidad: 1,
      operador: 'Operador IT',
      responsable: ''
    })
    const submittingInsumo = ref(false)

    // Computed Fields
    const filteredInventory = computed(() => {
      let data = inventory.value.filter(item => filtrosTipos.value.includes(item.tipo_equipo))
      
      if (filtroUbicacion.value === 'deposito') {
        return data.filter(item => item.ubicacion_estado === '📦 En Depósito')
      } else if (filtroUbicacion.value === 'produccion') {
        return data.filter(item => item.ubicacion_estado === '🟢 En Producción')
      }
      return data
    })

    const equiposDeposito = computed(() => {
      return inventory.value.filter(item => item.ubicacion_estado === '📦 En Depósito')
    })

    const selectedDesplegarEquipo = computed(() => {
      return equiposDeposito.value.find(item => item.nombre === desplegarForm.value.equipoNombre) || null
    })

    const destinosFiltrados = computed(() => {
      if (!selectedDesplegarEquipo.value) return []
      if (selectedDesplegarEquipo.value.tipo_equipo === '🔌 Switch') {
        return racks.value
      } else {
        return switches.value
      }
    })

    const filteredConsumibles = computed(() => {
      let data = stockConsumibles.value
      
      // Filter by category
      if (categoryFilterConsumibles.value && categoryFilterConsumibles.value !== 'todos') {
        data = data.filter(item => item.tipo === categoryFilterConsumibles.value)
      }
      
      // Filter by search term
      if (searchConsumibles.value) {
        const query = searchConsumibles.value.toLowerCase().trim()
        data = data.filter(item => {
          const marca = (item.marca || '').toLowerCase()
          const modelo = (item.modelo || '').toLowerCase()
          return marca.includes(query) || modelo.includes(query)
        })
      }
      
      return data
    })

    const totalConsumiblesPages = computed(() => Math.ceil(filteredConsumibles.value.length / consumiblesPageSize.value) || 1)

    const paginatedConsumibles = computed(() => {
      const start = (currentConsumiblesPage.value - 1) * consumiblesPageSize.value
      const end = start + consumiblesPageSize.value
      return filteredConsumibles.value.slice(start, end)
    })

    const visibleConsumiblesPages = computed(() => {
      const pages = []
      const maxVisible = 5
      let start = Math.max(1, currentConsumiblesPage.value - 2)
      let end = Math.min(totalConsumiblesPages.value, start + maxVisible - 1)
      if (end - start + 1 < maxVisible) {
        start = Math.max(1, end - maxVisible + 1)
      }
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    const consumiblesDisponibles = computed(() => {
      return stockConsumibles.value.filter(c => c.cantidad > 0)
    })

    const selectedInsumoStock = computed(() => {
      const match = consumiblesDisponibles.value.find(c => c.id === insumosForm.value.consumible_id)
      return match ? match.cantidad : 0
    })

    // Fetch API Methods
    const fetchInventory = async () => {
      loadingInventory.value = true
      try {
        const response = await axios.get('/api/inventario/consolidado')
        inventory.value = response.data
        if (equiposDeposito.value.length > 0 && !desplegarForm.value.equipoNombre) {
          desplegarForm.value.equipoNombre = equiposDeposito.value[0].nombre
          onDesplegarEquipoChange()
        }
      } catch (error) {
        console.error("Error fetching consolidated inventory", error)
      } finally {
        loadingInventory.value = false
      }
    }

    const fetchConsumibles = async () => {
      loadingConsumibles.value = true
      try {
        const response = await axios.get('/api/consumibles')
        stockConsumibles.value = response.data.map(item => ({ ...item, editado: false }))
        if (consumiblesDisponibles.value.length > 0) {
          insumosForm.value.consumible_id = consumiblesDisponibles.value[0].id
        }
      } catch (error) {
        console.error("Error fetching stock consumibles", error)
      } finally {
        loadingConsumibles.value = false
      }
    }

    const fetchHistorial = async () => {
      loadingHistorial.value = true
      try {
        const response = await axios.get('/api/inventario/movimientos')
        historial.value = response.data
      } catch (error) {
        console.error("Error fetching historical movements", error)
      } finally {
        loadingHistorial.value = false
      }
    }

    const fetchDestinations = async () => {
      try {
        const racksRes = await axios.get('/api/racks')
        racks.value = racksRes.data
        const swsRes = await axios.get('/api/switches')
        switches.value = swsRes.data
      } catch (error) {
        console.error("Error fetching deploy destinations", error)
      }
    }

    // Form Event Handlers
    const onFileChange = (e) => {
      ingresoForm.value.archivo_remito = e.target.files[0]
    }

    const onDesplegarEquipoChange = () => {
      if (destinosFiltrados.value.length > 0) {
        desplegarForm.value.destino_id = destinosFiltrados.value[0].id
      } else {
        desplegarForm.value.destino_id = ''
      }
    }

    const onInsumoChange = () => {
      insumosForm.value.cantidad = 1
    }

    // Actions Submit
    const registrarIngreso = async () => {
      submittingIngreso.value = true
      
      const formData = new FormData()
      formData.append('tipo_activo', ingresoForm.value.tipo_activo)
      formData.append('nombre', ingresoForm.value.nombre)
      formData.append('marca', ingresoForm.value.marca)
      formData.append('modelo', ingresoForm.value.modelo)
      formData.append('serial', ingresoForm.value.serial)
      if (ingresoForm.value.archivo_remito) {
        formData.append('archivo_remito', ingresoForm.value.archivo_remito)
      }
      
      try {
        await axios.post('/api/inventario/ingreso', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        
        alert("✨ Equipo registrado en Depósito con éxito.")
        // Reset form
        ingresoForm.value = {
          tipo_activo: '🔌 Switch',
          nombre: '',
          marca: '',
          modelo: '',
          serial: '',
          archivo_remito: null
        }
        
        await fetchInventory()
        await fetchHistorial()
      } catch (error) {
        console.error("Error registering incoming asset", error)
        alert("Error al registrar el equipo.")
      } finally {
        submittingIngreso.value = false
      }
    }

    const descargarPdf = (data, filename) => {
      const blob = new Blob([data], { type: 'application/pdf' })
      const link = document.createElement('a')
      link.href = window.URL.createObjectURL(blob)
      link.download = filename
      link.click()
    }

    const desplegarEquipo = async () => {
      submittingDespliegue.value = true
      try {
        const response = await axios.post('/api/inventario/desplegar', {
          tipo_equipo: selectedDesplegarEquipo.value.tipo_equipo,
          nombre: desplegarForm.value.equipoNombre,
          destino_id: desplegarForm.value.destino_id,
          operador: desplegarForm.value.operador,
          responsable: desplegarForm.value.responsable
        }, { responseType: 'blob' })
        
        alert("🚀 ¡Despliegue exitoso! Iniciando descarga del Acta de Entrega...")
        descargarPdf(response.data, `acta_entrega_${desplegarForm.value.equipoNombre.replace(/ /g, '_')}.pdf`)
        
        // Reset
        desplegarForm.value.responsable = ''
        desplegarForm.value.equipoNombre = ''
        
        await fetchInventory()
        await fetchHistorial()
      } catch (error) {
        console.error("Error deploying asset", error)
        alert("Error en el despliegue del equipo. Verifique los datos.")
      } finally {
        submittingDespliegue.value = false
      }
    }

    const retirarConsumible = async () => {
      submittingInsumo.value = true
      try {
        const response = await axios.post('/api/inventario/consumibles/salida', {
          consumible_id: insumosForm.value.consumible_id,
          cantidad: insumosForm.value.cantidad,
          operador: insumosForm.value.operador,
          responsable: insumosForm.value.responsable
        }, { responseType: 'blob' })
        
        alert("✨ ¡Salida autorizada! Descargando remito de materiales...")
        descargarPdf(response.data, `remito_consumible_${insumosForm.value.consumible_id}.pdf`)
        
        // Reset
        insumosForm.value.responsable = ''
        insumosForm.value.cantidad = 1
        
        await fetchConsumibles()
        await fetchHistorial()
      } catch (error) {
        console.error("Error withdrawing consumable", error)
        alert("Error al retirar el insumo.")
      } finally {
        submittingInsumo.value = false
      }
    }

    // Tab 3 Consumible Flat grid edit methods
    const agregarFilaConsumible = () => {
      // Reset filters so the new row is visible
      searchConsumibles.value = ''
      categoryFilterConsumibles.value = 'todos'
      currentConsumiblesPage.value = 1

      stockConsumibles.value.unshift({
        id: null,
        marca: '',
        modelo: '',
        tipo: 'Patchcord CO',
        cantidad: 1,
        ubicacion: 'Dep. ITP',
        stock_minimo: 5,
        editado: true
      })
    }

    const guardarFilaConsumible = async (item) => {
      try {
        if (item.id) {
          // Edit
          await axios.put(`/api/consumibles/${item.id}`, item)
        } else {
          // Insert
          await axios.post('/api/consumibles', item)
        }
        alert("Insumo guardado correctamente.")
        await fetchConsumibles()
      } catch (error) {
        console.error("Error saving consumable", error)
        alert("Error al guardar la fila.")
      }
    }

    const eliminarFilaConsumible = async (item) => {
      if (!confirm("¿Está seguro de eliminar este insumo?")) return
      
      try {
        if (item.id) {
          await axios.delete(`/api/consumibles/${item.id}`)
        }
        const idx = stockConsumibles.value.findIndex(c => c === item)
        if (idx !== -1) {
          stockConsumibles.value.splice(idx, 1)
        }
        alert("Insumo eliminado.")
      } catch (error) {
        console.error("Error deleting consumable", error)
        alert("Error al eliminar la fila.")
      }
    }

    // Helper formatting methods
    const formatearFecha = (str) => {
      const d = new Date(str)
      return d.toLocaleString()
    }

    const renderizarDetalle = (detail) => {
      if (!detail) return ''
      // Detect [Remito PDF: ...] or [Acta PDF: ...] and convert it to download button
      const pdfRegex = /\[(Remito|Acta) PDF: (.*?)\]/g
      
      return detail.replace(pdfRegex, (match, type, path) => {
        // Serve statically from FastAPI mounted '/static' endpoint
        const basename = path.split('/').pop()
        const url = `/static/${basename}`
        return `<a href="${url}" target="_blank" class="badge badge-produccion" style="text-decoration:none; margin-left: 5px;">📄 Descargar ${type}</a>`
      })
    }

    // Watch tab changes to load relevant data
    watch(activeTab, (newTab) => {
      if (newTab === 'inventory') {
        fetchInventory()
      } else if (newTab === 'operations') {
        fetchInventory()
        fetchConsumibles()
        fetchDestinations()
      } else if (newTab === 'consumibles') {
        fetchConsumibles()
      } else if (newTab === 'history') {
        fetchHistorial()
      }
    })

    onMounted(() => {
      loadUserPermissions()
      fetchInventory()
    })

    return {
      activeTab,
      canWrite,
      inventory,
      loadingInventory,
      filtroUbicacion,
      filtrosTipos,
      tiposEquipos,
      stockConsumibles,
      loadingConsumibles,
      searchConsumibles,
      categoryFilterConsumibles,
      currentConsumiblesPage,
      consumiblesPageSize,
      historial,
      loadingHistorial,
      racks,
      switches,
      ingresoForm,
      submittingIngreso,
      desplegarForm,
      submittingDespliegue,
      insumosForm,
      submittingInsumo,
      filteredInventory,
      paginatedInventory,
      currentPage,
      pageSize,
      totalPages,
      visiblePages,
      filteredConsumibles,
      totalConsumiblesPages,
      paginatedConsumibles,
      visibleConsumiblesPages,
      equiposDeposito,
      destinosFiltrados,
      consumiblesDisponibles,
      selectedInsumoStock,
      onFileChange,
      onDesplegarEquipoChange,
      onInsumoChange,
      registrarIngreso,
      desplegarEquipo,
      retirarConsumible,
      agregarFilaConsumible,
      guardarFilaConsumible,
      eliminarFilaConsumible,
      formatearFecha,
      renderizarDetalle
    }
  }
}
</script>
