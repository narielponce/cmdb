<template>
  <div class="crud-panel-container">
    <!-- Active Grid Panel -->
    <div class="glass-panel">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <h3 style="font-size: 1.25rem;">{{ activeTabLabel }}</h3>
        <button 
          v-if="canWrite && ['ups', 'switches', 'hosts', 'servidores'].includes(activeTab)"
          class="btn btn-primary" 
          style="max-width: 220px; padding: 0.5rem;" 
          @click="abrirModalAlta"
        >
          ✨ Alta de Activo (Host)
        </button>
        <button 
          v-else-if="canWrite"
          class="btn btn-secondary" 
          style="max-width: 150px; padding: 0.5rem;" 
          @click="agregarFila"
        >
          ➕ Nueva Fila
        </button>
      </div>

      <!-- Search and Filter Bar -->
      <div v-if="items.length > 0 && ['subestaciones', 'blindobarras', 'ups', 'racks', 'switches', 'hosts', 'servidores'].includes(activeTab)" class="flex flex-col md:flex-row gap-4 items-center mb-6 p-4 bg-slate-50 border border-slate-200 rounded-xl shadow-sm">
        <!-- Text Search -->
        <div class="w-full md:flex-1 relative">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">🔍</span>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Buscar por nombre, modelo, IP, serie..." 
            class="form-control w-full"
            style="padding-left: 2.25rem;"
          />
          <button 
            v-if="searchQuery" 
            @click="searchQuery = ''" 
            class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 font-bold text-lg font-mono"
            type="button"
            style="background: none; border: none; padding: 0; cursor: pointer; line-height: 1;"
          >
            &times;
          </button>
        </div>

        <!-- Dynamic Filters depending on activeTab -->
        <div class="flex flex-wrap gap-2 w-full md:w-auto items-center">
          <!-- Clear Filters Button -->
          <button 
            v-if="hasActiveFilters" 
            @click="clearFilters" 
            class="px-3 py-2 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 transition text-xs font-semibold shadow-sm cursor-pointer"
            style="width: auto; height: 38px;"
          >
            🧹 Limpiar Filtros
          </button>

          <!-- Subestación Filter for Blindobarras -->
          <select 
            v-if="activeTab === 'blindobarras'" 
            v-model="filters.subestacion_id" 
            class="form-select text-xs py-2 h-[38px] rounded-lg border border-slate-300"
            style="width: auto; min-width: 160px;"
          >
            <option :value="null">Todas las Subestaciones</option>
            <option v-for="se in subestaciones" :key="se.id" :value="se.id">{{ se.nombre }}</option>
          </select>

          <!-- Blindobarra Filter for UPS -->
          <select 
            v-if="activeTab === 'ups'" 
            v-model="filters.blindobarra_id" 
            class="form-select text-xs py-2 h-[38px] rounded-lg border border-slate-300"
            style="width: auto; min-width: 160px;"
          >
            <option :value="null">Todas las Blindobarras</option>
            <option v-for="bb in blindobarras" :key="bb.id" :value="bb.id">{{ bb.nombre }}</option>
          </select>

          <!-- Brand Filter (UPS, Switches, Hosts, Servidores) -->
          <select 
            v-if="['ups', 'switches', 'hosts', 'servidores'].includes(activeTab)" 
            v-model="filters.marca" 
            class="form-select text-xs py-2 h-[38px] rounded-lg border border-slate-300"
            style="width: auto; min-width: 140px;"
          >
            <option value="">Todas las Marcas</option>
            <option v-for="m in marcas" :key="m.id" :value="m.nombre">{{ m.nombre }}</option>
          </select>

          <!-- Battery Status Filter (UPS) -->
          <select 
            v-if="activeTab === 'ups'" 
            v-model="filters.estado_baterias" 
            class="form-select text-xs py-2 h-[38px] rounded-lg border border-slate-300"
            style="width: auto; min-width: 160px;"
          >
            <option value="">Todos los Estados Baterías</option>
            <option value="Ok">Ok</option>
            <option value="Cambio Requerido">Cambio Requerido</option>
            <option value="Crítico">Crítico</option>
            <option value="En Mantenimiento">En Mantenimiento</option>
          </select>

          <!-- UPS Filter for Racks -->
          <select 
            v-if="activeTab === 'racks'" 
            v-model="filters.ups_id" 
            class="form-select text-xs py-2 h-[38px] rounded-lg border border-slate-300"
            style="width: auto; min-width: 160px;"
          >
            <option :value="null">Todos los UPS</option>
            <option v-for="u in ups" :key="u.id" :value="u.id">{{ u.nombre }}</option>
          </select>

          <!-- Rack Filter for Switches -->
          <select 
            v-if="activeTab === 'switches'" 
            v-model="filters.rack_id" 
            class="form-select text-xs py-2 h-[38px] rounded-lg border border-slate-300"
            style="width: auto; min-width: 160px;"
          >
            <option :value="null">Todos los Racks</option>
            <option :value="-1">En Depósito (Ninguno)</option>
            <option v-for="rk in racks" :key="rk.id" :value="rk.id">{{ rk.nombre }}</option>
          </select>

          <!-- Switch Filter (Hosts, Servidores) -->
          <select 
            v-if="['hosts', 'servidores'].includes(activeTab)" 
            v-model="filters.switch_id" 
            class="form-select text-xs py-2 h-[38px] rounded-lg border border-slate-300"
            style="width: auto; min-width: 160px;"
          >
            <option :value="null">Todos los Switches</option>
            <option :value="-1">En Depósito / Ninguno</option>
            <option v-for="sw in switches" :key="sw.id" :value="sw.id">{{ sw.nombre }}</option>
          </select>

          <!-- Rol Filter (Hosts) -->
          <select 
            v-if="activeTab === 'hosts'" 
            v-model="filters.rol" 
            class="form-select text-xs py-2 h-[38px] rounded-lg border border-slate-300"
            style="width: auto; min-width: 140px;"
          >
            <option value="">Todos los Roles</option>
            <option v-for="th in tiposHost" :key="th.id" :value="th.nombre">{{ th.nombre }}</option>
          </select>

          <!-- Server Type Filter (Servidores) -->
          <select 
            v-if="activeTab === 'servidores'" 
            v-model="filters.tipo_servidor" 
            class="form-select text-xs py-2 h-[38px] rounded-lg border border-slate-300"
            style="width: auto; min-width: 140px;"
          >
            <option value="">Todos los Tipos</option>
            <option value="Físico">Físico</option>
            <option value="Virtual (VM)">Virtual (VM)</option>
            <option value="Contenedor">Contenedor</option>
            <option value="Otro">Otro</option>
          </select>

          <!-- OS Filter (Servidores) -->
          <select 
            v-if="activeTab === 'servidores'" 
            v-model="filters.sistema_operativo" 
            class="form-select text-xs py-2 h-[38px] rounded-lg border border-slate-300"
            style="width: auto; min-width: 160px;"
          >
            <option value="">Todos los SO</option>
            <option value="Linux RHEL">Linux RHEL</option>
            <option value="Ubuntu">Ubuntu</option>
            <option value="Windows Server 2019">Windows Server 2019</option>
            <option value="Windows Server 2022">Windows Server 2022</option>
            <option value="Windows Server 2025">Windows Server 2025</option>
            <option value="VMware ESXi">VMware ESXi</option>
            <option value="Otro">Otro</option>
          </select>
        </div>
      </div>

      <div v-if="loading" style="text-align: center; padding: 3rem; color: var(--text-muted);">
        Cargando datos...
      </div>

      <div class="table-container" v-else>
        <!-- Dynamic Table depending on tab -->
        <table class="custom-table" :class="{ 'readonly-mode': !canWrite }">
          <thead>
            <tr v-if="activeTab === 'subestaciones'">
              <th>Nombre Subestación</th>
              <th>Capacidad (KVA)</th>
              <th>Ubicación Física</th>
              <th style="width: 100px;">Acciones</th>
            </tr>
            <tr v-else-if="activeTab === 'blindobarras'">
              <th>Nombre Blindobarra</th>
              <th>Subestación Origen</th>
              <th>Capacidad (Amperios)</th>
              <th style="width: 100px;">Acciones</th>
            </tr>
            <tr v-else-if="activeTab === 'ups'">
              <th>Nombre UPS</th>
              <th>Conectado a</th>
              <th>Marca</th>
              <th>Modelo</th>
              <th>Nro Serie</th>
              <th style="width: 120px;">Acciones</th>
            </tr>
            <tr v-else-if="activeTab === 'racks'">
              <th>Nombre Rack</th>
              <th>UPS Respaldo</th>
              <th style="width: 100px;">Acciones</th>
            </tr>
            <tr v-else-if="activeTab === 'switches'">
              <th>Nombre Switch</th>
              <th>Rack Ubicación</th>
              <th>Marca</th>
              <th>Modelo</th>
              <th>Nro Serie</th>
              <th>IP Gestión</th>
              <th>VLAN</th>
              <th style="width: 100px;">Acciones</th>
            </tr>
            <tr v-else-if="activeTab === 'hosts'">
              <th>Hostname</th>
              <th>Marca</th>
              <th>Modelo</th>
              <th>Conectado a</th>
              <th>Rol</th>
              <th>Ubicación</th>
              <th style="width: 120px;">Acciones</th>
            </tr>
            <tr v-else-if="activeTab === 'servidores'">
              <th>Nombre Servidor</th>
              <th>Switch Conexión</th>
              <th>Marca</th>
              <th>Modelo</th>
              <th>Nro Serie</th>
              <th>IP</th>
              <th>Tipo</th>
              <th>Sistema Operativo</th>
              <th style="width: 100px;">Acciones</th>
            </tr>
            <tr v-else-if="activeTab === 'aplicaciones'">
              <th>Nombre Aplicación</th>
              <th>Descripción / Rol</th>
              <th>Owner de Negocio</th>
              <th style="width: 100px;">Acciones</th>
            </tr>
            <tr v-else-if="activeTab === 'dependencias'">
              <th>Aplicación</th>
              <th>Se aloja en Servidor</th>
              <th>Rol de Servidor</th>
              <th style="width: 100px;">Acciones</th>
            </tr>
            <tr v-else-if="activeTab === 'procesos'">
              <th>Línea / Proceso Productivo</th>
              <th>Línea / Sector</th>
              <th>Controlado por App</th>
              <th style="width: 100px;">Acciones</th>
            </tr>
            <tr v-else-if="activeTab === 'marcas'">
              <th>Nombre de Marca</th>
              <th style="width: 100px;">Acciones</th>
            </tr>
            <tr v-else-if="activeTab === 'estados'">
              <th>Nombre de Estado</th>
              <th style="width: 100px;">Acciones</th>
            </tr>
            <tr v-else-if="activeTab === 'tipos-host'">
              <th>Nombre Tipo Host</th>
              <th style="width: 100px;">Acciones</th>
            </tr>
            <tr v-else-if="activeTab === 'tipos-servidor'">
              <th>Nombre Tipo Servidor</th>
              <th style="width: 100px;">Acciones</th>
            </tr>
          </thead>
          
          <tbody>
            <tr v-if="filteredItems.length === 0">
              <td :colspan="columnCount" style="text-align: center; padding: 3rem; color: var(--text-muted);">
                🔍 No se encontraron registros que coincidan con la búsqueda o los filtros seleccionados.
              </td>
            </tr>
            <tr v-else v-for="(item, idx) in paginatedItems" :key="item.id || idx">
              <!-- SUBESTACIONES -->
              <template v-if="activeTab === 'subestaciones'">
                <td><input type="text" class="editable-cell" v-model="item.nombre" /></td>
                <td><input type="number" class="editable-cell" v-model.number="item.capacidad_kva" /></td>
                <td><input type="text" class="editable-cell" v-model="item.ubicacion" /></td>
              </template>

              <!-- BLINDOBARRAS -->
              <template v-else-if="activeTab === 'blindobarras'">
                <td><input type="text" class="editable-cell" v-model="item.nombre" /></td>
                <td>
                  <select class="editable-cell" v-model="item.subestacion_id">
                    <option v-for="se in subestaciones" :key="se.id" :value="se.id">{{ se.nombre }}</option>
                  </select>
                </td>
                <td><input type="number" class="editable-cell" v-model.number="item.capacidad_amperios" /></td>
              </template>

              <!-- UPS -->
              <template v-else-if="activeTab === 'ups'">
                <td><input type="text" class="editable-cell" v-model="item.nombre" /></td>
                <td>
                  <span class="text-slate-500 font-semibold px-2 text-xs">
                    {{ getBlindobarraNombre(item.blindobarra_id) }}
                  </span>
                </td>
                <td>
                  <select class="editable-cell" v-model="item.marca">
                    <option v-for="m in marcas" :key="m.id" :value="m.nombre">{{ m.nombre }}</option>
                  </select>
                </td>
                <td><input type="text" class="editable-cell" v-model="item.modelo" /></td>
                <td><input type="text" class="editable-cell" v-model="item.serial" /></td>
              </template>

              <!-- RACKS -->
              <template v-else-if="activeTab === 'racks'">
                <td><input type="text" class="editable-cell" v-model="item.nombre" /></td>
                <td>
                  <select class="editable-cell" v-model="item.ups_id">
                    <option v-for="u in ups" :key="u.id" :value="u.id">{{ u.nombre }}</option>
                  </select>
                </td>
              </template>

              <!-- SWITCHES -->
              <template v-else-if="activeTab === 'switches'">
                <td><input type="text" class="editable-cell" v-model="item.nombre" /></td>
                <td>
                  <select class="editable-cell" v-model="item.rack_id">
                    <option :value="null">-- Depósito (Ninguno) --</option>
                    <option v-for="rk in racks" :key="rk.id" :value="rk.id">{{ rk.nombre }}</option>
                  </select>
                </td>
                <td>
                  <select class="editable-cell" v-model="item.marca">
                    <option v-for="m in marcas" :key="m.id" :value="m.nombre">{{ m.nombre }}</option>
                  </select>
                </td>
                <td><input type="text" class="editable-cell" v-model="item.modelo" /></td>
                <td><input type="text" class="editable-cell" v-model="item.serial" /></td>
                <td><input type="text" class="editable-cell" v-model="item.ip" /></td>
                <td><input type="text" class="editable-cell" v-model="item.vlan_gestion" /></td>
              </template>

              <!-- HOSTS -->
              <template v-else-if="activeTab === 'hosts'">
                <td><input type="text" class="editable-cell" v-model="item.nombre" /></td>
                <td>
                  <select class="editable-cell" v-model="item.marca">
                    <option v-for="m in marcas" :key="m.id" :value="m.nombre">{{ m.nombre }}</option>
                  </select>
                </td>
                <td><input type="text" class="editable-cell" v-model="item.modelo" /></td>
                <td>
                  <span class="text-slate-500 font-semibold px-2 text-xs">
                    {{ getSwitchNombre(item.switch_id) }}
                  </span>
                </td>
                <td>
                  <select class="editable-cell" v-model="item.rol">
                    <option v-for="th in tiposHost" :key="th.id" :value="th.nombre">{{ th.nombre }}</option>
                  </select>
                </td>
                <td><input type="text" class="editable-cell" v-model="item.ubicacion" /></td>
              </template>

              <!-- SERVIDORES -->
              <template v-else-if="activeTab === 'servidores'">
                <td><input type="text" class="editable-cell" v-model="item.nombre" /></td>
                <td>
                  <select class="editable-cell" v-model="item.switch_id">
                    <option :value="null">-- Ninguno --</option>
                    <option v-for="sw in switches" :key="sw.id" :value="sw.id">{{ sw.nombre }}</option>
                  </select>
                </td>
                <td>
                  <select class="editable-cell" v-model="item.marca">
                    <option v-for="m in marcas" :key="m.id" :value="m.nombre">{{ m.nombre }}</option>
                  </select>
                </td>
                <td><input type="text" class="editable-cell" v-model="item.modelo" /></td>
                <td><input type="text" class="editable-cell" v-model="item.serial" /></td>
                <td><input type="text" class="editable-cell" v-model="item.ip" /></td>
                <td>
                  <select class="editable-cell" v-model="item.tipo_servidor">
                    <option value="Físico">Físico</option>
                    <option value="Virtual (VM)">Virtual (VM)</option>
                    <option value="Contenedor">Contenedor</option>
                    <option value="Otro">Otro</option>
                  </select>
                </td>
                <td>
                  <select class="editable-cell" v-model="item.sistema_operativo">
                    <option value="Linux RHEL">Linux RHEL</option>
                    <option value="Ubuntu">Ubuntu</option>
                    <option value="Windows Server 2019">Windows Server 2019</option>
                    <option value="Windows Server 2022">Windows Server 2022</option>
                    <option value="Windows Server 2025">Windows Server 2025</option>
                    <option value="VMware ESXi">VMware ESXi</option>
                    <option value="Otro">Otro</option>
                  </select>
                </td>
              </template>

              <!-- APLICACIONES -->
              <template v-else-if="activeTab === 'aplicaciones'">
                <td><input type="text" class="editable-cell" v-model="item.nombre" /></td>
                <td><input type="text" class="editable-cell" v-model="item.descripcion" /></td>
                <td><input type="text" class="editable-cell" v-model="item.owner_negocio" /></td>
              </template>

              <!-- DEPENDENCIAS -->
              <template v-else-if="activeTab === 'dependencias'">
                <td>
                  <select class="editable-cell" v-model="item.app_id">
                    <option v-for="app in aplicaciones" :key="app.id" :value="app.id">{{ app.nombre }}</option>
                  </select>
                </td>
                <td>
                  <select class="editable-cell" v-model="item.servidor_id">
                    <option v-for="srv in servidores" :key="srv.id" :value="srv.id">{{ srv.nombre }}</option>
                  </select>
                </td>
                <td><input type="text" class="editable-cell" v-model="item.rol_servidor" /></td>
              </template>

              <!-- PROCESOS -->
              <template v-else-if="activeTab === 'procesos'">
                <td><input type="text" class="editable-cell" v-model="item.nombre_proceso" /></td>
                <td><input type="text" class="editable-cell" v-model="item.linea_produccion" /></td>
                <td>
                  <select class="editable-cell" v-model="item.aplicacion_id">
                    <option v-for="app in aplicaciones" :key="app.id" :value="app.id">{{ app.nombre }}</option>
                  </select>
                </td>
              </template>

              <!-- MARCAS -->
              <template v-else-if="activeTab === 'marcas'">
                <td><input type="text" class="editable-cell" v-model="item.nombre" /></td>
              </template>

              <!-- ESTADOS -->
              <template v-else-if="activeTab === 'estados'">
                <td><input type="text" class="editable-cell" v-model="item.nombre" /></td>
              </template>

              <!-- TIPOS HOST -->
              <template v-else-if="activeTab === 'tipos-host'">
                <td><input type="text" class="editable-cell" v-model="item.nombre" /></td>
              </template>

              <!-- TIPOS SERVIDOR -->
              <template v-else-if="activeTab === 'tipos-servidor'">
                <td><input type="text" class="editable-cell" v-model="item.nombre" /></td>
              </template>

              <!-- ACTIONS -->
              <td>
                <div class="crud-actions">
                  <button 
                    v-if="activeTab === 'ups' || activeTab === 'hosts'" 
                    class="crud-btn" 
                    title="Detalles / Atributos adicionales" 
                    @click="activeTab === 'ups' ? abrirDetallesUps(item) : abrirDetallesHost(item)"
                    type="button"
                  >
                    🔍
                  </button>
                  <template v-if="canWrite">
                    <button class="crud-btn" title="Guardar" @click="guardarFila(item)">
                      💾
                    </button>
                    <button class="crud-btn" title="Eliminar" @click="eliminarFila(item, idx)">
                      🗑️
                    </button>
                  </template>
                  <span v-else-if="activeTab !== 'ups' && activeTab !== 'hosts'" style="font-size: 0.9rem; color: var(--text-muted);" title="Solo Lectura">🔒</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Controles de Paginación -->
      <div v-if="filteredItems.length > 0" class="flex flex-col sm:flex-row justify-between items-center gap-4 mt-4 bg-slate-50 p-4 rounded-xl border border-slate-200 shadow-sm">
        <div class="text-sm text-slate-600 font-medium">
          Mostrando {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, filteredItems.length) }} de {{ filteredItems.length }} registros
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
    </div>

    <!-- Modal for Host Extra Details -->
    <div v-if="showHostModal && selectedHostItem" class="modal-overlay" @click.self="cerrarDetallesHost">
      <div class="modal-content glass-panel" style="max-width: 500px; width: 90%; margin: 4rem auto; position: relative;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; border-bottom: 1px solid var(--panel-border); padding-bottom: 0.8rem;">
          <h3 style="font-size: 1.25rem; margin: 0; color: var(--text-title);">📋 Detalles Adicionales: {{ selectedHostItem.nombre }}</h3>
          <button @click="cerrarDetallesHost" style="background: none; border: none; font-size: 1.5rem; color: var(--text-muted); cursor: pointer; line-height: 1;">&times;</button>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
          <!-- Switch Conexión -->
          <div style="grid-column: span 2;">
            <label class="form-label">Switch Conexión</label>
            <select class="form-select" v-model="selectedHostItem.switch_id" :disabled="!canWrite">
              <option :value="null">-- Depósito (Ninguno) --</option>
              <option v-for="sw in switches" :key="sw.id" :value="sw.id">{{ sw.nombre }}</option>
            </select>
          </div>

          <!-- Nro Serie -->
          <div>
            <label class="form-label">Nro Serie</label>
            <input type="text" class="form-input" v-model="selectedHostItem.serial" :disabled="!canWrite" />
          </div>

          <!-- IP -->
          <div>
            <label class="form-label">IP</label>
            <input type="text" class="form-input" v-model="selectedHostItem.ip" :disabled="!canWrite" />
          </div>

          <!-- Puerto Switch -->
          <div>
            <label class="form-label">Puerto Switch</label>
            <input type="text" class="form-input" v-model="selectedHostItem.puerto_switch" :disabled="!canWrite" />
          </div>

          <!-- Sector Planta -->
          <div>
            <label class="form-label">Sector Planta</label>
            <input type="text" class="form-input" v-model="selectedHostItem.sector_planta" :disabled="!canWrite" />
          </div>
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 1rem; border-top: 1px solid var(--panel-border); padding-top: 1rem;">
          <button type="button" class="btn btn-primary" style="max-width: 120px;" @click="cerrarDetallesHost">Aceptar</button>
        </div>
      </div>
    </div>

    <!-- Modal for UPS Extra Details -->
    <div v-if="showUpsModal && selectedUpsItem" class="modal-overlay" @click.self="cerrarDetallesUps">
      <div class="modal-content glass-panel" style="max-width: 500px; width: 90%; margin: 4rem auto; position: relative;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; border-bottom: 1px solid var(--panel-border); padding-bottom: 0.8rem;">
          <h3 style="font-size: 1.25rem; margin: 0; color: var(--text-title);">📋 Detalles Adicionales: {{ selectedUpsItem.nombre }}</h3>
          <button @click="cerrarDetallesUps" style="background: none; border: none; font-size: 1.5rem; color: var(--text-muted); cursor: pointer; line-height: 1;">&times;</button>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
          <!-- Blindobarra Alimentación -->
          <div style="grid-column: span 2;">
            <label class="form-label">Blindobarra Alimentación</label>
            <select class="form-select" v-model="selectedUpsItem.blindobarra_id" :disabled="!canWrite">
              <option v-for="bb in blindobarras" :key="bb.id" :value="bb.id">{{ bb.nombre }}</option>
            </select>
          </div>

          <!-- Capacidad (KVA) -->
          <div>
            <label class="form-label">Capacidad (KVA)</label>
            <input type="number" step="0.1" class="form-input" v-model.number="selectedUpsItem.capacidad_kva" :disabled="!canWrite" />
          </div>

          <!-- Estado Baterías -->
          <div>
            <label class="form-label">Estado Baterías</label>
            <select class="form-select" v-model="selectedUpsItem.estado_baterias" :disabled="!canWrite">
              <option value="Ok">Ok</option>
              <option value="Cambio Requerido">Cambio Requerido</option>
              <option value="Crítico">Crítico</option>
              <option value="En Mantenimiento">En Mantenimiento</option>
            </select>
          </div>

          <!-- IP Gestión -->
          <div>
            <label class="form-label">IP Gestión</label>
            <input type="text" class="form-input" v-model="selectedUpsItem.ip" :disabled="!canWrite" />
          </div>

          <!-- VLAN -->
          <div>
            <label class="form-label">VLAN</label>
            <input type="text" class="form-input" v-model="selectedUpsItem.vlan" :disabled="!canWrite" />
          </div>
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 1rem; border-top: 1px solid var(--panel-border); padding-top: 1rem;">
          <button type="button" class="btn btn-primary" style="max-width: 120px;" @click="cerrarDetallesUps">Aceptar</button>
        </div>
      </div>
    </div>

    <!-- Modal for Unified Host Creation -->
    <div v-if="showModal" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content glass-panel" style="max-width: 600px; width: 90%; margin: 2rem auto; position: relative;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; border-bottom: 1px solid var(--panel-border); padding-bottom: 0.8rem;">
          <h3 style="font-size: 1.25rem; margin: 0; color: var(--text-title);">✨ Alta de Activo Unificada</h3>
          <button @click="cerrarModal" style="background: none; border: none; font-size: 1.5rem; color: var(--text-muted); cursor: pointer; line-height: 1;">&times;</button>
        </div>

        <form @submit.prevent="guardarModalHost">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
            <!-- Tipo de Activo -->
            <div style="grid-column: span 2;">
              <label class="form-label">Tipo de Activo / Host</label>
              <select class="form-select" v-model="modalHost.tipo_host_nombre" required>
                <option v-for="th in tiposHost" :key="th.id" :value="th.nombre">
                  {{ th.nombre }}
                </option>
              </select>
            </div>

            <!-- Nombre -->
            <div>
              <label class="form-label">Nombre / Hostname</label>
              <input type="text" class="form-input" v-model="modalHost.nombre" required placeholder="Ej: SW-ACCESO-02" />
            </div>

            <!-- IP -->
            <div>
              <label class="form-label">Dirección IP</label>
              <input type="text" class="form-input" v-model="modalHost.ip" placeholder="Ej: 10.20.30.5" />
            </div>

            <!-- Marca -->
            <div>
              <label class="form-label">Marca</label>
              <select class="form-select" v-model="modalHost.marca">
                <option value="">-- Seleccionar Marca --</option>
                <option v-for="m in marcas" :key="m.id" :value="m.nombre">{{ m.nombre }}</option>
              </select>
            </div>

            <!-- Modelo -->
            <div>
              <label class="form-label">Modelo</label>
              <input type="text" class="form-input" v-model="modalHost.modelo" placeholder="Ej: Catalyst 9200" />
            </div>

            <!-- Serial -->
            <div>
              <label class="form-label">Número de Serie</label>
              <input type="text" class="form-input" v-model="modalHost.serial" placeholder="Ej: SN12345" />
            </div>

            <!-- VLAN (Only for Switch or UPS) -->
            <div v-if="['UPS', 'Switch'].includes(modalHost.tipo_host_nombre)">
              <label class="form-label">VLAN de Gestión</label>
              <input type="text" class="form-input" v-model="modalHost.vlan" placeholder="Ej: 10" />
            </div>

            <!-- DYNAMIC FIELDS FOR UPS -->
            <template v-if="modalHost.tipo_host_nombre === 'UPS'">
              <div>
                <label class="form-label">Capacidad (KVA)</label>
                <input type="number" step="0.1" class="form-input" v-model.number="modalHost.capacidad_kva" />
              </div>
              <div>
                <label class="form-label">Blindobarra Origen</label>
                <select class="form-select" v-model="modalHost.blindobarra_id">
                  <option :value="null">-- Ninguna --</option>
                  <option v-for="bb in blindobarras" :key="bb.id" :value="bb.id">{{ bb.nombre }}</option>
                </select>
              </div>
              <div>
                <label class="form-label">Estado Baterías</label>
                <select class="form-select" v-model="modalHost.estado_baterias">
                  <option value="Ok">Ok</option>
                  <option value="Cambio Requerido">Cambio Requerido</option>
                  <option value="Crítico">Crítico</option>
                  <option value="En Mantenimiento">En Mantenimiento</option>
                </select>
              </div>
            </template>

            <!-- DYNAMIC FIELDS FOR SWITCH -->
            <template v-if="modalHost.tipo_host_nombre === 'Switch'">
              <div style="grid-column: span 2;">
                <label class="form-label">Rack Ubicación</label>
                <select class="form-select" v-model="modalHost.rack_id">
                  <option :value="null">-- En Depósito (Ninguno) --</option>
                  <option v-for="rk in racks" :key="rk.id" :value="rk.id">{{ rk.nombre }}</option>
                </select>
              </div>
            </template>

            <!-- DYNAMIC FIELDS FOR SERVIDOR -->
            <template v-if="modalHost.tipo_host_nombre === 'Servidor'">
              <div>
                <label class="form-label">Tipo Servidor</label>
                <select class="form-select" v-model="modalHost.tipo_servidor">
                  <option value="Físico">Físico</option>
                  <option value="Virtual (VM)">Virtual (VM)</option>
                  <option value="Contenedor">Contenedor</option>
                  <option value="Otro">Otro</option>
                </select>
              </div>
              <div>
                <label class="form-label">Sistema Operativo</label>
                <input type="text" class="form-input" v-model="modalHost.sistema_operativo" placeholder="Ej: Linux RHEL" />
              </div>
              <div style="grid-column: span 2;">
                <label class="form-label">Switch Conexión</label>
                <select class="form-select" v-model="modalHost.switch_id">
                  <option :value="null">-- Ninguno --</option>
                  <option v-for="sw in switches" :key="sw.id" :value="sw.id">{{ sw.nombre }}</option>
                </select>
              </div>
            </template>

            <!-- DYNAMIC FIELDS FOR GENERAL HOST (AP, PLC, Cámara, Router, etc) -->
            <template v-if="modalHost.tipo_host_nombre && !['UPS', 'Switch', 'Servidor'].includes(modalHost.tipo_host_nombre)">
              <div>
                <label class="form-label">Switch Conexión</label>
                <select class="form-select" v-model="modalHost.switch_id">
                  <option :value="null">-- En Depósito (Ninguno) --</option>
                  <option v-for="sw in switches" :key="sw.id" :value="sw.id">{{ sw.nombre }}</option>
                </select>
              </div>
              <div>
                <label class="form-label">Puerto Switch</label>
                <input type="text" class="form-input" v-model="modalHost.puerto_switch" placeholder="Ej: Gi1/0/12" />
              </div>
              <div style="grid-column: span 2;">
                <label class="form-label">Ubicación Física</label>
                <input type="text" class="form-input" v-model="modalHost.ubicacion" placeholder="Ej: Línea 2 / Montaje" />
              </div>
            </template>
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 1rem; border-top: 1px solid var(--panel-border); padding-top: 1rem;">
            <button type="button" class="btn btn-secondary" style="max-width: 120px;" @click="cerrarModal">Cancelar</button>
            <button type="submit" class="btn btn-primary" style="max-width: 150px;">💾 Guardar Activo</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

export default {
  name: 'DataCRUD',
  props: {
    activeTabProp: {
      type: String,
      default: 'subestaciones'
    }
  },
  emits: ['update-tab'],
  setup(props, { emit }) {
    const activeTab = ref(props.activeTabProp || 'subestaciones')
    const items = ref([])
    const loading = ref(false)
    const canWrite = ref(false)

    // Pagination State
    const currentPage = ref(1)
    const pageSize = ref(10)

    // Search and Filter State
    const searchQuery = ref('')
    const filters = ref({
      subestacion_id: null,
      blindobarra_id: null,
      marca: '',
      estado_baterias: '',
      ups_id: null,
      rack_id: null,
      switch_id: null,
      rol: '',
      tipo_servidor: '',
      sistema_operativo: ''
    })

    const resetFilters = () => {
      searchQuery.value = ''
      filters.value = {
        subestacion_id: null,
        blindobarra_id: null,
        marca: '',
        estado_baterias: '',
        ups_id: null,
        rack_id: null,
        switch_id: null,
        rol: '',
        tipo_servidor: '',
        sistema_operativo: ''
      }
    }

    const clearFilters = () => {
      resetFilters()
    }

    const hasActiveFilters = computed(() => {
      return searchQuery.value !== '' ||
        filters.value.subestacion_id !== null ||
        filters.value.blindobarra_id !== null ||
        filters.value.marca !== '' ||
        filters.value.estado_baterias !== '' ||
        filters.value.ups_id !== null ||
        filters.value.rack_id !== null ||
        filters.value.switch_id !== null ||
        filters.value.rol !== '' ||
        filters.value.tipo_servidor !== '' ||
        filters.value.sistema_operativo !== ''
    })

    const filteredItems = computed(() => {
      let result = items.value

      // Apply search query
      if (searchQuery.value.trim() !== '') {
        const query = searchQuery.value.toLowerCase().trim()
        result = result.filter(item => {
          const nombreMatch = item.nombre ? item.nombre.toLowerCase().includes(query) : false
          const modeloMatch = item.modelo ? item.modelo.toLowerCase().includes(query) : false
          const serialMatch = item.serial ? item.serial.toLowerCase().includes(query) : false
          const ipMatch = item.ip ? item.ip.toLowerCase().includes(query) : false
          const ubicacionMatch = item.ubicacion ? item.ubicacion.toLowerCase().includes(query) : false
          const vlanMatch = item.vlan ? String(item.vlan).toLowerCase().includes(query) : false
          const vlanGestionMatch = item.vlan_gestion ? String(item.vlan_gestion).toLowerCase().includes(query) : false
          
          const nombreProcesoMatch = item.nombre_proceso ? item.nombre_proceso.toLowerCase().includes(query) : false
          const descripcionMatch = item.descripcion ? item.descripcion.toLowerCase().includes(query) : false
          const ownerMatch = item.owner_negocio ? item.owner_negocio.toLowerCase().includes(query) : false

          return nombreMatch || modeloMatch || serialMatch || ipMatch || ubicacionMatch || vlanMatch || vlanGestionMatch || nombreProcesoMatch || descripcionMatch || ownerMatch
        })
      }

      // Apply dynamic filters depending on activeTab
      if (activeTab.value === 'blindobarras') {
        if (filters.value.subestacion_id !== null) {
          result = result.filter(item => item.subestacion_id === filters.value.subestacion_id)
        }
      } else if (activeTab.value === 'ups') {
        if (filters.value.blindobarra_id !== null) {
          result = result.filter(item => item.blindobarra_id === filters.value.blindobarra_id)
        }
        if (filters.value.marca !== '') {
          result = result.filter(item => item.marca === filters.value.marca)
        }
        if (filters.value.estado_baterias !== '') {
          result = result.filter(item => item.estado_baterias === filters.value.estado_baterias)
        }
      } else if (activeTab.value === 'racks') {
        if (filters.value.ups_id !== null) {
          result = result.filter(item => item.ups_id === filters.value.ups_id)
        }
      } else if (activeTab.value === 'switches') {
        if (filters.value.rack_id !== null) {
          if (filters.value.rack_id === -1) {
            result = result.filter(item => item.rack_id === null)
          } else {
            result = result.filter(item => item.rack_id === filters.value.rack_id)
          }
        }
        if (filters.value.marca !== '') {
          result = result.filter(item => item.marca === filters.value.marca)
        }
      } else if (activeTab.value === 'hosts') {
        if (filters.value.switch_id !== null) {
          if (filters.value.switch_id === -1) {
            result = result.filter(item => item.switch_id === null)
          } else {
            result = result.filter(item => item.switch_id === filters.value.switch_id)
          }
        }
        if (filters.value.marca !== '') {
          result = result.filter(item => item.marca === filters.value.marca)
        }
        if (filters.value.rol !== '') {
          result = result.filter(item => item.rol === filters.value.rol)
        }
      } else if (activeTab.value === 'servidores') {
        if (filters.value.switch_id !== null) {
          if (filters.value.switch_id === -1) {
            result = result.filter(item => item.switch_id === null)
          } else {
            result = result.filter(item => item.switch_id === filters.value.switch_id)
          }
        }
        if (filters.value.marca !== '') {
          result = result.filter(item => item.marca === filters.value.marca)
        }
        if (filters.value.tipo_servidor !== '') {
          result = result.filter(item => item.tipo_servidor === filters.value.tipo_servidor)
        }
        if (filters.value.sistema_operativo !== '') {
          result = result.filter(item => item.sistema_operativo === filters.value.sistema_operativo)
        }
      }

      return result
    })

    const columnCount = computed(() => {
      switch (activeTab.value) {
        case 'subestaciones': return 4
        case 'blindobarras': return 4
        case 'ups': return 6
        case 'racks': return 3
        case 'switches': return 8
        case 'hosts': return 7
        case 'servidores': return 9
        case 'aplicaciones': return 4
        case 'dependencias': return 4
        case 'procesos': return 4
        case 'marcas': return 2
        case 'estados': return 2
        case 'tipos-host': return 2
        case 'tipos-servidor': return 2
        default: return 5
      }
    })

    const totalPages = computed(() => Math.ceil(filteredItems.value.length / pageSize.value) || 1)

    const paginatedItems = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredItems.value.slice(start, end)
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

    const loadUserPermissions = () => {
      const savedUser = localStorage.getItem('net_cmdb_user')
      if (savedUser) {
        const user = JSON.parse(savedUser)
        canWrite.value = user.is_superadmin || user.modules?.some(m => m.module_name === 'crud' && m.can_write)
      }
    }

    // Lookup caches for foreign keys
    const subestaciones = ref([])
    const blindobarras = ref([])
    const ups = ref([])
    const racks = ref([])
    const switches = ref([])
    const servidores = ref([])
    const aplicaciones = ref([])
    const marcas = ref([])
    const estados = ref([])
    const tiposHost = ref([])
    const tiposServidor = ref([])

    const tabs = [
      { id: 'subestaciones', label: 'Subestaciones' },
      { id: 'blindobarras', label: 'Blindobarras' },
      { id: 'ups', label: 'UPS' },
      { id: 'racks', label: 'Racks' },
      { id: 'switches', label: 'Switches' },
      { id: 'hosts', label: 'Hosts' },
      { id: 'servidores', label: 'Servidores' },
      { id: 'aplicaciones', label: 'Aplicaciones' },
      { id: 'dependencias', label: 'Dependencias App-Srv' },
      { id: 'procesos', label: 'Procesos Planta' },
      { id: 'marcas', label: 'Marcas' },
      { id: 'estados', label: 'Estados' },
      { id: 'tipos-host', label: 'Tipos Host' },
      { id: 'tipos-servidor', label: 'Tipos Servidor' }
    ]

    const tabGroups = [
      {
        name: "CMDB & Activos",
        tabs: [
          { id: 'subestaciones', label: 'Subestaciones' },
          { id: 'blindobarras', label: 'Blindobarras' },
          { id: 'racks', label: 'Racks' },
          { id: 'ups', label: 'UPS' },
          { id: 'switches', label: 'Switches' },
          { id: 'hosts', label: 'Hosts' },
          { id: 'servidores', label: 'Servidores' }
        ]
      },
      {
        name: "Software & Procesos",
        tabs: [
          { id: 'aplicaciones', label: 'Aplicaciones' },
          { id: 'dependencias', label: 'Dependencias App-Srv' },
          { id: 'procesos', label: 'Procesos Planta' }
        ]
      },
      {
        name: "Tablas de Soporte",
        tabs: [
          { id: 'marcas', label: 'Marcas' },
          { id: 'estados', label: 'Estados' },
          { id: 'tipos-host', label: 'Tipos Host' },
          { id: 'tipos-servidor', label: 'Tipos Servidor' }
        ]
      }
    ]

    const activeTabLabel = computed(() => {
      const match = tabs.find(t => t.id === activeTab.value)
      return match ? match.label : ''
    })

    // Load lookups
    const loadLookups = async () => {
      try {
        const [subRes, bbRes, upsRes, rkRes, swRes, srvRes, appRes, marcasRes, estadosRes, thRes, tsRes] = await Promise.all([
          axios.get('/api/subestaciones'),
          axios.get('/api/blindobarras'),
          axios.get('/api/ups'),
          axios.get('/api/racks'),
          axios.get('/api/switches'),
          axios.get('/api/servidores'),
          axios.get('/api/aplicaciones'),
          axios.get('/api/marcas'),
          axios.get('/api/estados'),
          axios.get('/api/tipos-host'),
          axios.get('/api/tipos-servidor')
        ])
        subestaciones.value = subRes.data
        blindobarras.value = bbRes.data
        ups.value = upsRes.data
        racks.value = rkRes.data
        switches.value = swRes.data
        servidores.value = srvRes.data
        aplicaciones.value = appRes.data
        marcas.value = marcasRes.data
        estados.value = estadosRes.data
        tiposHost.value = thRes.data
        tiposServidor.value = tsRes.data
      } catch (error) {
        console.error("Error loading lookups for CRUD dropdowns", error)
      }
    }

    const fetchData = async () => {
      loading.value = true
      try {
        await loadLookups()
        const response = await axios.get(`/api/${activeTab.value}`)
        items.value = response.data
      } catch (error) {
        console.error(`Error loading data for ${activeTab.value}`, error)
      } finally {
        loading.value = false
      }
    }

    const agregarFila = () => {
      let defaultObj = {}
      
      switch (activeTab.value) {
        case 'subestaciones':
          defaultObj = { nombre: 'NUEVA_SUBESTACION', capacidad_kva: 1000.0, ubicacion: 'Sector Industrial' }
          break
        case 'blindobarras':
          defaultObj = { 
            nombre: 'NUEVA_BLINDOBARRA', 
            subestacion_id: subestaciones.value[0]?.id || null, 
            capacidad_amperios: 400 
          }
          break
        case 'ups':
          defaultObj = {
            nombre: 'NUEVA_UPS',
            blindobarra_id: blindobarras.value[0]?.id || null,
            marca: '',
            modelo: '',
            serial: '',
            capacidad_kva: 10.0,
            estado_baterias: 'Ok',
            ip: '0.0.0.0',
            vlan: '1'
          }
          break
        case 'racks':
          defaultObj = {
            nombre: 'NUEVO_RACK',
            ups_id: ups.value[0]?.id || null
          }
          break
        case 'switches':
          defaultObj = {
            nombre: 'NUEVO_SW',
            rack_id: racks.value[0]?.id || null,
            marca: '',
            modelo: '',
            serial: '',
            ip: '0.0.0.0',
            vlan_gestion: '1'
          }
          break
        case 'hosts':
          defaultObj = {
            nombre: 'NUEVO_HOST',
            switch_id: switches.value[0]?.id || null,
            marca: '',
            modelo: '',
            serial: '',
            ip: '0.0.0.0',
            rol: 'Otro',
            ubicacion: ''
          }
          break
        case 'servidores':
          defaultObj = {
            nombre: 'NUEVO_SERVIDOR',
            switch_id: switches.value[0]?.id || null,
            marca: '',
            modelo: '',
            serial: '',
            ip: '0.0.0.0',
            tipo_servidor: 'Virtual (VM)',
            sistema_operativo: 'Linux RHEL'
          }
          break
        case 'aplicaciones':
          defaultObj = {
            nombre: 'NUEVA_APP',
            descripcion: '',
            owner_negocio: ''
          }
          break
        case 'dependencias':
          defaultObj = {
            app_id: aplicaciones.value[0]?.id || null,
            servidor_id: servidores.value[0]?.id || null,
            rol_servidor: ''
          }
          break
        case 'procesos':
          defaultObj = {
            nombre_proceso: 'NUEVO_PROCESO',
            linea_produccion: '',
            aplicacion_id: aplicaciones.value[0]?.id || null
          }
          break
        case 'marcas':
          defaultObj = { nombre: 'NUEVA_MARCA' }
          break
        case 'estados':
          defaultObj = { nombre: 'NUEVO_ESTADO' }
          break
        case 'tipos-host':
          defaultObj = { nombre: 'NUEVO_TIPO_HOST' }
          break
        case 'tipos-servidor':
          defaultObj = { nombre: 'NUEVO_TIPO_SERVIDOR' }
          break
      }
      
      // Prepend to items list
      items.value.unshift(defaultObj)
      currentPage.value = 1
    }

    const guardarFila = async (item) => {
      try {
        if (item.id) {
          // Update
          await axios.put(`/api/${activeTab.value}/${item.id}`, item)
          alert("✨ Fila actualizada con éxito.")
        } else {
          // Create
          await axios.post(`/api/${activeTab.value}`, item)
          alert("✨ Nueva fila registrada con éxito.")
        }
        await fetchData()
      } catch (error) {
        console.error("Error saving row", error)
        alert("Ocurrió un error al guardar los datos de la fila. Verifique campos duplicados o requeridos.")
      }
    }

    const eliminarFila = async (item) => {
      if (!item.id) {
        // Just remove unsaved row from visual list
        const actualIdx = items.value.indexOf(item)
        if (actualIdx !== -1) {
          items.value.splice(actualIdx, 1)
        }
        return
      }

      if (!confirm("¿Está seguro de eliminar este registro? Esto podría eliminar dependencias en cascada en otras tablas.")) return

      try {
        await axios.delete(`/api/${activeTab.value}/${item.id}`)
        alert("✨ Registro eliminado.")
        const actualIdx = items.value.indexOf(item)
        if (actualIdx !== -1) {
          items.value.splice(actualIdx, 1)
        }
      } catch (error) {
        console.error("Error deleting row", error)
        alert("Error al eliminar la fila de la base de datos.")
      }
    }

    watch(activeTab, (newVal) => {
      emit('update-tab', newVal)
      resetFilters()
      currentPage.value = 1
      fetchData()
    })

    watch([searchQuery, filters], () => {
      currentPage.value = 1
    }, { deep: true })

    watch(() => props.activeTabProp, (newVal) => {
      if (newVal && newVal !== activeTab.value) {
        activeTab.value = newVal
      }
    })

    onMounted(() => {
      loadUserPermissions()
      fetchData()
    })

    // Modal Host details state
    const showHostModal = ref(false)
    const selectedHostItem = ref(null)

    const abrirDetallesHost = (item) => {
      selectedHostItem.value = item
      showHostModal.value = true
    }

    const cerrarDetallesHost = () => {
      showHostModal.value = false
      selectedHostItem.value = null
    }

    const getSwitchNombre = (id) => {
      const sw = switches.value.find(s => s.id === id)
      return sw ? sw.nombre : 'Depósito (Ninguno)'
    }

    // Modal UPS details state
    const showUpsModal = ref(false)
    const selectedUpsItem = ref(null)

    const abrirDetallesUps = (item) => {
      selectedUpsItem.value = item
      showUpsModal.value = true
    }

    const cerrarDetallesUps = () => {
      showUpsModal.value = false
      selectedUpsItem.value = null
    }

    const getBlindobarraNombre = (id) => {
      const bb = blindobarras.value.find(b => b.id === id)
      return bb ? bb.nombre : 'Ninguna'
    }

    // Modal Unified Creation State
    const showModal = ref(false)
    const modalHost = ref({
      tipo_host_nombre: 'Host',
      nombre: '',
      ip: '',
      marca: '',
      modelo: '',
      serial: '',
      vlan: '1',
      capacidad_kva: 10.0,
      blindobarra_id: null,
      estado_baterias: 'Ok',
      rack_id: null,
      switch_id: null,
      rol: 'Host',
      puerto_switch: '',
      ubicacion: '',
      tipo_servidor: 'Virtual (VM)',
      sistema_operativo: ''
    })

    const abrirModalAlta = () => {
      let defaultType = 'Host'
      if (activeTab.value === 'ups') defaultType = 'UPS'
      else if (activeTab.value === 'switches') defaultType = 'Switch'
      else if (activeTab.value === 'servidores') defaultType = 'Servidor'
      else if (activeTab.value === 'hosts') {
        const firstCustom = tiposHost.value.find(t => !['UPS', 'Switch', 'Servidor'].includes(t.nombre))
        defaultType = firstCustom ? firstCustom.nombre : 'Host'
      }

      modalHost.value = {
        tipo_host_nombre: defaultType,
        nombre: '',
        ip: '',
        marca: marcas.value[0]?.nombre || '',
        modelo: '',
        serial: '',
        vlan: '1',
        capacidad_kva: 10.0,
        blindobarra_id: blindobarras.value[0]?.id || null,
        estado_baterias: 'Ok',
        rack_id: racks.value[0]?.id || null,
        switch_id: switches.value[0]?.id || null,
        rol: defaultType,
        puerto_switch: '',
        ubicacion: '',
        tipo_servidor: 'Virtual (VM)',
        sistema_operativo: ''
      }
      showModal.value = true
    }

    const cerrarModal = () => {
      showModal.value = false
    }

    const guardarModalHost = async () => {
      try {
        let payload = {
          nombre: modalHost.value.nombre,
          marca: modalHost.value.marca,
          modelo: modalHost.value.modelo,
          serial: modalHost.value.serial,
          ip: modalHost.value.ip
        }

        let endpoint = '/api/hosts'

        if (modalHost.value.tipo_host_nombre === 'UPS') {
          payload.blindobarra_id = modalHost.value.blindobarra_id
          payload.capacidad_kva = modalHost.value.capacidad_kva
          payload.estado_baterias = modalHost.value.estado_baterias
          payload.vlan = modalHost.value.vlan
          endpoint = '/api/ups'
        } else if (modalHost.value.tipo_host_nombre === 'Switch') {
          payload.rack_id = modalHost.value.rack_id
          payload.vlan_gestion = modalHost.value.vlan
          endpoint = '/api/switches'
        } else if (modalHost.value.tipo_host_nombre === 'Servidor') {
          payload.switch_id = modalHost.value.switch_id
          payload.tipo_servidor = modalHost.value.tipo_servidor
          payload.sistema_operativo = modalHost.value.sistema_operativo
          endpoint = '/api/servidores'
        } else {
          payload.switch_id = modalHost.value.switch_id
          payload.rol = modalHost.value.tipo_host_nombre
          payload.puerto_switch = modalHost.value.puerto_switch
          payload.ubicacion = modalHost.value.ubicacion
          endpoint = '/api/hosts'
        }

        await axios.post(endpoint, payload)
        
        alert("✨ Activo registrado correctamente.")
        showModal.value = false
        await fetchData()
      } catch (error) {
        console.error("Error creating host from modal", error)
        alert("Error al registrar el activo. Verifique que el nombre o serial no estén duplicados.")
      }
    }

    return {
      activeTab,
      tabs,
      tabGroups,
      activeTabLabel,
      items,
      searchQuery,
      filters,
      resetFilters,
      clearFilters,
      hasActiveFilters,
      filteredItems,
      columnCount,
      paginatedItems,
      currentPage,
      pageSize,
      totalPages,
      visiblePages,
      loading,
      canWrite,
      subestaciones,
      blindobarras,
      ups,
      racks,
      switches,
      servidores,
      aplicaciones,
      marcas,
      estados,
      tiposHost,
      tiposServidor,
      showUpsModal,
      selectedUpsItem,
      abrirDetallesUps,
      cerrarDetallesUps,
      showHostModal,
      selectedHostItem,
      abrirDetallesHost,
      cerrarDetallesHost,
      getSwitchNombre,
      getBlindobarraNombre,
      showModal,
      modalHost,
      abrirModalAlta,
      cerrarModal,
      guardarModalHost,
      agregarFila,
      guardarFila,
      eliminarFila
    }
  }
}
</script>
