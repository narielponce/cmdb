<template>
  <div class="planos-container flex flex-col gap-6">
    <!-- CRUD & Selector Header -->
    <div class="glass-panel">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h3 class="text-xl font-bold text-slate-800">🗺️ Gestión de Planos de Planta</h3>
          <p class="text-sm text-slate-500">Administra los planos y distribuye geográficamente los racks, switches y servidores de tu infraestructura.</p>
        </div>
        <button 
          v-if="canWrite" 
          @click="abrirModalCrear" 
          class="btn btn-primary px-4 py-2 text-sm font-semibold shadow-sm rounded-lg"
          style="max-width: 180px;"
        >
          ➕ Nuevo Plano
        </button>
      </div>

      <!-- Planos List Grid -->
      <div v-if="loadingPlanos" class="text-center py-8 text-slate-500">
        Cargando planos...
      </div>
      <div v-else-if="planos.length === 0" class="text-center py-12 border border-dashed border-slate-200 rounded-xl bg-slate-50/50">
        <span class="text-3xl block mb-2">🗺️</span>
        <p class="text-slate-600 font-semibold mb-1">No hay planos registrados</p>
        <p class="text-xs text-slate-400 max-w-xs mx-auto">Crea un plano de planta y sube su mapa para comenzar a ubicar físicamente tu equipamiento.</p>
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div 
          v-for="p in planos" 
          :key="p.id" 
          :class="['p-4 rounded-xl border transition shadow-sm flex flex-col justify-between cursor-pointer', selectedPlano && selectedPlano.id === p.id ? 'border-primary bg-primary/5 ring-2 ring-primary/20' : 'border-slate-200 bg-white hover:border-slate-300']"
          @click="seleccionarPlano(p)"
        >
          <div>
            <div class="flex justify-between items-start mb-2">
              <h4 class="font-bold text-slate-800 text-base">{{ p.nombre }}</h4>
              <div v-if="canWrite" class="flex gap-1" @click.stop>
                <button @click="abrirModalEditar(p)" class="p-1 hover:bg-slate-100 rounded text-slate-500 hover:text-slate-800 transition" title="Editar">✏️</button>
                <button @click="confirmarEliminarPlano(p)" class="p-1 hover:bg-red-50 rounded text-slate-400 hover:text-red-600 transition" title="Eliminar">🗑️</button>
              </div>
            </div>
            <!-- Thumbnail preview -->
            <div 
              v-if="p.imagen_url" 
              class="w-full h-24 rounded-lg bg-cover bg-center mb-3 border border-slate-100" 
              :style="{ backgroundImage: 'url(' + p.imagen_url + ')' }"
            ></div>
            <div class="text-xs text-slate-400 mb-4 flex flex-col gap-1">
              <span>📐 Tamaño: {{ p.ancho }}x{{ p.alto }}px</span>
              <span>🖼️ Imagen: {{ p.imagen_url ? 'Cargada' : 'Sin Imagen' }}</span>
            </div>
          </div>
          
          <div class="mt-2 border-t border-slate-100 pt-3 flex justify-between items-center">
            <span class="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Ver y Ubicar Activos</span>
            <span class="text-primary text-sm font-bold">👉</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Drag & Drop Layout (Only visible if a plano is selected) -->
    <div v-if="selectedPlano" class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      
      <!-- Toolbox / Available Items Sidebar -->
      <div class="glass-panel lg:col-span-1 flex flex-col h-[650px]">
        <div class="mb-4">
          <h4 class="font-bold text-slate-800 text-sm mb-1">🛠️ Equipos Disponibles</h4>
          <p class="text-xs text-slate-400">Arrastra los equipos hacia el plano para posicionarlos, o haz doble click para devolverlos aquí.</p>
        </div>

        <input 
          type="text" 
          v-model="searchItemQuery" 
          placeholder="Filtrar equipos..." 
          class="form-control text-xs mb-3"
        />

        <!-- Unplaced list scrollable -->
        <div class="flex-1 overflow-y-auto pr-1 flex flex-col gap-2">
          <div v-if="loadingItems" class="text-center py-4 text-xs text-slate-400">
            Cargando inventario...
          </div>
          <div v-else-if="filteredUnplacedItems.length === 0" class="text-center py-8 border border-dashed border-slate-100 rounded-lg bg-slate-50 text-xs text-slate-400">
            Ningún equipo disponible para ubicar.
          </div>
          <div 
            v-else
            v-for="item in filteredUnplacedItems" 
            :key="item.type + '-' + item.id"
            draggable="true"
            @dragstart="startDrag($event, item)"
            class="flex items-center gap-2.5 p-2 rounded-lg border border-slate-200 bg-white hover:border-primary/50 hover:shadow-sm cursor-grab transition active:cursor-grabbing text-xs"
          >
            <div :class="['w-7 h-7 rounded-full flex items-center justify-center text-sm shadow-sm shrink-0', getTypeColorClass(item.tipo)]">
              {{ getTypeIcon(item.tipo) }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-bold text-slate-800 truncate mb-0.5" :title="item.nombre">{{ item.nombre }}</p>
              <p class="text-[10px] text-slate-400 font-mono truncate">{{ item.ip || 'Sin IP' }} • {{ item.tipo }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Floorplan Canvas Viewport -->
      <div class="glass-panel lg:col-span-3 flex flex-col items-stretch">
        <div class="flex justify-between items-center mb-4">
          <div>
            <h4 class="font-bold text-slate-800 text-base">📍 Distribución Física: {{ selectedPlano.nombre }}</h4>
            <p class="text-xs text-slate-400">Haz clic y arrastra los elementos colocados para ajustar sus coordenadas.</p>
          </div>
          <div class="flex gap-2">
            <button 
              v-if="canWrite"
              @click="guardarDistribucion" 
              :disabled="savingPositions"
              class="btn btn-primary px-4 py-2 text-sm font-semibold rounded-lg shadow-sm flex items-center gap-1.5"
              style="width: auto;"
            >
              <span v-if="savingPositions">💾 Guardando...</span>
              <span v-else>💾 Guardar Distribución</span>
            </button>
          </div>
        </div>

        <!-- Canvas Container -->
        <div 
          class="canvas-wrapper relative border border-slate-200 rounded-xl overflow-auto bg-slate-900 shadow-inner flex items-center justify-center"
          style="min-height: 520px; height: 520px;"
        >
          <!-- Upload image prompt if no image is set -->
          <div v-if="!selectedPlano.imagen_url" class="absolute inset-0 flex flex-col items-center justify-center p-8 bg-slate-950/80 text-white z-10">
            <span class="text-4xl mb-3">🖼️</span>
            <p class="font-bold mb-2">Este plano no tiene una imagen cargada</p>
            <p class="text-xs text-slate-400 max-w-sm text-center mb-4">Sube un plano de planta, mapa de red o blueprint industrial para comenzar a mapear tu equipamiento.</p>
            
            <div v-if="canWrite" class="flex flex-col items-center">
              <input 
                type="file" 
                ref="fileInput" 
                @change="subirImagenPlano" 
                class="hidden" 
                accept="image/*"
              />
              <button 
                @click="$refs.fileInput.click()" 
                class="px-4 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow transition"
              >
                📁 Seleccionar e Importar Imagen
              </button>
              <span v-if="uploadingImage" class="text-xs text-slate-400 mt-2">Subiendo archivo...</span>
            </div>
          </div>

          <!-- Interactive Plan Container -->
          <div 
            v-else
            class="plano-map-canvas relative shadow-lg bg-cover bg-no-repeat bg-center transition-all duration-300"
            :style="{ 
              width: selectedPlano.ancho + 'px', 
              height: selectedPlano.alto + 'px',
              backgroundImage: 'url(' + selectedPlano.imagen_url + ')',
              minWidth: selectedPlano.ancho + 'px',
              minHeight: selectedPlano.alto + 'px'
            }"
            @dragover.prevent
            @drop="onDrop($event)"
          >
            <!-- Connectors SVG Overlay -->
            <svg 
              class="absolute inset-0 pointer-events-none w-full h-full"
              :style="{ 
                width: selectedPlano.ancho + 'px', 
                height: selectedPlano.alto + 'px',
                minWidth: selectedPlano.ancho + 'px',
                minHeight: selectedPlano.alto + 'px'
              }"
            >
              <line 
                v-for="line in connectorLines" 
                :key="line.id"
                :x1="line.x1" 
                :y1="line.y1" 
                :x2="line.x2" 
                :y2="line.y2" 
                stroke="#64748b" 
                stroke-width="2"
                stroke-dasharray="4,4"
                class="connector-line-transition"
              />
            </svg>

            <!-- Placed Items -->
            <div 
              v-for="item in placedItems" 
              :key="item.type + '-' + item.id"
              class="placed-item-badge absolute select-none flex items-center justify-center"
              :style="{ 
                left: (item.x - 20) + 'px', 
                top: (item.y - 20) + 'px',
                width: '40px',
                height: '40px'
              }"
              draggable="true"
              @dragstart="startDrag($event, item)"
              @dblclick="unplaceItem(item)"
              :title="item.nombre + ' (' + item.tipo + ') - Doble click para remover'"
            >
              <!-- Colored Circle pin -->
              <div :class="['w-10 h-10 rounded-full flex items-center justify-center text-lg shadow-lg border-2 border-white ring-4 transition transform hover:scale-110 active:scale-95 cursor-grab', getTypeColorClass(item.tipo), 'ring-slate-900/10']">
                {{ getTypeIcon(item.tipo) }}
              </div>
              
              <!-- Floating label -->
              <span class="absolute top-11 bg-slate-950/80 text-white text-[9px] font-bold px-1.5 py-0.5 rounded shadow whitespace-nowrap pointer-events-none select-none max-w-[100px] truncate">
                {{ item.nombre }}
              </span>
            </div>
          </div>
        </div>

        <div v-if="selectedPlano.imagen_url && canWrite" class="mt-4 flex justify-between items-center text-xs text-slate-500">
          <span>💡 <strong>Doble click</strong> sobre un equipo posicionado para devolverlo a la lista de disponibles.</span>
          <div class="flex items-center gap-2">
            <input type="file" ref="fileInputUpdate" @change="subirImagenPlano" class="hidden" accept="image/*" />
            <button @click="$refs.fileInputUpdate.click()" class="text-primary hover:underline font-semibold bg-none border-none p-0 cursor-pointer">
              ⚙️ Cambiar Imagen del Plano
            </button>
            <span v-if="uploadingImage" class="text-slate-400"> (Cargando...)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Form (Create/Edit Plano) -->
    <div v-if="showModal" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content glass-panel" style="max-width: 480px; width: 90%; margin: 4rem auto; position: relative;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; border-bottom: 1px solid var(--panel-border); padding-bottom: 0.8rem;">
          <h3 style="font-size: 1.15rem; margin: 0; color: var(--text-title);">
            {{ modalMode === 'create' ? '🗺️ Nuevo Plano de Planta' : '⚙️ Editar Plano' }}
          </h3>
          <button @click="cerrarModal" style="background: none; border: none; font-size: 1.5rem; color: var(--text-muted); cursor: pointer; line-height: 1;">&times;</button>
        </div>

        <form @submit.prevent="guardarPlano">
          <div class="flex flex-col gap-4 mb-6">
            <div>
              <label class="form-label">Nombre del Plano</label>
              <input type="text" class="form-input" v-model="modalPlano.nombre" required placeholder="Ej: Planta Alta / Rackroom Principal" />
            </div>
            
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="form-label">Ancho de Diseño (px)</label>
                <input type="number" class="form-input" v-model.number="modalPlano.ancho" required min="400" max="3000" />
              </div>
              <div>
                <label class="form-label">Alto de Diseño (px)</label>
                <input type="number" class="form-input" v-model.number="modalPlano.alto" required min="400" max="3000" />
              </div>
            </div>

            <div>
              <label class="form-label text-slate-700 font-semibold mb-1">Imagen del Plano (Mapa)</label>
              <input type="file" @change="onModalFileChange" class="form-input text-xs" accept="image/*" />
              <p class="text-[10px] text-slate-400 mt-1" v-if="modalPlano.imagen_url">
                Imagen actual: {{ modalPlano.imagen_url }}
              </p>
            </div>
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 1rem; border-top: 1px solid var(--panel-border); padding-top: 1rem;">
            <button type="button" class="btn btn-secondary" style="max-width: 120px;" @click="cerrarModal">Cancelar</button>
            <button type="submit" class="btn btn-primary" style="max-width: 150px;">💾 Guardar Plano</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'PlanosPanel',
  setup() {
    const planos = ref([])
    const selectedPlano = ref(null)
    const loadingPlanos = ref(false)
    const canWrite = ref(false)

    // Items for Drag & Drop
    const placedItems = ref([])
    const unplacedItems = ref([])
    const loadingItems = ref(false)
    const savingPositions = ref(false)
    
    // Search
    const searchItemQuery = ref('')

    // Drag tracking
    const draggedItem = ref(null)

    // Modal state
    const showModal = ref(false)
    const modalMode = ref('create') // 'create' or 'edit'
    const modalPlano = ref({
      id: null,
      nombre: '',
      ancho: 800,
      alto: 600
    })

    const uploadingImage = ref(false)

    const loadUserPermissions = () => {
      const savedUser = localStorage.getItem('net_cmdb_user')
      if (savedUser) {
        const user = JSON.parse(savedUser)
        canWrite.value = user.is_superadmin || user.modules?.some(m => m.module_name === 'crud' && m.can_write)
      }
    }

    const fetchPlanos = async () => {
      loadingPlanos.value = true
      try {
        const res = await axios.get('/api/planos')
        planos.value = res.data
        if (planos.value.length > 0 && !selectedPlano.value) {
          seleccionarPlano(planos.value[0])
        }
      } catch (err) {
        console.error("Error loading planos", err)
      } finally {
        loadingPlanos.value = false
      }
    }

    const seleccionarPlano = async (plano) => {
      selectedPlano.value = plano
      await fetchPlanoItems(plano.id)
    }

    const fetchPlanoItems = async (planoId) => {
      loadingItems.value = true
      try {
        const res = await axios.get(`/api/planos/${planoId}/items`)
        
        // Merge positioned items
        placedItems.value = [
          ...res.data.placed_hosts,
          ...res.data.placed_racks
        ]

        // Merge available items
        unplacedItems.value = [
          ...res.data.unplaced_hosts,
          ...res.data.unplaced_racks
        ]
      } catch (err) {
        console.error("Error loading plano items", err)
      } finally {
        loadingItems.value = false
      }
    }

    // Drag & Drop Handlers
    const startDrag = (event, item) => {
      draggedItem.value = item
      event.dataTransfer.effectAllowed = 'move'
    }

    const onDrop = (event) => {
      if (!draggedItem.value) return
      
      const rect = event.currentTarget.getBoundingClientRect()
      const x = Math.round(event.clientX - rect.left)
      const y = Math.round(event.clientY - rect.top)

      const item = draggedItem.value
      
      // Update coordinates
      item.x = x
      item.y = y
      item.plano_id = selectedPlano.value.id

      // Check if it's already in placedItems
      const placedIdx = placedItems.value.findIndex(p => p.id === item.id && p.tipo === item.tipo)
      if (placedIdx === -1) {
        // Move from unplaced to placed
        placedItems.value.push(item)
        
        const unplacedIdx = unplacedItems.value.findIndex(u => u.id === item.id && u.tipo === item.tipo)
        if (unplacedIdx !== -1) {
          unplacedItems.value.splice(unplacedIdx, 1)
        }
      } else {
        // Just update existing placement positions
        placedItems.value[placedIdx].x = x
        placedItems.value[placedIdx].y = y
      }

      draggedItem.value = null
    }

    const unplaceItem = (item) => {
      if (!canWrite.value) return
      
      // Remove from placed
      const idx = placedItems.value.findIndex(p => p.id === item.id && p.tipo === item.tipo)
      if (idx !== -1) {
        placedItems.value.splice(idx, 1)
      }

      // Restore to unplaced
      item.x = null
      item.y = null
      item.plano_id = null
      unplacedItems.value.push(item)
    }

    const guardarDistribucion = async () => {
      if (!selectedPlano.value) return
      savingPositions.value = true
      
      try {
        // Build payload
        const racks = placedItems.value
          .filter(i => i.tipo === 'Rack')
          .map(r => ({ id: r.id, x: r.x, y: r.y }))
          
        const hosts = placedItems.value
          .filter(i => i.tipo !== 'Rack')
          .map(h => ({ id: h.id, x: h.x, y: h.y }))

        // Append unplaced items to unset their coordinates on backend
        const unplacedRacks = unplacedItems.value
          .filter(i => i.tipo === 'Rack')
          .map(r => ({ id: r.id, x: null, y: null }))
          
        const unplacedHosts = unplacedItems.value
          .filter(i => i.tipo !== 'Rack')
          .map(h => ({ id: h.id, x: null, y: null }))

        const payload = {
          racks: [...racks, ...unplacedRacks],
          hosts: [...hosts, ...unplacedHosts]
        }

        await axios.post(`/api/planos/${selectedPlano.value.id}/posicionar`, payload)
        alert("✨ Distribución de equipos guardada con éxito.")
        await fetchPlanoItems(selectedPlano.value.id)
      } catch (err) {
        console.error("Error saving positioning", err)
        alert("Ocurrió un error al guardar las posiciones.")
      } finally {
        savingPositions.value = false
      }
    }

    // Upload Floorplan Image
    const subirImagenPlano = async (event) => {
      const file = event.target.files[0]
      if (!file || !selectedPlano.value) return
      
      const formData = new FormData()
      formData.append('file', file)
      
      uploadingImage.value = true
      try {
        const res = await axios.post(`/api/planos/${selectedPlano.value.id}/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        selectedPlano.value.imagen_url = res.data.imagen_url
        alert("✨ Imagen del plano subida correctamente.")
        await fetchPlanos()
      } catch (err) {
        console.error("Error uploading plano image", err)
        alert("Error al cargar la imagen.")
      } finally {
        uploadingImage.value = false
      }
    }

    // CRUD functions
    const abrirModalCrear = () => {
      modalMode.value = 'create'
      modalPlano.value = { id: null, nombre: '', ancho: 800, alto: 600 }
      showModal.value = true
    }

    const abrirModalEditar = (plano) => {
      modalMode.value = 'edit'
      modalPlano.value = { ...plano }
      showModal.value = true
    }

    const modalFile = ref(null)

    const onModalFileChange = (event) => {
      modalFile.value = event.target.files[0] || null
    }

    const cerrarModal = () => {
      showModal.value = false
      modalFile.value = null
    }

    const guardarPlano = async () => {
      try {
        let savedPlano = null
        if (modalMode.value === 'create') {
          const res = await axios.post('/api/planos', modalPlano.value)
          planos.value.push(res.data)
          seleccionarPlano(res.data)
          savedPlano = res.data
          alert("✨ Plano de planta registrado.")
        } else {
          const res = await axios.put(`/api/planos/${modalPlano.value.id}`, modalPlano.value)
          const idx = planos.value.findIndex(p => p.id === modalPlano.value.id)
          if (idx !== -1) {
            planos.value[idx] = res.data
          }
          if (selectedPlano.value && selectedPlano.value.id === res.data.id) {
            selectedPlano.value = res.data
          }
          savedPlano = res.data
          alert("✨ Plano actualizado.")
        }

        // If a file was chosen in the modal, upload it now
        if (modalFile.value && savedPlano) {
          uploadingImage.value = true
          const formData = new FormData()
          formData.append('file', modalFile.value)
          const uploadRes = await axios.post(`/api/planos/${savedPlano.id}/upload`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          })
          savedPlano.imagen_url = uploadRes.data.imagen_url
          if (selectedPlano.value && selectedPlano.value.id === savedPlano.id) {
            selectedPlano.value.imagen_url = uploadRes.data.imagen_url
          }
          const idx = planos.value.findIndex(p => p.id === savedPlano.id)
          if (idx !== -1) {
            planos.value[idx].imagen_url = uploadRes.data.imagen_url
          }
        }

        showModal.value = false
        modalFile.value = null
        await fetchPlanos()
      } catch (err) {
        console.error("Error saving plano", err)
        alert("Error al registrar el plano.")
      } finally {
        uploadingImage.value = false
      }
    }

    const confirmarEliminarPlano = async (plano) => {
      if (!confirm(`¿Está seguro de eliminar el plano "${plano.nombre}"? Los equipos posicionados serán desvinculados.`)) return
      
      try {
        await axios.delete(`/api/planos/${plano.id}`)
        planos.value = planos.value.filter(p => p.id !== plano.id)
        if (selectedPlano.value && selectedPlano.value.id === plano.id) {
          selectedPlano.value = planos.value[0] || null
          if (selectedPlano.value) {
            await fetchPlanoItems(selectedPlano.value.id)
          }
        }
        alert("✨ Plano eliminado.")
      } catch (err) {
        console.error("Error deleting plano", err)
        alert("Error al eliminar el plano.")
      }
    }

    // Helper functions for item formatting
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
      const items = placedItems.value
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
            lines.push({
              id: `rack-ups-${item.id}-${upsItem.id}`,
              x1: item.x,
              y1: item.y,
              x2: upsItem.x,
              y2: upsItem.y
            })
          }
        }

        // 2. Switch -> Rack
        if (item.tipo === 'Switch' && item.rack_id) {
          const rackItem = findItem('Rack', item.rack_id)
          if (rackItem) {
            lines.push({
              id: `switch-rack-${item.id}-${rackItem.id}`,
              x1: item.x,
              y1: item.y,
              x2: rackItem.x,
              y2: rackItem.y
            })
          }
        }

        // 3. Host/Servidor -> Switch
        if (item.tipo !== 'Switch' && item.tipo !== 'Rack' && item.switch_id) {
          const switchItem = findItem('Switch', item.switch_id)
          if (switchItem) {
            lines.push({
              id: `host-switch-${item.id}-${switchItem.id}`,
              x1: item.x,
              y1: item.y,
              x2: switchItem.x,
              y2: switchItem.y
            })
          }
        }
      })

      return lines
    })

    // Search Filtering
    const filteredUnplacedItems = computed(() => {
      if (!searchItemQuery.value.trim()) return unplacedItems.value
      const q = searchItemQuery.value.toLowerCase().trim()
      return unplacedItems.value.filter(item => 
        item.nombre.toLowerCase().includes(q) || 
        (item.ip && item.ip.toLowerCase().includes(q)) || 
        item.tipo.toLowerCase().includes(q)
      )
    })

    onMounted(() => {
      loadUserPermissions()
      fetchPlanos()
    })

    return {
      planos,
      selectedPlano,
      loadingPlanos,
      canWrite,
      placedItems,
      unplacedItems,
      loadingItems,
      savingPositions,
      searchItemQuery,
      filteredUnplacedItems,
      showModal,
      modalMode,
      modalPlano,
      uploadingImage,
      seleccionarPlano,
      abrirModalCrear,
      abrirModalEditar,
      cerrarModal,
      guardarPlano,
      confirmarEliminarPlano,
      startDrag,
      onDrop,
      unplaceItem,
      guardarDistribucion,
      subirImagenPlano,
      getTypeIcon,
      getTypeColorClass,
      connectorLines,
      onModalFileChange,
      modalFile
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  z-index: 1000;
}
.draggable-item-card {
  user-select: none;
}
.placed-item-badge {
  z-index: 20;
  transition: transform 0.2s ease;
}
.placed-item-badge:hover {
  z-index: 50;
}
.connector-line-transition {
  transition: stroke 0.3s ease, stroke-width 0.3s ease;
  animation: techDash 4s linear infinite;
}
@keyframes techDash {
  to {
    stroke-dashoffset: -20;
  }
}
</style>
