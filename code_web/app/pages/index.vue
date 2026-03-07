<script setup lang="ts">
useHead({ title: 'QuyY Print - In Lá Phái Quy Y' })

// ===================== COMPOSABLES =====================
const toast = useToast()
const { config, saveConfig, resetConfig, exportConfig } = useConfigManager()

// Date
const dateManager = useDateManager(config)
const { selectedDate, lunarInfo, highlightDate, lunarDisplayText,
  onDateChange, clearDate, onLunarTextChange, onBuddhistYearChange, highlightDatePicker } = dateManager

// Excel & Records
const excelManager = useExcelManager(clearDate)
const { recordCount, excelFileName, processedRecords, currentRecordIndex,
  isUsingDemoData, showQuickEntry, quickForm, currentRecord, totalRecords,
  onExcelUpload, prevRecord, nextRecord, applyQuickEntry, clearQuickForm } = excelManager

// Canvas
const canvasEditor = useCanvasEditor({ config, currentRecord, currentRecordIndex })
const { canvasRef, canvasWidth, canvasHeight, selectedFields, fieldOverrides,
  inlineEditField, inlineEditValue, inlineEditPos, allFields,
  initCanvas, loadVniFont, drawCanvas,
  onCanvasMouseDown, onCanvasMouseMove, onCanvasMouseUp,
  onCanvasKeyDown, onCanvasDblClick,
  saveInlineEdit, onInlineEditKeydown } = canvasEditor

// PDF
const pdfGenerator = usePdfGenerator({
  config, processedRecords, currentRecordIndex, fieldOverrides,
  selectedDate, isUsingDemoData, highlightDatePicker
})
const { isGeneratingPdf, generatePdf, quickPrint, printSingleRecord } = pdfGenerator

// ===================== UI STATE =====================
const showAdvanced = ref(false)
const showFieldsPanel = ref(false)

// ===================== INIT =====================
onMounted(() => {
  initCanvas()
  loadVniFont()
  excelManager.initDemoData()
  nextTick(() => drawCanvas())
})

// ===================== CONFIG ACTIONS =====================
function onSaveConfig() {
  saveConfig()
  toast.add({ severity: 'success', summary: 'Đã lưu', detail: 'Cấu hình đã được lưu', life: 2000 })
}
function onResetConfig() {
  resetConfig()
  toast.add({ severity: 'info', summary: 'Đã reset', detail: 'Cấu hình đã khôi phục mặc định', life: 2000 })
}
function onExportConfig() {
  const jsonStr = exportConfig()
  const blob = new Blob([jsonStr], { type: 'application/json' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'quyy_config.json'
  a.click()
}

function onCustomValueChange(key: string, newValue: string) {
  if (config.value.custom_fields[key]) {
    config.value.custom_fields[key].value = newValue
  }
}

// Field editing dialog
const editingField = ref<{ key: string; label: string; x: number; y: number; size: number; align: string } | null>(null)
const showEditDialog = ref(false)

function openFieldEdit(key: string) {
  const f = allFields.value[key]
  if (!f) return
  editingField.value = { key, label: f.label, x: f.x, y: f.y, size: f.size, align: f.align }
  showEditDialog.value = true
}

function saveFieldEdit() {
  if (!editingField.value) return
  const { key, x, y, size, align } = editingField.value
  const alignTyped = align as 'L' | 'C' | 'R'
  if (config.value.field_positions[key]) {
    Object.assign(config.value.field_positions[key], { x, y, size, align: alignTyped })
  } else if (config.value.custom_fields[key]) {
    Object.assign(config.value.custom_fields[key], { x, y, size, align: alignTyped })
  }
  showEditDialog.value = false
  toast.add({ severity: 'success', summary: 'Đã cập nhật', detail: editingField.value.label, life: 2000 })
}
</script>

<template>
  <div class="page-container">
    <Toast />

    <!-- ============ TOOLBAR ============ -->
    <div class="toolbar">
      <div class="toolbar-left">
        <!-- Upload Excel -->
        <label class="btn-upload" tabindex="0">
          <i class="pi pi-file-excel" />
          <span>{{ excelFileName || 'Tải Excel' }}</span>
          <input type="file" accept=".xlsx,.xls" hidden @change="onExcelUpload" />
        </label>
        <span v-if="recordCount > 0 && !isUsingDemoData" class="record-badge">
          {{ recordCount }} bản ghi
        </span>
        <span v-else-if="isUsingDemoData" class="record-badge demo">Demo</span>

        <div class="toolbar-divider" />

        <!-- Ngày Quy Y -->
        <div class="date-group" :class="{ 'highlight-pulse': highlightDate }">
          <label class="date-label">📅 Ngày Quy Y:</label>
          <DatePicker v-model="selectedDate" dateFormat="dd/mm/yy" placeholder="Chọn ngày..."
            showIcon class="date-input" @update:modelValue="onDateChange" />
          <Button v-if="selectedDate" icon="pi pi-times" severity="secondary" text rounded size="small"
            @click="clearDate" v-tooltip.bottom="'Xóa ngày'" />
        </div>

        <!-- Lunar Info -->
        <div v-if="lunarInfo" class="lunar-edit-group">
          <span class="lunar-label">🌙 ÂL:</span>
          <input type="text" class="lunar-inline" :value="lunarDisplayText"
            @change="(e: Event) => onLunarTextChange((e.target as HTMLInputElement).value)"
            v-tooltip.bottom="'Sửa ngày âm lịch'" />
          <span class="lunar-label">☸️ PL:</span>
          <input type="text" class="lunar-inline pl-input" :value="config.custom_fields.phat_lich?.value || ''"
            @change="(e: Event) => onBuddhistYearChange((e.target as HTMLInputElement).value)"
            v-tooltip.bottom="'Sửa Phật lịch'" />
        </div>
      </div>

      <div class="toolbar-right">
        <Button label="In hàng loạt" icon="pi pi-print" severity="warn" @click="quickPrint"
          v-tooltip.bottom="'Tạo PDF và In ngay'" />
        <Button label="Tạo PDF" icon="pi pi-file-pdf" severity="success" :loading="isGeneratingPdf"
          @click="generatePdf" v-tooltip.bottom="'Tạo và tải PDF xuống'" />
        <div class="toolbar-divider" />
        <Button :icon="showFieldsPanel ? 'pi pi-times' : 'pi pi-sliders-h'"
          :severity="showFieldsPanel ? 'secondary' : 'contrast'" text rounded
          v-tooltip.bottom="showFieldsPanel ? 'Ẩn bảng fields' : 'Hiện bảng fields'"
          @click="showFieldsPanel = !showFieldsPanel" />
      </div>
    </div>

    <!-- ============ MAIN AREA ============ -->
    <div class="main-area">
      <!-- LEFT: Records List -->
      <div class="records-panel">
        <div class="records-header"><i class="pi pi-users" /> Danh sách ({{ totalRecords }})</div>
        <div class="records-list">
          <div v-for="(rec, idx) in processedRecords" :key="idx"
            class="record-item" :class="{ active: idx === currentRecordIndex }"
            @click="currentRecordIndex = idx">
            <span class="rec-idx">{{ idx + 1 }}</span>
            <div class="rec-info">
              <span class="rec-name">{{ rec.ho_ten || '(chưa có tên)' }}</span>
              <span v-if="rec.phap_danh" class="rec-phap">{{ rec.phap_danh }}</span>
            </div>
            <button class="rec-print-btn" :class="{ visible: idx === currentRecordIndex }"
              @click.stop="printSingleRecord(idx)" title="In người này">
              <i class="pi pi-print" />
            </button>
          </div>
          <div v-if="processedRecords.length === 0" class="records-empty">Chưa có dữ liệu</div>
        </div>
      </div>

      <!-- CENTER: Canvas -->
      <div class="canvas-panel">
        <div class="canvas-header">
          <span class="canvas-title"><i class="pi pi-image" /> Canvas Preview</span>
          <div v-if="totalRecords > 0" class="record-nav">
            <Button icon="pi pi-chevron-left" text rounded size="small" :disabled="currentRecordIndex === 0"
              @click="prevRecord" />
            <span class="record-pos">{{ currentRecordIndex + 1 }} / {{ totalRecords }}</span>
            <Button icon="pi pi-chevron-right" text rounded size="small"
              :disabled="currentRecordIndex >= totalRecords - 1" @click="nextRecord" />
          </div>
        </div>
        <div class="canvas-wrapper">
          <div class="canvas-container">
            <canvas ref="canvasRef" :width="canvasWidth" :height="canvasHeight" tabindex="0"
              @mousedown="onCanvasMouseDown" @mousemove="onCanvasMouseMove" @mouseup="onCanvasMouseUp"
              @mouseleave="onCanvasMouseUp" @keydown="onCanvasKeyDown" @dblclick="onCanvasDblClick" />
            <input v-if="inlineEditField" v-model="inlineEditValue" class="canvas-inline-input"
              :style="{ left: inlineEditPos.left, top: inlineEditPos.top, width: inlineEditPos.width, fontSize: inlineEditPos.fontSize }"
              @blur="saveInlineEdit" @keydown="onInlineEditKeydown" @click.stop />
          </div>
        </div>
        <div v-if="selectedFields.size > 0" class="selection-info">
          <i class="pi pi-arrows-alt" /> {{ selectedFields.size }} field đang chọn – Phím ←↑→↓ di chuyển
        </div>
      </div>

      <!-- RIGHT: Fields Panel -->
      <div v-if="showFieldsPanel" class="fields-panel">
        <div class="panel-section">
          <div class="panel-header">
            <i class="pi pi-list" /> Danh sách Fields
            <Button icon="pi pi-save" text rounded size="small" v-tooltip.left="'Lưu cấu hình'" @click="onSaveConfig" />
          </div>
          <div class="fields-table">
            <div class="field-row header">
              <span class="col-name">Field</span>
              <span class="col-val">Giá trị</span>
              <span class="col-x">X</span>
              <span class="col-y">Y</span>
              <span class="col-action"></span>
            </div>
            <div v-for="(field, key) in allFields" :key="key" class="field-row"
              :class="{ selected: selectedFields.has(key as string), custom: field.isCustom }"
              @click="selectedFields = new Set([key as string])">
              <span class="col-name" :title="field.label">{{ field.label }}</span>
              <span class="col-val">
                <input v-if="field.isCustom" type="text" class="inline-val-input"
                  :value="config.custom_fields[key as string]?.value || ''"
                  @input="(e: Event) => onCustomValueChange(key as string, (e.target as HTMLInputElement).value)"
                  @click.stop placeholder="..." />
                <span v-else class="val-readonly" :title="field.value">{{ field.value || '—' }}</span>
              </span>
              <span class="col-x">{{ field.x.toFixed(1) }}</span>
              <span class="col-y">{{ field.y.toFixed(1) }}</span>
              <span class="col-action">
                <Button icon="pi pi-pencil" text rounded size="small" @click.stop="openFieldEdit(key as string)" />
              </span>
            </div>
          </div>
        </div>

        <!-- Nhập nhanh -->
        <div class="panel-section">
          <div class="panel-header clickable" @click="showQuickEntry = !showQuickEntry">
            <i :class="showQuickEntry ? 'pi pi-chevron-down' : 'pi pi-chevron-right'" />
            ✍️ Nhập nhanh (không cần Excel)
          </div>
          <div v-if="showQuickEntry" class="quick-entry-form">
            <div class="form-row">
              <label>Họ tên <span class="required">*</span></label>
              <InputText v-model="quickForm.ho_ten" placeholder="Nguyễn Văn A" class="w-full" />
            </div>
            <div class="form-row">
              <label>Pháp danh</label>
              <InputText v-model="quickForm.phap_danh" placeholder="Tâm Minh" class="w-full" />
            </div>
            <div class="form-row-2col">
              <div>
                <label>Năm sinh</label>
                <InputText v-model="quickForm.sinh_nam" placeholder="1990" />
              </div>
              <div>
                <label>Địa chỉ</label>
                <InputText v-model="quickForm.dia_chi" placeholder="TP.HCM" />
              </div>
            </div>
            <div class="form-actions">
              <Button label="Áp dụng" icon="pi pi-check" size="small" @click="applyQuickEntry" />
              <Button label="Xóa" icon="pi pi-refresh" size="small" severity="secondary" text @click="clearQuickForm" />
            </div>
          </div>
        </div>

        <!-- Cài đặt nâng cao -->
        <div class="panel-section">
          <div class="panel-header clickable" @click="showAdvanced = !showAdvanced">
            <i :class="showAdvanced ? 'pi pi-chevron-down' : 'pi pi-chevron-right'" />
            ⚙️ Cài đặt nâng cao
          </div>
          <div v-if="showAdvanced" class="advanced-settings">
            <div class="setting-item">
              <label>Sử dụng Font VNI</label>
              <InputSwitch v-model="config.use_vni_font" />
            </div>
            <div class="setting-item">
              <label>In kèm ảnh nền (phôi mẫu)</label>
              <InputSwitch v-model="config.use_background_image" />
            </div>
            <div class="setting-item">
              <Button label="Reset mặc định" icon="pi pi-undo" size="small" severity="danger" text @click="onResetConfig" />
              <Button label="Export Config" icon="pi pi-download" size="small" severity="secondary" text @click="onExportConfig" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ============ EDIT FIELD DIALOG ============ -->
    <Dialog v-model:visible="showEditDialog" :header="editingField?.label || 'Chỉnh sửa'" modal :style="{ width: '360px' }">
      <div v-if="editingField" class="edit-dialog-body">
        <div class="form-row">
          <label>X (mm)</label>
          <InputNumber v-model="editingField.x" :minFractionDigits="1" :maxFractionDigits="1" />
        </div>
        <div class="form-row">
          <label>Y (mm)</label>
          <InputNumber v-model="editingField.y" :minFractionDigits="1" :maxFractionDigits="1" />
        </div>
        <div class="form-row">
          <label>Cỡ chữ</label>
          <InputNumber v-model="editingField.size" :min="6" :max="72" />
        </div>
        <div class="form-row">
          <label>Căn lề</label>
          <SelectButton v-model="editingField.align" :options="[
            { label: 'Trái', value: 'L' },
            { label: 'Giữa', value: 'C' },
            { label: 'Phải', value: 'R' }
          ]" optionLabel="label" optionValue="value" />
        </div>
      </div>
      <template #footer>
        <Button label="Hủy" severity="secondary" text @click="showEditDialog = false" />
        <Button label="Lưu" icon="pi pi-check" @click="saveFieldEdit" />
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.page-container { display: flex; flex-direction: column; height: calc(100vh - 60px); overflow: hidden; }

/* TOOLBAR */
.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px 16px; background: var(--surface-card); border-bottom: 1px solid var(--surface-border); flex-wrap: wrap; min-height: 52px; }
.toolbar-left, .toolbar-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.toolbar-divider { width: 1px; height: 28px; background: var(--surface-border); }
.btn-upload { display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; background: var(--primary-color); color: white; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 0.875rem; transition: all 0.2s; white-space: nowrap; }
.btn-upload:hover { filter: brightness(1.1); }
.btn-upload i { font-size: 1.1rem; }
.record-badge { background: var(--green-100); color: var(--green-700); padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; }
.record-badge.demo { background: var(--blue-100); color: var(--blue-700); }
.date-group { display: flex; align-items: center; gap: 6px; }
.date-label { font-size: 0.85rem; font-weight: 600; white-space: nowrap; }
.date-input { width: 145px; }
:deep(.date-input .p-inputtext) { font-size: 0.85rem; padding: 6px 8px; }
.date-group.highlight-pulse { animation: date-pulse 0.6s ease-in-out 5; border-radius: 8px; }
@keyframes date-pulse {
  0%, 100% { background: transparent; box-shadow: none; }
  50% { background: rgba(251,146,60,0.2); box-shadow: 0 0 0 3px rgba(251,146,60,0.4); }
}
.lunar-edit-group { display: flex; align-items: center; gap: 4px; background: linear-gradient(135deg, var(--yellow-100), var(--orange-100)); padding: 3px 10px; border-radius: 8px; white-space: nowrap; }
.lunar-label { font-size: 0.78rem; font-weight: 700; color: var(--orange-800); }
.lunar-inline { width: 130px; border: 1px solid transparent; border-radius: 4px; padding: 2px 6px; font-size: 0.8rem; font-weight: 600; background: rgba(255,255,255,0.5); color: var(--orange-900); transition: all 0.15s; }
.lunar-inline.pl-input { width: 55px; text-align: center; }
.lunar-inline:hover { border-color: var(--orange-300); background: rgba(255,255,255,0.8); }
.lunar-inline:focus { outline: none; border-color: var(--orange-500); background: white; box-shadow: 0 0 0 2px rgba(251,146,60,0.2); }

/* MAIN AREA */
.main-area { display: flex; flex: 1; overflow: hidden; }

/* LEFT: Records */
.records-panel { width: 200px; min-width: 160px; border-right: 1px solid var(--surface-border); display: flex; flex-direction: column; background: var(--surface-ground); }
.records-header { padding: 8px 12px; font-weight: 700; font-size: 0.8rem; background: var(--surface-card); border-bottom: 1px solid var(--surface-border); display: flex; align-items: center; gap: 6px; }
.records-list { flex: 1; overflow-y: auto; }
.record-item { display: flex; align-items: center; gap: 8px; padding: 7px 10px; cursor: pointer; border-bottom: 1px solid var(--surface-100); transition: background 0.12s; font-size: 0.8rem; }
.record-item:hover { background: var(--surface-hover); }
.record-item.active { background: var(--green-50); border-left: 3px solid var(--green-500); }
.rec-idx { width: 20px; height: 20px; border-radius: 50%; background: var(--surface-200); display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 700; flex-shrink: 0; }
.record-item.active .rec-idx { background: var(--green-500); color: white; }
.rec-info { display: flex; flex-direction: column; overflow: hidden; min-width: 0; }
.rec-name { font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rec-phap { font-size: 0.72rem; color: var(--text-color-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.records-empty { padding: 20px; text-align: center; color: var(--text-color-secondary); font-size: 0.8rem; }
.rec-print-btn { margin-left: auto; flex-shrink: 0; border: none; background: none; cursor: pointer; padding: 3px 5px; border-radius: 4px; color: var(--text-color-secondary); opacity: 0.15; transition: all 0.15s; font-size: 0.8rem; }
.rec-print-btn.visible, .record-item:hover .rec-print-btn { opacity: 0.6; }
.rec-print-btn:hover { opacity: 1 !important; color: var(--green-600); background: var(--green-50); }

/* CENTER: Canvas */
.canvas-panel { flex: 1; display: flex; flex-direction: column; overflow: auto; padding: 12px; }
.canvas-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.canvas-title { font-size: 0.85rem; color: var(--text-color-secondary); }
.record-nav { display: flex; align-items: center; gap: 4px; }
.record-pos { font-weight: 700; font-size: 0.9rem; min-width: 60px; text-align: center; }
.canvas-wrapper { display: flex; justify-content: center; overflow: auto; }
.canvas-container { position: relative; display: inline-block; }
.canvas-container canvas { border: 1px solid var(--surface-border); border-radius: 6px; cursor: crosshair; max-width: 100%; height: auto; }
.canvas-inline-input { position: absolute; z-index: 10; padding: 3px 6px; border: 2px solid #22c55e; border-radius: 4px; background: rgba(255,255,255,0.95); color: #1a1a1a; font-weight: 600; box-shadow: 0 2px 12px rgba(0,0,0,0.15), 0 0 0 3px rgba(34,197,94,0.2); outline: none; min-width: 60px; }
.selection-info { text-align: center; padding: 6px; color: var(--green-600); font-weight: 600; font-size: 0.85rem; }

/* RIGHT: Fields panel */
.fields-panel { width: 380px; min-width: 320px; border-left: 1px solid var(--surface-border); overflow-y: auto; background: var(--surface-ground); }
.panel-section { border-bottom: 1px solid var(--surface-border); }
.panel-header { display: flex; align-items: center; gap: 8px; padding: 10px 14px; font-weight: 700; font-size: 0.85rem; background: var(--surface-card); }
.panel-header.clickable { cursor: pointer; user-select: none; transition: background 0.15s; }
.panel-header.clickable:hover { background: var(--surface-hover); }
.fields-table { font-size: 0.8rem; }
.field-row { display: flex; align-items: center; padding: 6px 14px; border-bottom: 1px solid var(--surface-100); cursor: pointer; transition: background 0.15s; }
.field-row:hover { background: var(--surface-hover); }
.field-row.selected { background: var(--green-50); border-left: 3px solid var(--green-500); }
.field-row.custom .col-name { color: var(--red-600); }
.field-row.header { font-weight: 700; background: var(--surface-card); cursor: default; font-size: 0.75rem; text-transform: uppercase; color: var(--text-color-secondary); }
.col-name { width: 80px; min-width: 70px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.col-val { flex: 1; min-width: 50px; overflow: hidden; }
.col-x, .col-y { width: 42px; text-align: right; font-variant-numeric: tabular-nums; }
.col-action { width: 32px; text-align: center; }
.inline-val-input { width: 100%; border: 1px solid transparent; border-radius: 4px; padding: 2px 5px; font-size: 0.8rem; background: transparent; color: var(--text-color); transition: all 0.15s; font-variant-numeric: tabular-nums; }
.inline-val-input:hover { border-color: var(--surface-300); background: var(--surface-0); }
.inline-val-input:focus { outline: none; border-color: var(--primary-color); background: var(--surface-0); box-shadow: 0 0 0 2px rgba(var(--primary-color-rgb, 59, 130, 246), 0.15); }
.val-readonly { color: var(--text-color-secondary); font-size: 0.78rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: block; }

/* Quick entry */
.quick-entry-form { padding: 12px 14px; display: flex; flex-direction: column; gap: 8px; }
.form-row { display: flex; flex-direction: column; gap: 3px; }
.form-row label { font-size: 0.8rem; font-weight: 600; }
.form-row .required { color: var(--red-500); }
.form-row-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.form-row-2col label { font-size: 0.8rem; font-weight: 600; display: block; margin-bottom: 3px; }
.form-actions { display: flex; gap: 8px; margin-top: 4px; }
:deep(.quick-entry-form .p-inputtext) { font-size: 0.85rem; padding: 6px 8px; }

/* Advanced settings */
.advanced-settings { padding: 12px 14px; display: flex; flex-direction: column; gap: 12px; }
.setting-item { display: flex; align-items: center; justify-content: space-between; gap: 8px; font-size: 0.85rem; }

/* Edit dialog */
.edit-dialog-body { display: flex; flex-direction: column; gap: 12px; }
.edit-dialog-body .form-row { display: flex; flex-direction: column; gap: 4px; }
.edit-dialog-body label { font-weight: 600; font-size: 0.85rem; }
</style>
