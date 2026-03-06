/**
 * Xử lý dữ liệu từ Excel → định dạng in PDF
 * Port từ Python: core/data_processor.py + core/excel_handler.py
 */

const MAX_FIELD_LENGTH = 50
const MAX_ADDR_LENGTH = 100

export interface ProcessedRecord {
    phap_danh: string
    ho_ten: string
    sinh_nam: string
    dia_chi: string
    _has_error: boolean
    _error_details: string[]
    _row_index: number
}

export interface ValidationResult {
    has_warnings: boolean
    missing_columns: string[]
    row_warnings: { row: number; name: string; issues: string[] }[]
    summary: string
}

/** Các cột Excel bắt buộc */
const REQUIRED_COLUMNS = ['hovaten', 'phapdanh', 'namsinh', 'diachithuongtru_short']

export function useDataProcessor() {

    /**
     * Đọc file Excel, trả về array of objects
     */
    async function readExcelFile(file: File): Promise<{ count: number; data: Record<string, unknown>[] }> {
        const XLSX = await import('xlsx')
        const buffer = await file.arrayBuffer()
        const workbook = XLSX.read(buffer, { type: 'array' })
        const sheetName = workbook.SheetNames[0]
        const sheet = workbook.Sheets[sheetName]
        let data: Record<string, unknown>[] = XLSX.utils.sheet_to_json(sheet)

        // Lọc bỏ dòng có hovaten rỗng/null
        data = data.filter(row => {
            const hoTen = row['hovaten']
            return hoTen !== undefined && hoTen !== null && String(hoTen).trim() !== ''
        })

        return { count: data.length, data }
    }

    /**
     * Validate dữ liệu Excel
     */
    function validateExcel(data: Record<string, unknown>[]): ValidationResult {
        const result: ValidationResult = {
            has_warnings: false,
            missing_columns: [],
            row_warnings: [],
            summary: ''
        }

        if (data.length === 0) {
            result.summary = '✅ Không có dữ liệu'
            return result
        }

        // Kiểm tra cột bắt buộc
        const existingColumns = Object.keys(data[0])
        for (const col of REQUIRED_COLUMNS) {
            if (!existingColumns.includes(col)) {
                result.missing_columns.push(col)
            }
        }
        if (result.missing_columns.length > 0) result.has_warnings = true

        // Kiểm tra từng dòng
        data.forEach((row, idx) => {
            const issues: string[] = []
            const excelRow = idx + 2 // +2: Excel bắt đầu từ 1 + header

            const hoTen = row['hovaten']
            if (!hoTen || String(hoTen).trim() === '') {
                issues.push('Thiếu họ tên')
            } else if (String(hoTen).length > MAX_FIELD_LENGTH) {
                issues.push(`Họ tên quá dài (${String(hoTen).length} ký tự)`)
            }

            const phapDanh = row['phapdanh']
            if (phapDanh && String(phapDanh).trim() !== '' && String(phapDanh).length > MAX_FIELD_LENGTH) {
                issues.push(`Pháp danh quá dài (${String(phapDanh).length} ký tự)`)
            }

            const namSinh = row['namsinh']
            if (namSinh !== undefined && namSinh !== null && String(namSinh).trim() !== '') {
                let nsStr = String(namSinh).trim()
                if (nsStr.includes('.')) nsStr = nsStr.split('.')[0]
                if (!/^\d{4}$/.test(nsStr)) {
                    issues.push(`Năm sinh không hợp lệ: '${namSinh}'`)
                }
            }

            const diaChi = row['diachithuongtru_short']
            if (diaChi && String(diaChi).trim() !== '' && String(diaChi).length > MAX_ADDR_LENGTH) {
                issues.push(`Địa chỉ quá dài (${String(diaChi).length} ký tự)`)
            }

            if (issues.length > 0) {
                result.row_warnings.push({
                    row: excelRow,
                    name: hoTen ? String(hoTen).substring(0, 25) : `Dòng ${excelRow}`,
                    issues
                })
            }
        })

        if (result.row_warnings.length > 0) result.has_warnings = true

        // Summary
        const parts: string[] = []
        if (result.missing_columns.length > 0) parts.push(`⚠️ Thiếu cột: ${result.missing_columns.join(', ')}`)
        if (result.row_warnings.length > 0) parts.push(`⚠️ ${result.row_warnings.length} dòng có vấn đề`)
        result.summary = parts.length > 0 ? parts.join('\n') : '✅ Dữ liệu hợp lệ'

        return result
    }

    /**
     * Xử lý 1 dòng Excel → ProcessedRecord
     */
    function processRow(row: Record<string, unknown>, rowIndex: number = 0): ProcessedRecord {
        const errors: string[] = []
        const excelRow = rowIndex + 2

        // Họ tên
        let ho_ten: string
        const rawHoTen = row['hovaten']
        if (!rawHoTen || String(rawHoTen).trim() === '') {
            ho_ten = `[LỖI: Thiếu họ tên - Dòng ${excelRow}]`
            errors.push('Thiếu họ tên')
        } else {
            ho_ten = String(rawHoTen).trim()
            if (ho_ten.length > MAX_FIELD_LENGTH) {
                errors.push(`Họ tên quá dài (${ho_ten.length} ký tự)`)
                ho_ten = ho_ten.substring(0, MAX_FIELD_LENGTH - 3) + '...'
            }
        }

        // Pháp danh
        let phap_danh = ''
        const rawPD = row['phapdanh']
        if (rawPD && String(rawPD).trim() !== '') {
            phap_danh = String(rawPD).trim()
            if (phap_danh.length > MAX_FIELD_LENGTH) {
                errors.push(`Pháp danh quá dài (${phap_danh.length} ký tự)`)
                phap_danh = phap_danh.substring(0, MAX_FIELD_LENGTH - 3) + '...'
            }
        }

        // Năm sinh
        let sinh_nam = ''
        const rawNS = row['namsinh']
        if (rawNS !== undefined && rawNS !== null && String(rawNS).trim() !== '') {
            let nsStr = String(rawNS).trim()
            // Xử lý float: "1990.0" → "1990"
            if (nsStr.includes('.')) nsStr = nsStr.split('.')[0]
            if (/^\d{4}$/.test(nsStr)) {
                sinh_nam = nsStr
            } else {
                errors.push(`Năm sinh không hợp lệ: '${rawNS}'`)
                sinh_nam = `[${nsStr}?]`
            }
        }

        // Địa chỉ
        let dia_chi = ''
        const rawDC = row['diachithuongtru_short']
        if (rawDC && String(rawDC).trim() !== '') {
            dia_chi = String(rawDC).trim()
            if (dia_chi.length > MAX_ADDR_LENGTH) {
                errors.push(`Địa chỉ quá dài (${dia_chi.length} ký tự)`)
                dia_chi = dia_chi.substring(0, MAX_ADDR_LENGTH - 3) + '...'
            }
        }

        return {
            phap_danh,
            ho_ten,
            sinh_nam,
            dia_chi,
            _has_error: errors.length > 0,
            _error_details: errors,
            _row_index: excelRow
        }
    }

    /**
     * Xử lý toàn bộ danh sách
     */
    function processAll(data: Record<string, unknown>[]): {
        dataList: ProcessedRecord[]
        errorCount: number
        errorSummary: string | null
    } {
        const dataList: ProcessedRecord[] = []
        let errorCount = 0
        const errorRows: { row: number; errors: string[] }[] = []

        data.forEach((row, idx) => {
            const processed = processRow(row, idx)
            dataList.push(processed)
            if (processed._has_error) {
                errorCount++
                errorRows.push({ row: processed._row_index, errors: processed._error_details })
            }
        })

        let errorSummary: string | null = null
        if (errorCount > 0) {
            const lines = [`⚠️ ${errorCount} dòng có vấn đề:\n`]
            errorRows.slice(0, 10).forEach(err => {
                lines.push(`• Dòng ${err.row}: ${err.errors.join('; ')}`)
            })
            if (errorRows.length > 10) lines.push(`... và ${errorRows.length - 10} dòng khác`)
            errorSummary = lines.join('\n')
        }

        return { dataList, errorCount, errorSummary }
    }

    /** Dữ liệu demo khi chưa có Excel */
    function getDemoData(): ProcessedRecord[] {
        return [
            { phap_danh: 'Tâm Minh', ho_ten: 'Nguyễn Văn An', sinh_nam: '1990', dia_chi: 'P.10, Q.Gò Vấp, TP.HCM', _has_error: false, _error_details: [], _row_index: 2 },
            { phap_danh: 'Diệu Hạnh', ho_ten: 'Trần Thị Bình', sinh_nam: '1985', dia_chi: 'TT.Đức Phổ, Quảng Ngãi', _has_error: false, _error_details: [], _row_index: 3 },
            { phap_danh: 'Thiện Tâm', ho_ten: 'Lê Văn Cường', sinh_nam: '2001', dia_chi: 'X.An Phú, H.Củ Chi, TP.HCM', _has_error: false, _error_details: [], _row_index: 4 }
        ]
    }

    return {
        readExcelFile,
        validateExcel,
        processRow,
        processAll,
        getDemoData
    }
}
