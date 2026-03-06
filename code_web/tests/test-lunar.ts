/**
 * Test Lunar Converter đầy đủ
 * Chạy: npx tsx tests/test-lunar.ts
 */

// ===== PORT LOGIC (copy from composable for standalone test) =====
const CAN = ['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý']
const CHI = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi']

function getCanChi(year: number): string {
    const canIndex = ((year - 4) % 10 + 10) % 10
    const chiIndex = ((year - 4) % 12 + 12) % 12
    return `${CAN[canIndex]} ${CHI[chiIndex]}`
}

function jdFromDate(dd: number, mm: number, yy: number): number {
    const a = Math.trunc((14 - mm) / 12)
    const y = yy + 4800 - a
    const m = mm + 12 * a - 3
    return dd + Math.trunc((153 * m + 2) / 5) + 365 * y + Math.trunc(y / 4) - Math.trunc(y / 100) + Math.trunc(y / 400) - 32045
}

function getNewMoonDay(k: number, timezone: number = 7): number {
    const T = k / 1236.85; const T2 = T * T; const T3 = T2 * T; const dr = Math.PI / 180
    let Jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * T2 - 0.000000155 * T3
    Jd1 = Jd1 + 0.00033 * Math.cos((166.56 + 132.87 * T - 0.009173 * T2) * dr)
    const M = 359.2242 + 29.10535608 * k - 0.0000333 * T2 - 0.00000347 * T3
    const Mpr = 306.0253 + 385.81691806 * k + 0.0107306 * T2 + 0.00001236 * T3
    const F = 21.2964 + 390.67050646 * k - 0.0016528 * T2 - 0.00000239 * T3
    let C1 = (0.1734 - 0.000393 * T) * Math.sin(M * dr)
    C1 += 0.0021 * Math.sin(2 * dr * M)
    C1 -= 0.4068 * Math.sin(Mpr * dr)
    C1 += 0.0161 * Math.sin(2 * dr * Mpr)
    C1 -= 0.0004 * Math.sin(3 * dr * Mpr)
    C1 += 0.0104 * Math.sin(2 * dr * F)
    C1 -= 0.0051 * Math.sin((M + Mpr) * dr)
    C1 -= 0.0074 * Math.sin((M - Mpr) * dr)
    C1 += 0.0004 * Math.sin((2 * F + M) * dr)
    C1 -= 0.0004 * Math.sin((2 * F - M) * dr)
    C1 -= 0.0006 * Math.sin((2 * F + Mpr) * dr)
    C1 += 0.0010 * Math.sin((2 * F - Mpr) * dr)
    C1 += 0.0005 * Math.sin((2 * Mpr + M) * dr)
    let deltaT: number
    if (T < -11) { deltaT = 0.001 + 0.000839 * T + 0.0002261 * T2 - 0.00000845 * T3 - 0.000000081 * T * T3 }
    else { deltaT = -0.000278 + 0.000265 * T + 0.000262 * T2 }
    return Math.trunc(Jd1 + C1 - deltaT + 0.5 + timezone / 24.0)
}

function getSunLongitude(jdn: number, timezone: number = 7): number {
    const T = (jdn - 2451545.5 - timezone / 24.0) / 36525; const T2 = T * T; const dr = Math.PI / 180
    const M = 357.52910 + 35999.05030 * T - 0.0001559 * T2 - 0.00000048 * T * T2
    const L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T2
    let DL = (1.914600 - 0.004817 * T - 0.000014 * T2) * Math.sin(dr * M)
    DL += (0.019993 - 0.000101 * T) * Math.sin(dr * 2 * M) + 0.000290 * Math.sin(dr * 3 * M)
    let L = (L0 + DL) * dr
    L = L - Math.PI * 2 * Math.trunc(L / (Math.PI * 2))
    return Math.trunc(L / Math.PI * 6)
}

function getLunarMonth11(yy: number, timezone: number = 7): number {
    const off = jdFromDate(31, 12, yy) - 2415021
    const k = Math.trunc(off / 29.530588853)
    let nm = getNewMoonDay(k, timezone)
    if (getSunLongitude(nm, timezone) >= 9) nm = getNewMoonDay(k - 1, timezone)
    return nm
}

function getLeapMonthOffset(a11: number, timezone: number = 7): number {
    const k = Math.trunc((a11 - 2415021.076998695) / 29.530588853 + 0.5)
    let last = 0; let i = 1
    let arc = getSunLongitude(getNewMoonDay(k + i, timezone), timezone)
    while (arc !== last && i < 14) { last = arc; i++; arc = getSunLongitude(getNewMoonDay(k + i, timezone), timezone) }
    return i - 1
}

function solarToLunar(dd: number, mm: number, yy: number, timezone: number = 7): [number, number, number, number] {
    const dayNumber = jdFromDate(dd, mm, yy)
    const k = Math.trunc((dayNumber - 2415021.076998695) / 29.530588853)
    let monthStart = getNewMoonDay(k + 1, timezone)
    if (monthStart > dayNumber) monthStart = getNewMoonDay(k, timezone)
    let a11 = getLunarMonth11(yy, timezone); let b11 = a11; let lunarYear: number
    if (a11 >= monthStart) { lunarYear = yy; a11 = getLunarMonth11(yy - 1, timezone) }
    else { lunarYear = yy + 1; b11 = getLunarMonth11(yy + 1, timezone) }
    const lunarDay = dayNumber - monthStart + 1
    const diff = Math.trunc((monthStart - a11) / 29)
    let lunarLeap = 0; let lunarMonth = diff + 11
    if (b11 - a11 > 365) {
        const leapMonthDiff = getLeapMonthOffset(a11, timezone)
        if (diff >= leapMonthDiff) { lunarMonth = diff + 10; if (diff === leapMonthDiff) lunarLeap = 1 }
    }
    if (lunarMonth > 12) lunarMonth -= 12
    if (lunarMonth >= 11 && diff < 4) lunarYear -= 1
    return [lunarDay, lunarMonth, lunarYear, lunarLeap]
}

function convertDate(dateStr: string) {
    const parts = dateStr.split('-')
    const solarYear = parseInt(parts[0]), solarMonth = parseInt(parts[1]), solarDay = parseInt(parts[2])
    const [lunarDay, lunarMonth, lunarYear] = solarToLunar(solarDay, solarMonth, solarYear)
    return {
        solar_day: solarDay, solar_month: solarMonth, solar_year: solarYear,
        lunar_day: lunarDay, lunar_month: lunarMonth, lunar_year: lunarYear,
        lunar_year_name: getCanChi(lunarYear), buddhist_year: solarYear + 544
    }
}

// ===== RUN TESTS =====
let passed = 0, failed = 0

function assert(condition: boolean, message: string, detail?: string) {
    if (condition) { passed++; console.log(`  ✅ ${message}`) }
    else { failed++; console.log(`  ❌ ${message}${detail ? ` (${detail})` : ''}`) }
}

function assertDate(input: string, expectedLunarDay: number, expectedLunarMonth: number, expectedLunarYear: number, expectedCanChi: string) {
    const result = convertDate(input)
    const ok = result.lunar_day === expectedLunarDay && result.lunar_month === expectedLunarMonth && result.lunar_year === expectedLunarYear && result.lunar_year_name === expectedCanChi
    assert(ok, `${input} → ${expectedLunarDay}/${expectedLunarMonth}/${expectedLunarYear} (${expectedCanChi})`,
        ok ? undefined : `Got: ${result.lunar_day}/${result.lunar_month}/${result.lunar_year} (${result.lunar_year_name})`)
}

console.log('\n===== TEST LUNAR CONVERTER =====')

// Test cases đã biết (verified with Python version)
assertDate('2025-01-01', 2, 12, 2024, 'Giáp Thìn')  // 1/1/2025 = 2/12/Giáp Thìn
assertDate('2025-01-29', 1, 1, 2025, 'Ất Tỵ')        // Tết Nguyên Đán 2025 = 1/1/Ất Tỵ
assertDate('2025-05-02', 5, 4, 2025, 'Ất Tỵ')        // Lễ Phật Đản 2025
assertDate('2025-12-16', 27, 10, 2025, 'Ất Tỵ')      // Ngày test từ đặc tả

console.log('\n===== TEST BUDDHIST YEAR =====')
assert(convertDate('2025-01-01').buddhist_year === 2569, 'PL 2025 = 2569')
assert(convertDate('2024-01-01').buddhist_year === 2568, 'PL 2024 = 2568')

console.log('\n===== TEST CAN CHI =====')
assert(getCanChi(2024) === 'Giáp Thìn', '2024 = Giáp Thìn')
assert(getCanChi(2025) === 'Ất Tỵ', '2025 = Ất Tỵ')
assert(getCanChi(2026) === 'Bính Ngọ', '2026 = Bính Ngọ')
assert(getCanChi(2027) === 'Đinh Mùi', '2027 = Đinh Mùi')
assert(getCanChi(2028) === 'Mậu Thân', '2028 = Mậu Thân')
assert(getCanChi(2029) === 'Kỷ Dậu', '2029 = Kỷ Dậu')
assert(getCanChi(2030) === 'Canh Tuất', '2030 = Canh Tuất')

console.log('\n===== TEST DATE WITH TIME =====')
// "2025-12-16 19:00:07" → lấy "2025-12-16"
const dateWithTimeSplit = "2025-12-16 19:00:07".split(' ')[0]
const r = convertDate(dateWithTimeSplit)
assert(r.lunar_day === 27, 'Date with time: lunar_day = 27')

console.log(`\n===== KẾT QUẢ: ${passed} passed, ${failed} failed =====\n`)
process.exit(failed > 0 ? 1 : 0)
