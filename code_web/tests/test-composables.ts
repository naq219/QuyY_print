/**
 * Test script cho các composables
 * Chạy: npx tsx tests/test-composables.ts
 */

// ===== TEST LUNAR CONVERTER =====
// Port trực tiếp logic, không dùng composable wrapper

const CAN = ['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý']
const CHI = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi']

function getCanChi(year: number): string {
    const canIndex = ((year - 4) % 10 + 10) % 10
    const chiIndex = ((year - 4) % 12 + 12) % 12
    return `${CAN[canIndex]} ${CHI[chiIndex]}`
}

// ===== DATA PROCESSOR TESTS =====
const MAX_FIELD_LENGTH = 50
const MAX_ADDR_LENGTH = 100

function processRow(row: Record<string, unknown>, rowIndex: number = 0) {
    const errors: string[] = []
    const excelRow = rowIndex + 2

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

    let phap_danh = ''
    const rawPD = row['phapdanh']
    if (rawPD && String(rawPD).trim() !== '') {
        phap_danh = String(rawPD).trim()
    }

    let sinh_nam = ''
    const rawNS = row['namsinh']
    if (rawNS !== undefined && rawNS !== null && String(rawNS).trim() !== '') {
        let nsStr = String(rawNS).trim()
        if (nsStr.includes('.')) nsStr = nsStr.split('.')[0]
        if (/^\d{4}$/.test(nsStr)) {
            sinh_nam = nsStr
        } else {
            errors.push(`Năm sinh không hợp lệ: '${rawNS}'`)
            sinh_nam = `[${nsStr}?]`
        }
    }

    let dia_chi = ''
    const rawDC = row['diachithuongtru_short']
    if (rawDC && String(rawDC).trim() !== '') {
        dia_chi = String(rawDC).trim()
    }

    return { phap_danh, ho_ten, sinh_nam, dia_chi, _has_error: errors.length > 0, _error_details: errors, _row_index: excelRow }
}

// ===== RUN TESTS =====
let passed = 0
let failed = 0

function assert(condition: boolean, message: string) {
    if (condition) {
        passed++
        console.log(`  ✅ ${message}`)
    } else {
        failed++
        console.log(`  ❌ ${message}`)
    }
}

console.log('\n===== TEST CAN CHI =====')
assert(getCanChi(2025) === 'Ất Tỵ', 'Năm 2025 = Ất Tỵ')
assert(getCanChi(2024) === 'Giáp Thìn', 'Năm 2024 = Giáp Thìn')
assert(getCanChi(2026) === 'Bính Ngọ', 'Năm 2026 = Bính Ngọ')
assert(getCanChi(2020) === 'Canh Tý', 'Năm 2020 = Canh Tý')
assert(getCanChi(1984) === 'Giáp Tý', 'Năm 1984 = Giáp Tý')

console.log('\n===== TEST BUDDHIST YEAR =====')
assert(2025 + 544 === 2569, '2025 + 544 = 2569')
assert(2024 + 544 === 2568, '2024 + 544 = 2568')

console.log('\n===== TEST DATA PROCESSOR - processRow =====')

// Test 1: Dữ liệu bình thường
const row1 = processRow({ hovaten: 'Nguyễn Văn An', phapdanh: 'Tâm Minh', namsinh: '1990', diachithuongtru_short: 'TP.HCM' }, 0)
assert(row1.ho_ten === 'Nguyễn Văn An', 'Họ tên bình thường')
assert(row1.phap_danh === 'Tâm Minh', 'Pháp danh bình thường')
assert(row1.sinh_nam === '1990', 'Năm sinh bình thường')
assert(row1._has_error === false, 'Không có lỗi')

// Test 2: Họ tên rỗng
const row2 = processRow({ hovaten: '', phapdanh: '', namsinh: '1990' }, 0)
assert(row2.ho_ten.includes('LỖI'), 'Họ tên rỗng → hiện lỗi')
assert(row2._has_error === true, 'Có lỗi khi thiếu họ tên')

// Test 3: Năm sinh float
const row3 = processRow({ hovaten: 'Test', namsinh: '1990.0' }, 0)
assert(row3.sinh_nam === '1990', 'Năm sinh float "1990.0" → "1990"')

// Test 4: Năm sinh không hợp lệ
const row4 = processRow({ hovaten: 'Test', namsinh: 'abc' }, 0)
assert(row4.sinh_nam === '[abc?]', 'Năm sinh không hợp lệ → "[abc?]"')
assert(row4._has_error === true, 'Đánh dấu lỗi')

// Test 5: Null values
const row5 = processRow({ hovaten: 'Test' }, 0)
assert(row5.phap_danh === '', 'Pháp danh null → ""')
assert(row5.sinh_nam === '', 'Năm sinh undefined → ""')
assert(row5.dia_chi === '', 'Địa chỉ undefined → ""')

// Test 6: Trim whitespace
const row6 = processRow({ hovaten: '  Nguyễn Văn An  ', phapdanh: '  Tâm Minh  ' }, 0)
assert(row6.ho_ten === 'Nguyễn Văn An', 'Trim họ tên')
assert(row6.phap_danh === 'Tâm Minh', 'Trim pháp danh')

// Test 7: Row index
const row7 = processRow({ hovaten: 'Test' }, 5)
assert(row7._row_index === 7, 'Row index: row 5 → Excel dòng 7 (5+2)')

console.log(`\n===== KẾT QUẢ: ${passed} passed, ${failed} failed =====\n`)
process.exit(failed > 0 ? 1 : 0)
