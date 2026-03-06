# -*- coding: utf-8 -*-
"""
Module chuyển đổi Dương lịch sang Âm lịch
Sử dụng thuật toán chuyển đổi lịch Việt Nam
"""

import datetime

class LunarConverter:
    """Chuyển đổi Dương lịch sang Âm lịch"""
    
    # Mapping năm âm lịch sang Can Chi (2015-2040)
    CAN_CHI_MAP = {
        2015: "Ất Mùi",
        2016: "Bính Thân",
        2017: "Đinh Dậu",
        2018: "Mậu Tuất",
        2019: "Kỷ Hợi",
        2020: "Canh Tý",
        2021: "Tân Sửu",
        2022: "Nhâm Dần",
        2023: "Quý Mão",
        2024: "Giáp Thìn",
        2025: "Ất Tỵ",
        2026: "Bính Ngọ",
        2027: "Đinh Mùi",
        2028: "Mậu Thân",
        2029: "Kỷ Dậu",
        2030: "Canh Tuất",
        2031: "Tân Hợi",
        2032: "Nhâm Tý",
        2033: "Quý Sửu",
        2034: "Giáp Dần",
        2035: "Ất Mão",
        2036: "Bính Thìn",
        2037: "Đinh Tỵ",
        2038: "Mậu Ngọ",
        2039: "Kỷ Mùi",
        2040: "Canh Thân"
    }
    
    # Can (Thiên Can - 10 chữ)
    CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
    
    # Chi (Địa Chi - 12 con giáp)
    CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
    
    @staticmethod
    def get_can_chi(year):
        """
        Tính Can Chi cho một năm bất kỳ
        
        Args:
            year: Năm cần tính (số nguyên)
            
        Returns:
            str: Tên Can Chi (ví dụ: "Ất Tỵ")
        """
        # Nếu có trong map sẵn thì dùng
        if year in LunarConverter.CAN_CHI_MAP:
            return LunarConverter.CAN_CHI_MAP[year]
        
        # Tính toán cho các năm khác
        # Năm 1984 là Giáp Tý (Can = 0, Chi = 0)
        can_index = (year - 4) % 10
        chi_index = (year - 4) % 12
        
        return f"{LunarConverter.CAN[can_index]} {LunarConverter.CHI[chi_index]}"
    
    @staticmethod
    def jd_from_date(dd, mm, yy):
        """Tính Julian day number từ ngày dương lịch"""
        a = (14 - mm) // 12
        y = yy + 4800 - a
        m = mm + 12 * a - 3
        jd = dd + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        return jd
    
    @staticmethod
    def get_new_moon_day(k, timezone=7):
        """Tính ngày trăng non (sóc) thứ k kể từ năm 1900"""
        import math
        T = k / 1236.85
        T2 = T * T
        T3 = T2 * T
        dr = 3.14159265358979323846 / 180
        Jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * T2 - 0.000000155 * T3
        Jd1 = Jd1 + 0.00033 * math.cos((166.56 + 132.87 * T - 0.009173 * T2) * dr)
        M = 359.2242 + 29.10535608 * k - 0.0000333 * T2 - 0.00000347 * T3
        Mpr = 306.0253 + 385.81691806 * k + 0.0107306 * T2 + 0.00001236 * T3
        F = 21.2964 + 390.67050646 * k - 0.0016528 * T2 - 0.00000239 * T3
        C1 = (0.1734 - 0.000393 * T) * math.sin(M * dr)
        C1 = C1 + 0.0021 * math.sin(2 * dr * M)
        C1 = C1 - 0.4068 * math.sin(Mpr * dr)
        C1 = C1 + 0.0161 * math.sin(2 * dr * Mpr)
        C1 = C1 - 0.0004 * math.sin(3 * dr * Mpr)
        C1 = C1 + 0.0104 * math.sin(2 * dr * F)
        C1 = C1 - 0.0051 * math.sin((M + Mpr) * dr)
        C1 = C1 - 0.0074 * math.sin((M - Mpr) * dr)
        C1 = C1 + 0.0004 * math.sin((2 * F + M) * dr)
        C1 = C1 - 0.0004 * math.sin((2 * F - M) * dr)
        C1 = C1 - 0.0006 * math.sin((2 * F + Mpr) * dr)
        C1 = C1 + 0.0010 * math.sin((2 * F - Mpr) * dr)
        C1 = C1 + 0.0005 * math.sin((2 * Mpr + M) * dr)
        deltaT = 0
        if T < -11:
            deltaT = 0.001 + 0.000839 * T + 0.0002261 * T2 - 0.00000845 * T3 - 0.000000081 * T * T3
        else:
            deltaT = -0.000278 + 0.000265 * T + 0.000262 * T2
        JdNew = Jd1 + C1 - deltaT
        return int(JdNew + 0.5 + timezone / 24.0)
    
    @staticmethod
    def get_lunar_month_11(yy, timezone=7):
        """Tìm ngày bắt đầu tháng 11 âm lịch"""
        off = LunarConverter.jd_from_date(31, 12, yy) - 2415021
        k = int(off / 29.530588853)
        nm = LunarConverter.get_new_moon_day(k, timezone)
        sunLong = LunarConverter.get_sun_longitude(nm, timezone)
        if sunLong >= 9:
            nm = LunarConverter.get_new_moon_day(k - 1, timezone)
        return nm
    
    @staticmethod
    def get_sun_longitude(jdn, timezone=7):
        """Tính kinh độ mặt trời"""
        import math
        T = (jdn - 2451545.5 - timezone / 24.0) / 36525
        T2 = T * T
        dr = 3.14159265358979323846 / 180
        M = 357.52910 + 35999.05030 * T - 0.0001559 * T2 - 0.00000048 * T * T2
        L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T2
        DL = (1.914600 - 0.004817 * T - 0.000014 * T2) * math.sin(dr * M)
        DL = DL + (0.019993 - 0.000101 * T) * math.sin(dr * 2 * M) + 0.000290 * math.sin(dr * 3 * M)
        L = L0 + DL
        L = L * dr
        L = L - 3.14159265358979323846 * 2 * int(L / (3.14159265358979323846 * 2))
        return int(L / 3.14159265358979323846 * 6)
    
    @staticmethod
    def get_leap_month_offset(a11, timezone=7):
        """Tính tháng nhuận"""
        k = int((a11 - 2415021.076998695) / 29.530588853 + 0.5)
        last = 0
        i = 1
        arc = LunarConverter.get_sun_longitude(LunarConverter.get_new_moon_day(k + i, timezone), timezone)
        while arc != last and i < 14:
            last = arc
            i += 1
            arc = LunarConverter.get_sun_longitude(LunarConverter.get_new_moon_day(k + i, timezone), timezone)
        return i - 1
    
    @staticmethod
    def solar_to_lunar(dd, mm, yy, timezone=7):
        """
        Chuyển đổi ngày dương lịch sang âm lịch
        
        Args:
            dd: ngày (1-31)
            mm: tháng (1-12)
            yy: năm
            timezone: múi giờ (mặc định 7 cho Việt Nam)
            
        Returns:
            tuple: (ngày_âm, tháng_âm, năm_âm, leap_month)
        """
        dayNumber = LunarConverter.jd_from_date(dd, mm, yy)
        k = int((dayNumber - 2415021.076998695) / 29.530588853)
        monthStart = LunarConverter.get_new_moon_day(k + 1, timezone)
        
        if monthStart > dayNumber:
            monthStart = LunarConverter.get_new_moon_day(k, timezone)
        
        a11 = LunarConverter.get_lunar_month_11(yy, timezone)
        b11 = a11
        if a11 >= monthStart:
            lunarYear = yy
            a11 = LunarConverter.get_lunar_month_11(yy - 1, timezone)
        else:
            lunarYear = yy + 1
            b11 = LunarConverter.get_lunar_month_11(yy + 1, timezone)
        
        lunarDay = dayNumber - monthStart + 1
        diff = int((monthStart - a11) / 29)
        lunarLeap = 0
        lunarMonth = diff + 11
        
        if b11 - a11 > 365:
            leapMonthDiff = LunarConverter.get_leap_month_offset(a11, timezone)
            if diff >= leapMonthDiff:
                lunarMonth = diff + 10
                if diff == leapMonthDiff:
                    lunarLeap = 1
        
        if lunarMonth > 12:
            lunarMonth = lunarMonth - 12
        if lunarMonth >= 11 and diff < 4:
            lunarYear -= 1
        
        return (int(lunarDay), int(lunarMonth), int(lunarYear), int(lunarLeap))
    
    @staticmethod
    def convert_date(date_str):
        """
        Chuyển đổi chuỗi ngày dương lịch sang âm lịch
        
        Args:
            date_str: chuỗi ngày dạng "YYYY-MM-DD" hoặc datetime object
            
        Returns:
            dict: {
                'solar_day': int,
                'solar_month': int,
                'solar_year': int,
                'lunar_day': int,
                'lunar_month': int,
                'lunar_year': int,
                'buddhist_year': int
            }
        """
        if isinstance(date_str, str):
            # Parse string date
            if ' ' in date_str:
                date_str = date_str.split(' ')[0]
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        else:
            date_obj = date_str
        
        solar_day = date_obj.day
        solar_month = date_obj.month
        solar_year = date_obj.year
        
        # Chuyển sang âm lịch
        lunar_day, lunar_month, lunar_year, leap = LunarConverter.solar_to_lunar(
            solar_day, solar_month, solar_year
        )
        
        # Phật lịch = năm dương lịch + 544
        buddhist_year = solar_year + 544
        
        # Lấy tên Can Chi cho năm âm lịch
        lunar_year_name = LunarConverter.get_can_chi(lunar_year)
        
        return {
            'solar_day': solar_day,
            'solar_month': solar_month,
            'solar_year': solar_year,
            'lunar_day': lunar_day,
            'lunar_month': lunar_month,
            'lunar_year': lunar_year,
            'lunar_year_name': lunar_year_name,  # Tên Can Chi
            'buddhist_year': buddhist_year
        }

# Test
if __name__ == "__main__":
    # Test với một số ngày
    test_dates = [
        "2025-05-02",
        "2025-12-15",
        "2024-01-01"
    ]
    
    for date in test_dates:
        result = LunarConverter.convert_date(date)
        print(f"Dương lịch: {result['solar_day']}/{result['solar_month']}/{result['solar_year']}")
        print(f"Âm lịch: {result['lunar_day']}/{result['lunar_month']} năm {result['lunar_year_name']}")
        print(f"Phật lịch: {result['buddhist_year']}")
        print("-" * 40)

