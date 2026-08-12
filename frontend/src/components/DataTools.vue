<template>
  <div class="data-tools-container">
    <!-- Subnavigation Tabs -->
    <div class="tabs-header">
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'export' }" 
        @click="activeTab = 'export'"
      >
        📤 Exportar & Backups
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'import' }" 
        @click="activeTab = 'import'"
      >
        📥 Importar Datos (CSV / XLS)
      </button>
    </div>

    <!-- TAB 1: Exportar y Backups -->
    <div v-if="activeTab === 'export'" class="tab-pane">
      <div class="split-layout">
        <!-- Full System Backup -->
        <div class="glass-panel main-backup-card" style="display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; gap: 1.25rem; padding: 2.5rem 1.5rem;">
          <span style="font-size: 3.5rem;">💾</span>
          <h3 style="font-size: 1.35rem; font-weight: bold; color: var(--brand-accent);">Backup Completo de Base de Datos</h3>
          <p style="font-size: 0.9rem; color: var(--text-muted); max-width: 320px; line-height: 1.4;">
            Descarga un archivo ZIP comprimido que contiene los datos de las 14 tablas del sistema en formato CSV.
          </p>
          <button @click="downloadBackup" class="btn btn-primary" style="width: auto; padding: 0.75rem 2rem; font-weight: bold;">
            ⚡ Descargar Backup (.ZIP)
          </button>
        </div>

        <!-- Individual Tables Export -->
        <div class="glass-panel" style="flex-grow: 1;">
          <h3 style="font-size: 1.15rem; margin-bottom: 1rem; font-weight: bold;">Exportar Tablas Individuales</h3>
          <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1.25rem;">
            Exporta y descarga los datos específicos de cualquier tabla en formato CSV o Excel para su auditoría o edición externa.
          </p>
          <div class="table-container" style="max-height: 480px; overflow-y: auto;">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>Nombre de Tabla</th>
                  <th>Descripción / Tipo</th>
                  <th style="text-align: center; width: 220px;">Formatos de Descarga</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in tables" :key="t.id">
                  <td><strong>{{ t.label }}</strong></td>
                  <td><span class="badge badge-deposito">{{ t.category }}</span></td>
                  <td>
                    <div style="display: flex; gap: 0.5rem; justify-content: center;">
                      <button @click="exportTable(t.id, 'csv')" class="btn btn-secondary text-xs" style="padding: 0.4rem 0.6rem;">
                        📄 CSV
                      </button>
                      <button @click="exportTable(t.id, 'xlsx')" class="btn btn-secondary text-xs" style="padding: 0.4rem 0.6rem;">
                        📈 Excel (XLSX)
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: Importar Datos -->
    <div v-if="activeTab === 'import'" class="tab-pane">
      <div class="split-layout">
        <!-- Import Form -->
        <div class="glass-panel" style="min-width: 320px; max-width: 480px; flex-grow: 1;">
          <h3 style="font-size: 1.15rem; margin-bottom: 1.25rem; font-weight: bold; color: var(--brand-accent);">Configuración de Carga</h3>
          
          <form @submit.prevent="handleImport" class="form-container">
            <div class="form-group">
              <label class="form-label" for="import-table-select">1. Seleccione la Tabla de Destino:</label>
              <select id="import-table-select" class="form-select" v-model="selectedTable" @change="resetImportState">
                <option v-for="t in tables" :key="t.id" :value="t.id">
                  {{ t.label }} ({{ t.category }})
                </option>
              </select>
            </div>

            <!-- Download Sample Template Link -->
            <div v-if="selectedTable" style="margin-top: -0.5rem; margin-bottom: 1.25rem; text-align: right;">
              <a 
                href="#" 
                @click.prevent="downloadTemplate" 
                class="text-xs" 
                style="color: var(--brand-accent); text-decoration: underline; font-weight: bold;"
              >
                📥 Descargar Plantilla Muestra (.CSV)
              </a>
            </div>

            <div class="form-group">
              <label class="form-label">2. Modo de Importación:</label>
              <div style="display: flex; flex-direction: column; gap: 0.75rem; margin-top: 0.5rem;">
                <label style="display: flex; align-items: flex-start; gap: 0.5rem; cursor: pointer;">
                  <input type="radio" v-model="importMode" value="upsert" style="margin-top: 0.2rem;" />
                  <div>
                    <strong style="font-size: 0.85rem; color: var(--text-main);">Upsert (Insertar/Actualizar)</strong>
                    <p style="font-size: 0.75rem; color: var(--text-muted); margin: 0.1rem 0 0 0;">
                      Agrega nuevos registros. Si ya existe un registro con el mismo ID o Nombre, actualiza sus campos.
                    </p>
                  </div>
                </label>
                <label style="display: flex; align-items: flex-start; gap: 0.5rem; cursor: pointer;">
                  <input type="radio" v-model="importMode" value="clean" style="margin-top: 0.2rem;" />
                  <div>
                    <strong style="font-size: 0.85rem; color: var(--warning);">Limpiar e Importar (Reemplazar)</strong>
                    <p style="font-size: 0.75rem; color: var(--text-muted); margin: 0.1rem 0 0 0;">
                      Vacía completamente la tabla de destino antes de iniciar la importación. 
                      <span style="color: var(--warning); font-weight: bold;">(Requiere que no existan restricciones de claves foráneas bloqueándolo)</span>.
                    </p>
                  </div>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">3. Seleccione el Archivo (CSV o XLSX):</label>
              <div 
                class="dropzone-area"
                :class="{ active: dragActive }"
                @dragenter.prevent="dragActive = true"
                @dragover.prevent="dragActive = true"
                @dragleave.prevent="dragActive = false"
                @drop.prevent="handleFileDrop"
                @click="$refs.fileInput.click()"
              >
                <span style="font-size: 1.8rem; margin-bottom: 0.5rem;">📁</span>
                <span v-if="selectedFile" class="text-sm font-semibold text-emerald-400">
                  {{ selectedFile.name }} ({{ formatBytes(selectedFile.size) }})
                </span>
                <span v-else class="text-xs text-slate-400 text-center">
                  Arrastra tu archivo aquí o haz clic para buscar.<br>(Soporta CSV y XLSX)
                </span>
                <input 
                  type="file" 
                  ref="fileInput" 
                  style="display: none;" 
                  accept=".csv,.xlsx" 
                  @change="handleFileSelect"
                />
              </div>
            </div>

            <button 
              type="submit" 
              class="btn btn-primary" 
              :disabled="!selectedFile || importing"
              style="margin-top: 1rem; width: 100%;"
            >
              <span v-if="importing">Procesando Importación...</span>
              <span v-else>🚀 Iniciar Importación</span>
            </button>
          </form>
        </div>

        <!-- Import Results Panel -->
        <div class="glass-panel" style="flex-grow: 1; display: flex; flex-direction: column;">
          <h3 style="font-size: 1.15rem; margin-bottom: 1rem; font-weight: bold;">Resultados y Consola</h3>
          
          <div v-if="importResult" class="results-report" style="display: flex; flex-direction: column; gap: 1.25rem; height: 100%;">
            <!-- Status Card -->
            <div class="alert" :class="importResult.stats.errors.length > 0 ? 'alert-warning' : 'alert-success'">
              <strong>{{ importResult.message }}</strong>
            </div>

            <!-- Stats grid -->
            <div class="grid-cols-2" style="gap: 1rem;">
              <div class="metric-card navy" style="padding: 0.75rem 1rem;">
                <span class="metric-label" style="font-size: 0.75rem;">Insertados Nuevos</span>
                <span class="metric-value" style="font-size: 1.5rem; color: var(--emerald-400);">{{ importResult.stats.inserted }}</span>
              </div>
              <div class="metric-card blue-gradient" style="padding: 0.75rem 1rem;">
                <span class="metric-label" style="font-size: 0.75rem;">Actualizados/Upserted</span>
                <span class="metric-value" style="font-size: 1.5rem; color: var(--brand-accent);">{{ importResult.stats.updated }}</span>
              </div>
            </div>

            <!-- Errors Log -->
            <div style="flex-grow: 1; display: flex; flex-direction: column; gap: 0.5rem;">
              <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Errores Reportados ({{ importResult.stats.errors.length }}):</span>
              <div 
                v-if="importResult.stats.errors.length > 0"
                class="errors-log-container"
              >
                <ul>
                  <li v-for="(err, idx) in importResult.stats.errors" :key="idx">
                    {{ err }}
                  </li>
                </ul>
              </div>
              <div v-else class="empty-errors-box">
                ✔️ Archivo cargado sin ningún error de validación o clave.
              </div>
            </div>
          </div>
          
          <div v-else class="empty-state-import">
            <span style="font-size: 2.5rem; color: var(--text-muted); opacity: 0.4;">🔄</span>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.75rem; text-align: center; max-width: 300px;">
              Configure y ejecute la carga de un archivo para visualizar las métricas y logs de importación en esta consola.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'

export default {
  name: 'DataTools',
  setup() {
    const activeTab = ref('export')
    const selectedTable = ref('hosts')
    const importMode = ref('upsert')
    const selectedFile = ref(null)
    const dragActive = ref(false)
    const importing = ref(false)
    const importResult = ref(null)

    const tables = [
      { id: "subestaciones", label: "Subestaciones", category: "Infraestructura Física" },
      { id: "blindobarras", label: "Blindobarras", category: "Infraestructura Física" },
      { id: "racks", label: "Racks", category: "Infraestructura Física" },
      { id: "hosts", label: "Hosts / UPS / Switches / Servidores", category: "Activos Lógicos" },
      { id: "aplicaciones", label: "Aplicaciones", category: "Sistemas & Software" },
      { id: "dependencias_app_servidor", label: "Dependencias App-Srv", category: "Relaciones Lógicas" },
      { id: "procesos_planta", label: "Procesos de Planta", category: "Sistemas & Software" },
      { id: "catalogo_equipos", label: "Catálogo de Artículos", category: "ITAM & Almacén" },
      { id: "stock_consumibles", label: "Stock Consumibles", category: "ITAM & Almacén" },
      { id: "marcas", label: "Marcas", category: "Tablas Auxiliares" },
      { id: "estados", label: "Estados de Activos", category: "Tablas Auxiliares" },
      { id: "tipos_host", label: "Tipos de Host", category: "Tablas Auxiliares" },
      { id: "tipos_servidor", label: "Tipos de Servidores", category: "Tablas Auxiliares" },
      { id: "planos", label: "Planos de Planta", category: "Infraestructura Física" }
    ]

    // Downloads template CSV file
    const downloadTemplate = async () => {
      if (!selectedTable.value) return
      try {
        const response = await axios.get(`/api/data/template/${selectedTable.value}`, { responseType: 'blob' })
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `${selectedTable.value}_plantilla.csv`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } catch (err) {
        console.error("Error downloading template", err)
        alert("No se pudo descargar la plantilla de muestra.")
      }
    }

    // Export single table data
    const exportTable = async (tableId, format) => {
      try {
        const response = await axios.get(`/api/data/export/${tableId}?format=${format}`, { responseType: 'blob' })
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        const ext = format === 'xlsx' ? 'xlsx' : 'csv'
        link.setAttribute('download', `${tableId}_export.${ext}`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } catch (err) {
        console.error("Error exporting table", err)
        alert("Ocurrió un error al exportar la tabla.")
      }
    }

    // Downloads all system tables inside ZIP backup
    const downloadBackup = async () => {
      try {
        const response = await axios.get(`/api/data/export-backup`, { responseType: 'blob' })
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `nettrack_backup_completo.zip`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } catch (err) {
        console.error("Error downloading full backup", err)
        alert("No se pudo generar el archivo de backup.")
      }
    }

    // File selection event handlers
    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        selectedFile.value = file
        importResult.value = null
      }
    }

    const handleFileDrop = (event) => {
      dragActive.value = false
      const file = event.dataTransfer.files[0]
      if (file) {
        const ext = file.name.split('.').pop().toLowerCase()
        if (ext === 'csv' || ext === 'xlsx') {
          selectedFile.value = file
          importResult.value = null
        } else {
          alert("Por favor, sube únicamente archivos con extensión CSV o XLSX.")
        }
      }
    }

    const resetImportState = () => {
      selectedFile.value = null
      importResult.value = null
    }

    // Trigger POST file import endpoint
    const handleImport = async () => {
      if (!selectedFile.value || !selectedTable.value) return
      
      importing.value = true
      importResult.value = null
      
      const formData = new FormData()
      formData.append("table_name", selectedTable.value)
      formData.append("mode", importMode.value)
      formData.append("file", selectedFile.value)

      try {
        const response = await axios.post(`/api/data/import`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        importResult.value = response.data
        alert("Importación de datos finalizada.")
      } catch (err) {
        console.error("Error importing data", err)
        const detail = err.response?.data?.detail || "Ocurrió un error inesperado al procesar el archivo."
        alert(`Error al importar: ${detail}`)
      } finally {
        importing.value = false
      }
    }

    // Formatting utilities
    const formatBytes = (bytes, decimals = 2) => {
      if (!bytes) return '0 Bytes'
      const k = 1024
      const dm = decimals < 0 ? 0 : decimals
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
    }

    return {
      activeTab,
      selectedTable,
      importMode,
      selectedFile,
      dragActive,
      importing,
      importResult,
      tables,
      downloadTemplate,
      exportTable,
      downloadBackup,
      handleFileSelect,
      handleFileDrop,
      resetImportState,
      handleImport,
      formatBytes
    }
  }
}
</script>

<style scoped>
.dropzone-area {
  margin-top: 0.5rem;
  border: 2px dashed rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  background-color: rgba(255, 255, 255, 0.01);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 140px;
}
.dropzone-area:hover, .dropzone-area.active {
  border-color: var(--brand-accent);
  background-color: rgba(99, 102, 241, 0.03);
}

.errors-log-container {
  max-height: 180px;
  overflow-y: auto;
  border: 1px solid rgba(239, 68, 68, 0.2);
  background-color: rgba(239, 68, 68, 0.02);
  border-radius: 8px;
  padding: 0.75rem 1rem;
}
.errors-log-container ul {
  list-style: disc;
  padding-left: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.errors-log-container li {
  font-size: 0.8rem;
  color: #f87171;
  font-family: monospace;
}

.empty-errors-box {
  border: 1px solid rgba(16, 185, 129, 0.25);
  background-color: rgba(16, 185, 129, 0.03);
  color: var(--emerald-400);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  font-size: 0.8rem;
  font-weight: bold;
}

.empty-state-import {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  border: 1px dashed rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  background-color: rgba(255, 255, 255, 0.005);
}
</style>
