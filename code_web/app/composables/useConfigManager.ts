/**
 * Quản lý cấu hình ứng dụng (localStorage)
 * Port từ Python: core/config_manager.py + config.py
 */

export interface FieldPosition {
    x: number
    y: number
    size: number
    bold: boolean
    italic: boolean
    align: 'L' | 'C' | 'R'
}

export interface CustomField extends FieldPosition {
    value: string
}

export interface AppConfig {
    field_positions: Record<string, FieldPosition>
    excel_mapping: Record<string, string>
    custom_fields: Record<string, CustomField>
    use_vni_font: boolean
    export_mode: 'single'
    use_background_image: boolean
}

const DEFAULT_FIELD_POSITIONS: Record<string, FieldPosition> = {
    phap_danh: { x: 196.6, y: 139.0, size: 18, bold: false, italic: true, align: 'L' },
    ho_ten: { x: 196.6, y: 129.4, size: 18, bold: false, italic: true, align: 'L' },
    sinh_nam: { x: 197.0, y: 147.0, size: 12, bold: false, italic: true, align: 'L' },
    dia_chi: { x: 197.4, y: 154.2, size: 12, bold: true, italic: true, align: 'L' }
}

const DEFAULT_EXCEL_MAPPING: Record<string, string> = {
    ho_ten: 'hovaten',
    phap_danh: 'phapdanh',
    nam_sinh: 'namsinh',
    dia_chi: 'diachithuongtru_short'
}

const DEFAULT_CUSTOM_FIELDS: Record<string, CustomField> = {
    phat_lich: { value: '', x: 206.0, y: 178.0, size: 12, bold: false, italic: false, align: 'L' },
    ngay_duong: { value: '', x: 235.2, y: 178.4, size: 11, bold: false, italic: true, align: 'C' },
    thang_duong: { value: '', x: 259.6, y: 178.0, size: 11, bold: false, italic: true, align: 'C' },
    nam_duong: { value: '', x: 276.6, y: 178.0, size: 11, bold: false, italic: true, align: 'C' },
    ngay_am: { value: '', x: 235.6, y: 182.8, size: 11, bold: false, italic: true, align: 'C' },
    thang_am: { value: '', x: 259.2, y: 182.8, size: 11, bold: false, italic: true, align: 'C' },
    nam_am: { value: '', x: 277.8, y: 183.6, size: 11, bold: true, italic: true, align: 'C' }
}

const STORAGE_KEY = 'quyy_config'

function deepClone<T>(obj: T): T {
    return JSON.parse(JSON.stringify(obj))
}

export function useConfigManager() {
    const config = useState<AppConfig>('appConfig', () => loadConfig())

    function getDefaultConfig(): AppConfig {
        return {
            field_positions: deepClone(DEFAULT_FIELD_POSITIONS),
            excel_mapping: deepClone(DEFAULT_EXCEL_MAPPING),
            custom_fields: deepClone(DEFAULT_CUSTOM_FIELDS),
            use_vni_font: true,
            export_mode: 'single',
            use_background_image: false
        }
    }

    function loadConfig(): AppConfig {
        if (import.meta.server) return getDefaultConfig()
        try {
            const raw = localStorage.getItem(STORAGE_KEY)
            if (raw) {
                const saved = JSON.parse(raw)
                // Merge với defaults để đảm bảo không thiếu key
                const defaults = getDefaultConfig()
                return {
                    field_positions: { ...defaults.field_positions, ...saved.field_positions },
                    excel_mapping: { ...defaults.excel_mapping, ...saved.excel_mapping },
                    custom_fields: { ...defaults.custom_fields, ...saved.custom_fields },
                    use_vni_font: saved.use_vni_font ?? defaults.use_vni_font,
                    export_mode: 'single',
                    use_background_image: saved.use_background_image ?? defaults.use_background_image
                }
            }
        } catch (e) {
            console.warn('[ConfigManager] Lỗi load config:', e)
        }
        return getDefaultConfig()
    }

    function saveConfig() {
        if (import.meta.server) return
        try {
            // Không lưu selected_date
            localStorage.setItem(STORAGE_KEY, JSON.stringify(config.value))
        } catch (e) {
            console.warn('[ConfigManager] Lỗi save config:', e)
        }
    }

    function resetConfig() {
        config.value = getDefaultConfig()
        saveConfig()
    }

    function updateFieldPosition(fieldName: string, updates: Partial<FieldPosition>) {
        if (config.value.field_positions[fieldName]) {
            Object.assign(config.value.field_positions[fieldName], updates)
        }
    }

    function updateCustomField(fieldName: string, updates: Partial<CustomField>) {
        if (config.value.custom_fields[fieldName]) {
            Object.assign(config.value.custom_fields[fieldName], updates)
        }
    }

    function addCustomField(name: string, field: CustomField) {
        if (config.value.custom_fields[name]) {
            throw new Error(`Field '${name}' đã tồn tại!`)
        }
        config.value.custom_fields[name] = field
    }

    function deleteCustomField(name: string) {
        delete config.value.custom_fields[name]
    }

    /**
     * Cập nhật giá trị các custom fields ngày tháng từ LunarResult
     */
    function updateDateFields(dateInfo: {
        solar_day: number, solar_month: number, solar_year: number,
        lunar_day: number, lunar_month: number,
        lunar_year_name: string, buddhist_year: number
    }) {
        const fields = config.value.custom_fields
        if (fields.ngay_duong) fields.ngay_duong.value = String(dateInfo.solar_day)
        if (fields.thang_duong) fields.thang_duong.value = String(dateInfo.solar_month)
        if (fields.nam_duong) fields.nam_duong.value = String(dateInfo.solar_year)
        if (fields.ngay_am) fields.ngay_am.value = String(dateInfo.lunar_day)
        if (fields.thang_am) fields.thang_am.value = String(dateInfo.lunar_month)
        if (fields.nam_am) fields.nam_am.value = dateInfo.lunar_year_name
        if (fields.phat_lich) fields.phat_lich.value = String(dateInfo.buddhist_year)
    }

    function clearDateFields() {
        const dateKeys = ['ngay_duong', 'thang_duong', 'nam_duong', 'ngay_am', 'thang_am', 'nam_am', 'phat_lich']
        for (const key of dateKeys) {
            if (config.value.custom_fields[key]) {
                config.value.custom_fields[key].value = ''
            }
        }
    }

    /** Export config ra JSON string (cho download) */
    function exportConfig(): string {
        return JSON.stringify(config.value, null, 2)
    }

    /** Import config từ JSON string */
    function importConfig(jsonStr: string) {
        try {
            const imported = JSON.parse(jsonStr) as Partial<AppConfig>
            const defaults = getDefaultConfig()
            config.value = {
                field_positions: { ...defaults.field_positions, ...imported.field_positions },
                excel_mapping: { ...defaults.excel_mapping, ...imported.excel_mapping },
                custom_fields: { ...defaults.custom_fields, ...imported.custom_fields },
                use_vni_font: imported.use_vni_font ?? defaults.use_vni_font,
                export_mode: 'single',
                use_background_image: imported.use_background_image ?? defaults.use_background_image
            }
            saveConfig()
        } catch (e) {
            throw new Error('File config không hợp lệ')
        }
    }

    return {
        config,
        saveConfig,
        resetConfig,
        loadConfig: () => { config.value = loadConfig() },
        updateFieldPosition,
        updateCustomField,
        addCustomField,
        deleteCustomField,
        updateDateFields,
        clearDateFields,
        exportConfig,
        importConfig,
        getDefaultConfig
    }
}
