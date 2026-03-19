from flask import Flask, render_template, request, jsonify, send_from_directory
import swisseph as swe
from datetime import datetime, timedelta
import pytz
import json
import os

app = Flask(__name__)

# పంచాంగ మూలకాల పేర్లు
TITHIS = [
    'Prathama', 'Dvitiya', 'Tritiya', 'Chaturthi', 'Panchami', 
    'Shashthi', 'Saptami', 'Ashtami', 'Navami', 'Dashami', 
    'Ekadashi', 'Dvadashi', 'Trayodashi', 'Chaturdashi'
]
LUNAR_MONTHS = [
    "Chaitra", "Vaisakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", 
    "Ashwayuja", "Kartika", "Margashirsha", "Pushya", "Magha", "Phalguna"
]
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Arudra', 
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni', 
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha', 
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 
    'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]
YOGAS = [
    'Vishkambha', 'Priti', 'Ayushman', 'Saubhagya', 'Shobhana', 'Atiganda', 'Sukarma', 'Dhriti', 'Shula', 'Ganda', 'Vriddhi', 'Dhruva', 'Vyaghata', 'Harshana', 'Vajra', 'Siddhi', 'Vyatipata', 'Variyan', 'Parigha', 'Shiva', 'Siddha', 'Sadhya', 'Shubha', 'Shukla', 'Brahma', 'Indra', 'Vaidhriti'
]
KARANAS_MOVING = ['Bava', 'Balava', 'Kaulava', 'Taitila', 'Gara', 'Vanija', 'Vishti']
TARA_NAMES = {1: 'Janma', 2: 'Sampat', 3: 'Vipat', 4: 'Kshema', 5: 'Pratyak', 6: 'Sadhana', 7: 'Naidhana', 8: 'Mitra', 0: 'Parama Mitra'}
RASI_NAMES = ['Mesha', 'Vrishabha', 'Mithuna', 'Karka', 'Simha', 'Kanya', 'Tula', 'Vrischika', 'Dhanu', 'Makara', 'Kumbha', 'Meena']
VISHA_GHATIS = [50, 24, 30, 40, 14, 21, 30, 20, 32, 30, 20, 18, 21, 20, 14, 14, 10, 14, 56, 24, 20, 10, 10, 18, 16, 24, 30]
NAK_TO_RASI = {
    0: [0], 1: [0], 2: [0, 1], 3: [1], 4: [1, 2], 5: [2], 6: [2, 3], 7: [3], 8: [3],
    9: [4], 10: [4], 11: [4, 5], 12: [5], 13: [5, 6], 14: [6], 15: [6, 7], 16: [7], 17: [7],
    18: [8], 19: [8], 20: [8, 9], 21: [9], 22: [9, 10], 23: [10], 24: [10, 11], 25: [11], 26: [11]
}

EXPORT_COLUMNS = [
    'Priority', 'Date', 'Vaara', 'Asthg', 'Maasa', 'Tithi', 'Sunrise', 
    'Nakshatra', 'Moon Rasi', 'Yoga', 'Karana', 'Rahu Kalam', 
    'Yamagandam', 'Durmuhurtham', 'Varjyam', 'Boy Tarabalam', 
    'Boy Chandra Balam', 'Girl Tarabalam', 'Girl Chandra Balam', 'Muhurtha_Notes'
]

MUHURTHA_UI_COLUMNS = [
    'Priority', 'Date', 'Vaara', 'Asthg', 'Maasa', 'Tithi', 'Sunrise', 
    'Nakshatra', 'Moon Rasi', 'Yoga', 'Karana', 'Rahu Kalam', 
    'Yamagandam', 'Durmuhurtham', 'Varjyam', 'Boy Tarabalam', 
    'Boy Chandra Balam', 'Girl Tarabalam', 'Girl Chandra Balam', 'Muhurtha_Notes'
]

PANCHANGA_COLUMNS = [
    'Date', 'Vaara', 'Asthg', 'Maasa', 'Tithi', 'Tithi End', 'Sunrise', 
    'Nakshatra', 'Nakshatra End', 'Moon Rasi', 'Yoga', 'Yoga End', 
    'Karana', 'Karana End', 'Rahu Kalam', 'Yamagandam', 'Durmuhurtham', 'Varjyam',
    'Boy Tarabalam', 'Boy Chandra Balam', 'Girl Tarabalam', 'Girl Chandra Balam'
]

PREFS_FILE = 'preferences.json'

AMSHA_NADI_CACHE = None
def get_amsha_nadi_dict():
    global AMSHA_NADI_CACHE
    if AMSHA_NADI_CACHE is None:
        filepath = os.path.join(app.root_path, 'static', 'amsha_nadi.json')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    AMSHA_NADI_CACHE = json.load(f)
                except json.JSONDecodeError:
                    AMSHA_NADI_CACHE = {}
        else:
            AMSHA_NADI_CACHE = {}
    return AMSHA_NADI_CACHE

def load_preferences():
    default_prefs = {"tithi": [], "vaara": [], "nakshatra": [], "yoga": [], "karana": [], "tarabalam": [], "export_columns": EXPORT_COLUMNS, "panchanga_columns": PANCHANGA_COLUMNS, "muhurtha_ui_columns": MUHURTHA_UI_COLUMNS, "default_location": "Bengaluru, Karnataka", "default_lat": 12.9716, "default_lon": 77.5946, "default_tz": 5.5, "default_days": 10, "default_profile_name": "Panchanga", "default_ayanamsa": "Lahiri", "pdf_language": "en", "pdf_header_font": "", "pdf_body_font": ""}
    if os.path.exists(PREFS_FILE):
        with open(PREFS_FILE, 'r') as f:
            try:
                saved_prefs = json.load(f)
                default_prefs.update(saved_prefs)
            except json.JSONDecodeError:
                pass
    return default_prefs

def save_preferences(data):
    with open(PREFS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def find_end_jd(jd_start, element_type, target_val):
    low = jd_start
    high = jd_start + 1.5 # పంచాంగ అంశాలు గరిష్టంగా 1.5 రోజుల్లో ముగుస్తాయి
    for _ in range(40):
        mid = (low + high) / 2
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        sun = swe.calc_ut(mid, swe.SUN, flags)[0][0]
        moon = swe.calc_ut(mid, swe.MOON, flags)[0][0]
        
        if element_type in ['tithi', 'karana']:
            val = (moon - sun) % 360
        elif element_type == 'nakshatra':
            val = moon % 360
        elif element_type == 'yoga':
            val = (moon + sun) % 360
            
        diff = (val - target_val) % 360
        if diff > 180: low = mid
        else: high = mid
    return mid

def format_end_time(jd_end, base_dt_local, target_tz):
    unix_ts = (jd_end - 2440587.5) * 86400
    end_dt_local = datetime.fromtimestamp(unix_ts, tz=pytz.UTC).astimezone(target_tz)
    day_diff = (end_dt_local.date() - base_dt_local.date()).days
    time_str = end_dt_local.strftime('%I:%M %p')
    if day_diff > 0:
        return f"+{time_str}"
    return time_str

def get_amavasya(jd_start, direction=1):
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun = swe.calc_ut(jd_start, swe.SUN, flags)[0][0]
    moon = swe.calc_ut(jd_start, swe.MOON, flags)[0][0]
    tithi_val = (moon - sun) % 360
    
    if direction == 1:
        est_jd = jd_start + (360 - tithi_val) / 12.190749
    else:
        est_jd = jd_start - tithi_val / 12.190749
        
    low = est_jd - 1.5
    high = est_jd + 1.5
    for _ in range(35):
        mid = (low + high) / 2
        s = swe.calc_ut(mid, swe.SUN, flags)[0][0]
        m = swe.calc_ut(mid, swe.MOON, flags)[0][0]
        ang = (m - s) % 360
        if ang > 180:
            low = mid
        else:
            high = mid
    return mid

def get_lunar_month_name(jd):
    amav1 = get_amavasya(jd, -1)
    amav2 = get_amavasya(jd, 1)
    amav0 = get_amavasya(amav1 - 2, -1) # నిజ మాసాన్ని చెక్ చేయడానికి క్రితం అమావాస్య
    
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun_rasi_0 = int(swe.calc_ut(amav0, swe.SUN, flags)[0][0] / 30)
    sun_rasi_1 = int(swe.calc_ut(amav1, swe.SUN, flags)[0][0] / 30)
    sun_rasi_2 = int(swe.calc_ut(amav2, swe.SUN, flags)[0][0] / 30)
    
    if sun_rasi_1 == sun_rasi_2:
        return f"Adhi-{LUNAR_MONTHS[(sun_rasi_2 + 1) % 12]}"
    else:
        prefix = "Nija-" if sun_rasi_0 == sun_rasi_1 else ""
        return f"{prefix}{LUNAR_MONTHS[sun_rasi_2]}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/panchanga')
def panchanga_page():
    return render_template('panchanga.html')

@app.route('/match')
def match_page():
    return render_template('match.html')

@app.route('/jataka')
def jataka_page():
    return render_template('jataka.html')

@app.route('/logo.png')
def serve_logo():
    return send_from_directory(app.root_path, 'logo.png')

@app.route('/settings')
def settings():
    all_tithis = [f"S-{t}" for t in TITHIS] + ['Purnima'] + [f"K-{t}" for t in TITHIS] + ['Amavasya']
    all_karanas = KARANAS_MOVING + ["Kimstughna", "Shakuni", "Chatushpada", "Naga"]
    vaaras = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    prefs = load_preferences()
    return render_template('settings.html', 
                           tithis=all_tithis, 
                           nakshatras=NAKSHATRAS, 
                           yogas=YOGAS, 
                           karanas=all_karanas, 
                           taras=list(TARA_NAMES.values()),
                           vaaras=vaaras,
                           maasas=LUNAR_MONTHS + ["Adhika"],
                           export_columns=EXPORT_COLUMNS,
                           panchanga_columns=PANCHANGA_COLUMNS,
                           muhurtha_ui_columns=MUHURTHA_UI_COLUMNS,
                           prefs=prefs)

@app.route('/api/chart', methods=['POST'])
def get_chart():
    data = request.json
    date_str = data.get('date')
    time_str = data.get('time', '06:00')
    lat = float(data.get('lat', 0))
    lon = float(data.get('lon', 0))
    tz_val = float(data.get('tz', 5.5))

    target_tz = pytz.FixedOffset(int(tz_val * 60))
    try:
        local_dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
    except ValueError:
        local_dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
    local_dt = target_tz.localize(local_dt)
    utc_dt = local_dt.astimezone(pytz.UTC)

    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
    
    prefs = load_preferences()
    ayanamsa = prefs.get('default_ayanamsa', 'Lahiri')
    ayanamsa_map = {"Lahiri": swe.SIDM_LAHIRI, "Raman": swe.SIDM_RAMAN, "KP": swe.SIDM_KRISHNAMURTI}
    swe.set_sid_mode(ayanamsa_map.get(ayanamsa, swe.SIDM_LAHIRI))
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    planets = { 'Su': swe.SUN, 'Ch': swe.MOON, 'Ku': swe.MARS, 'Bu': swe.MERCURY, 'Gu': swe.JUPITER, 'Sk': swe.VENUS, 'Sa': swe.SATURN }
    chart_data = {i: [] for i in range(12)}
    chart_data_d9 = {i: [] for i in range(12)}

    sun_pos = swe.calc_ut(jd, swe.SUN, flags)[0][0]

    for p_name, p_id in planets.items():
        res = swe.calc_ut(jd, p_id, flags | swe.FLG_SPEED)
        pos = res[0][0]
        speed = res[0][3]
        
        is_r = False
        is_c = False
        
        if p_id not in [swe.SUN, swe.MOON]:
            if speed < 0:
                is_r = True
            diff = min(abs(pos - sun_pos) % 360, 360 - (abs(pos - sun_pos) % 360))
            if p_id == swe.MARS and diff <= 17: is_c = True
            elif p_id == swe.MERCURY and diff <= (12 if is_r else 14): is_c = True
            elif p_id == swe.JUPITER and diff <= 11: is_c = True
            elif p_id == swe.VENUS and diff <= (8 if is_r else 10): is_c = True
            elif p_id == swe.SATURN and diff <= 15: is_c = True
                
        p_obj = {'id': p_name, 'isR': is_r, 'isC': is_c}
        chart_data[int(pos / 30)].append(p_obj)
        chart_data_d9[int((pos * 9) / 30) % 12].append(p_obj)

    # Rahu & Ketu
    rahu_pos = swe.calc_ut(jd, swe.MEAN_NODE, flags)[0][0]
    rahu_obj = {'id': 'Ra', 'isR': False, 'isC': False}
    chart_data[int(rahu_pos / 30)].append(rahu_obj)
    chart_data_d9[int((rahu_pos * 9) / 30) % 12].append(rahu_obj)
    
    ketu_pos = (rahu_pos + 180) % 360
    ketu_obj = {'id': 'Ke', 'isR': False, 'isC': False}
    chart_data[int(ketu_pos / 30)].append(ketu_obj)
    chart_data_d9[int((ketu_pos * 9) / 30) % 12].append(ketu_obj)

    # Ascendant (Lagna) - 'Lg'
    res_houses = swe.houses_ex(jd, lat, lon, b'P', flags)
    asc = res_houses[1][0]
    asc_rasi = int(asc / 30)
    lg_obj = {'id': 'Lg', 'isR': False, 'isC': False}
    chart_data[asc_rasi].append(lg_obj)
    chart_data_d9[int((asc * 9) / 30) % 12].append(lg_obj)

    asc_deg_in_rasi = asc % 30
    deg = int(asc_deg_in_rasi)
    mins = int((asc_deg_in_rasi - deg) * 60)
    formatted_deg = f"{deg}°{mins:02d}'"
    remaining_percent = int(((30 - asc_deg_in_rasi) / 30) * 100)

    # --- Mid Lagna (+/- 24 mins) Calculation ---
    def get_lagna_boundary(start_jd, end_jd, target_rasi, is_start):
        low, high = start_jd, end_jd
        for _ in range(25):
            mid = (low + high) / 2
            mid_asc = swe.houses_ex(mid, lat, lon, b'P', flags)[1][0]
            if int(mid_asc / 30) == target_rasi:
                if is_start: high = mid
                else: low = mid
            else:
                if is_start: low = mid
                else: high = mid
        return (low + high) / 2

    start_lagna_jd = get_lagna_boundary(jd - 0.25, jd, asc_rasi, True)
    end_lagna_jd = get_lagna_boundary(jd, jd + 0.25, asc_rasi, False)
    
    midpoint_jd = (start_lagna_jd + end_lagna_jd) / 2
    window_start_jd = midpoint_jd - (24.0 / 1440.0)
    window_end_jd = midpoint_jd + (24.0 / 1440.0)

    def get_local_time_str(jd_val):
        unix_ts = (jd_val - 2440587.5) * 86400
        dt_local = datetime.fromtimestamp(unix_ts, tz=pytz.UTC).astimezone(target_tz)
        return dt_local.strftime('%I:%M %p')

    mid_lagna_window = f"{get_local_time_str(window_start_jd)} - {get_local_time_str(window_end_jd)}"

    # --- Panchaka Rahitam Calculation ---
    sun_pos_c = swe.calc_ut(jd, swe.SUN, flags)[0][0]
    moon_pos_c = swe.calc_ut(jd, swe.MOON, flags)[0][0]
    
    tithi_num = int(((moon_pos_c - sun_pos_c) % 360) / 12) + 1
    nak_num = int(moon_pos_c / (360.0/27.0)) + 1
    lagna_num = asc_rasi + 1
    
    # ఖచ్చితమైన హిందూ వారం (సూర్యోదయం ముందు ఉంటే క్రితం రోజు)
    local_midnight = local_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    utc_midnight = local_midnight.astimezone(pytz.UTC)
    jd_mid = swe.julday(utc_midnight.year, utc_midnight.month, utc_midnight.day, utc_midnight.hour + utc_midnight.minute/60.0 + utc_midnight.second/3600.0)
    res_rise = swe.rise_trans(jd_mid, swe.SUN, rsmi=swe.CALC_RISE, geopos=(lon, lat, 0.0))
    jd_sunrise_chart = res_rise[0] if isinstance(res_rise[0], float) else res_rise[1][0]
    
    wd = local_dt.weekday() # 0=Mon, 6=Sun
    if jd < jd_sunrise_chart:
        wd = (wd - 1) % 7
    hindu_wd = (wd + 1) % 7 + 1 # 1=Sun, 2=Mon... 7=Sat
    
    total_sum = tithi_num + nak_num + lagna_num + hindu_wd
    rem = total_sum % 9
    
    panchaka_map = {
        1: ("Mrityu (Bad)", False), 2: ("Agni (Bad)", False), 4: ("Raja (Bad)", False),
        6: ("Chora (Bad)", False), 8: ("Roga (Bad)", False),
        3: ("Shubham (Good)", True), 5: ("Shubham (Good)", True), 7: ("Shubham (Good)", True), 0: ("Shubham (Good)", True)
    }
    p_name, p_good = panchaka_map[rem]
    panchaka_str = f"{p_name} [Total:{total_sum}]"

    return jsonify({'chart': chart_data, 'chart_d9': chart_data_d9, 'lagna_deg': formatted_deg, 'lagna_rem_pct': remaining_percent, 'mid_lagna_window': mid_lagna_window, 'panchaka': panchaka_str, 'panchaka_is_good': p_good})

@app.route('/api/lagnas', methods=['POST'])
def get_lagnas():
    data = request.json
    date_str = data.get('date')
    lat = float(data.get('lat', 0))
    lon = float(data.get('lon', 0))
    tz_val = float(data.get('tz', 5.5))

    target_tz = pytz.FixedOffset(int(tz_val * 60))
    
    try:
        local_dt = datetime.strptime(f"{date_str} 00:00", '%Y-%m-%d %H:%M')
    except ValueError:
        return jsonify([])

    local_dt = target_tz.localize(local_dt)
    utc_dt = local_dt.astimezone(pytz.UTC)
    jd_midnight = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
    
    res_rise = swe.rise_trans(jd_midnight, swe.SUN, rsmi=swe.CALC_RISE, geopos=(lon, lat, 0.0))
    jd_sunrise = res_rise[0] if isinstance(res_rise[0], float) else res_rise[1][0]
    
    prefs = load_preferences()
    ayanamsa = prefs.get('default_ayanamsa', 'Lahiri')
    ayanamsa_map = {"Lahiri": swe.SIDM_LAHIRI, "Raman": swe.SIDM_RAMAN, "KP": swe.SIDM_KRISHNAMURTI}
    swe.set_sid_mode(ayanamsa_map.get(ayanamsa, swe.SIDM_LAHIRI))
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    lagnas = []
    current_jd = jd_sunrise

    for _ in range(14):
        res = swe.houses_ex(current_jd, lat, lon, b'P', flags)
        asc = res[1][0]
        current_rasi = int(asc / 30)
        target_asc = ((current_rasi + 1) * 30) % 360
        
        low_jd, high_jd = current_jd, current_jd + 0.15 # Max approx 3.6 hours for a lagna
        
        for _ in range(25): # Binary search for transition boundary
            mid_jd = (low_jd + high_jd) / 2
            mid_asc = swe.houses_ex(mid_jd, lat, lon, b'P', flags)[1][0]
            
            diff = (mid_asc - asc) % 360
            target_diff = (target_asc - asc) % 360
            if target_diff == 0: target_diff = 30
            
            if diff < target_diff: low_jd = mid_jd
            else: high_jd = mid_jd
                
        transition_jd = (low_jd + high_jd) / 2
        lagnas.append({'rasi': RASI_NAMES[current_rasi], 'end_time': format_end_time(transition_jd, local_dt, target_tz)})
        
        current_jd = transition_jd + 0.001
        if current_jd > jd_sunrise + 1.0: break # Stop after 24 hrs

    return jsonify(lagnas)

@app.route('/api/preferences', methods=['GET', 'POST'])
def api_preferences():
    if request.method == 'POST':
        data = request.json
        save_preferences(data)
        return jsonify({"status": "success", "message": "Preferences saved successfully!"})
    return jsonify(load_preferences())

@app.route('/api/fonts/<lang>')
def get_fonts(lang):
    lang_dir_map = {'en': 'ENG', 'te': 'TEL', 'kn': 'KAN', 'sa': 'SAN'}
    folder = lang_dir_map.get(lang, 'ENG')
    font_dir = os.path.join(app.root_path, 'static', 'fonts', folder)
    fonts = []
    if os.path.exists(font_dir):
        fonts = [f for f in os.listdir(font_dir) if f.lower().endswith('.ttf') or f.lower().endswith('.otf')]
    return jsonify(fonts)

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        start_date_str = data['date'] # YYYY-MM-DD ఫార్మాట్‌లో రావాలి
        lat = float(data['lat'])
        lon = float(data['lon'])
        tz_val = float(data['tz']) 
        num_days = int(data.get('days', 1)) # డిఫాల్ట్‌గా 1 రోజు
        boy_nak_name = data.get('boy_nakshatra')
        girl_nak_name = data.get('girl_nakshatra')
    except (KeyError, ValueError, TypeError) as e:
        return jsonify({'error': f'Invalid input data: {str(e)}'}), 400
    
    prefs = load_preferences()
    ayanamsa = prefs.get('default_ayanamsa', 'Lahiri')
    ayanamsa_map = {"Lahiri": swe.SIDM_LAHIRI, "Raman": swe.SIDM_RAMAN, "KP": swe.SIDM_KRISHNAMURTI}
    swe.set_sid_mode(ayanamsa_map.get(ayanamsa, swe.SIDM_LAHIRI))
    
    offset_minutes = int(tz_val * 60)
    target_tz = pytz.FixedOffset(offset_minutes)
    start_date_local = datetime.strptime(start_date_str, '%Y-%m-%d')
    
    results = []

    for i in range(num_days):
        current_local_date = start_date_local + timedelta(days=i)
        
        # ఆ రోజు స్థానిక సమయం అర్ధరాత్రి 00:00 ని UTC కి మార్చడం
        local_midnight = target_tz.localize(current_local_date)
        utc_midnight = local_midnight.astimezone(pytz.UTC)
        jd_midnight = swe.julday(utc_midnight.year, utc_midnight.month, utc_midnight.day, utc_midnight.hour + utc_midnight.minute/60.0 + utc_midnight.second/3600.0)
        
        # సూర్యోదయ సమయ లెక్కింపు (Rise Trans)
        res = swe.rise_trans(jd_midnight, swe.SUN, rsmi=swe.CALC_RISE, geopos=(lon, lat, 0.0))
        jd_sunrise = res[0] if isinstance(res[0], float) else res[1][0]
        
        # సూర్యోదయాన్ని లోకల్ టైమ్‌కి కన్వర్ట్ చేయడం
        unix_ts_sunrise = (jd_sunrise - 2440587.5) * 86400
        sunrise_dt_utc = datetime.fromtimestamp(unix_ts_sunrise, tz=pytz.UTC)
        sunrise_dt_local = sunrise_dt_utc.astimezone(target_tz)

        # సూర్యాస్తమయ సమయ లెక్కింపు (Set Trans)
        res_set = swe.rise_trans(jd_midnight, swe.SUN, rsmi=swe.CALC_SET, geopos=(lon, lat, 0.0))
        jd_sunset = res_set[0] if isinstance(res_set[0], float) else res_set[1][0]
        
        # సూర్యాస్తమయాన్ని లోకల్ టైమ్‌కి కన్వర్ట్ చేయడం
        unix_ts_sunset = (jd_sunset - 2440587.5) * 86400
        sunset_dt_utc = datetime.fromtimestamp(unix_ts_sunset, tz=pytz.UTC)
        sunset_dt_local = sunset_dt_utc.astimezone(target_tz)

        # --- రాహు కాలం లెక్కింపు (Rahu Kalam Calculation) ---
        # పగటి సమయాన్ని 8 భాగాలుగా విభజించడం
        day_duration = sunset_dt_local - sunrise_dt_local
        segment_duration = day_duration / 8
        
        # వారాన్ని బట్టి సెగ్మెంట్ నంబర్: Python weekday() -> 0=Mon, 1=Tue, ..., 6=Sun
        rahu_segment_map = {6: 8, 0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3}
        segment_number = rahu_segment_map[sunrise_dt_local.weekday()]
        
        rahu_start_dt = sunrise_dt_local + (segment_duration * (segment_number - 1))
        rahu_end_dt = rahu_start_dt + segment_duration
        rahu_kalam_str = f"{rahu_start_dt.strftime('%I:%M %p')} - {rahu_end_dt.strftime('%I:%M %p')}"

        # --- Yamagandam Calculation ---
        yama_segment_map = {6: 5, 0: 4, 1: 3, 2: 2, 3: 1, 4: 7, 5: 6}
        y_segment_number = yama_segment_map[sunrise_dt_local.weekday()]
        yama_start_dt = sunrise_dt_local + (segment_duration * (y_segment_number - 1))
        yama_end_dt = yama_start_dt + segment_duration
        yamagandam_str = f"{yama_start_dt.strftime('%I:%M %p')} - {yama_end_dt.strftime('%I:%M %p')}"

        # --- Durmuhurtham Calculation ---
        muhurtha_duration = day_duration / 15
        wd = sunrise_dt_local.weekday()
        dur_segments = {6: [14], 0: [9, 12], 1: [4, 11], 2: [6], 3: [12, 13], 4: [4, 8], 5: [2]}
        dur_times = []
        for seg in dur_segments[wd]:
            d_start = sunrise_dt_local + (muhurtha_duration * (seg - 1))
            d_end = d_start + muhurtha_duration
            dur_times.append(f"{d_start.strftime('%I:%M %p')} - {d_end.strftime('%I:%M %p')}")
        durmuhurtham_str = ", ".join(dur_times)
        
        # సూర్యోదయం సమయంలో గ్రహాల స్థితులు (Planetary Positions at Sunrise)
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        sun_pos = swe.calc_ut(jd_sunrise, swe.SUN, flags)[0][0]
        moon_pos = swe.calc_ut(jd_sunrise, swe.MOON, flags)[0][0]
        moon_rasi_idx = int(moon_pos / 30)
        
        # --- Asthangatha (Combustion) Calculation ---
        ven_pos = swe.calc_ut(jd_sunrise, swe.VENUS, flags)[0][0]
        jup_pos = swe.calc_ut(jd_sunrise, swe.JUPITER, flags)[0][0]
        
        diff_ven = min(abs(ven_pos - sun_pos) % 360, 360 - (abs(ven_pos - sun_pos) % 360))
        diff_jup = min(abs(jup_pos - sun_pos) % 360, 360 - (abs(jup_pos - sun_pos) % 360))
        
        combust_labels = []
        if diff_ven <= 10: combust_labels.append("Sk")
        if diff_jup <= 11: combust_labels.append("Gu")
        asthangatha_str = "-".join(combust_labels) if combust_labels else "-"
        
        # --- Maasa Auspicious Check ---
        maasa_name = get_lunar_month_name(jd_sunrise)
        if maasa_name.startswith("Adhi-"):
            base_m = maasa_name.replace("Adhi-", "")
            maasa_is_good = ("Adhika" in prefs.get('maasa', [])) and (base_m in prefs.get('maasa', []))
        elif maasa_name.startswith("Nija-"):
            base_m = maasa_name.replace("Nija-", "")
            maasa_is_good = base_m in prefs.get('maasa', [])
        else:
            maasa_is_good = maasa_name in prefs.get('maasa', [])
        
        # 1. తిథి (Tithi)
        tithi_val = (moon_pos - sun_pos) % 360
        tithi_idx = int(tithi_val / 12)
        paksha = "Shukla" if tithi_idx < 15 else "Krishna"
        tithi_name = "Purnima" if tithi_idx == 14 else "Amavasya" if tithi_idx == 29 else TITHIS[tithi_idx % 15]
        
        if tithi_idx == 14:
            pref_tithi = "Purnima"
        elif tithi_idx == 29:
            pref_tithi = "Amavasya"
        else:
            pref_tithi = f"S-{tithi_name}" if tithi_idx < 15 else f"K-{tithi_name}"
        target_tithi_val = ((tithi_idx + 1) * 12) % 360
        jd_tithi_end = find_end_jd(jd_sunrise, 'tithi', target_tithi_val)
        tithi_end_str = format_end_time(jd_tithi_end, sunrise_dt_local, target_tz)
        
        # 2. నక్షత్రం (Nakshatra)
        nak_val = moon_pos % 360
        nak_idx = int(nak_val / (360.0/27.0))
        target_nak_val = ((nak_idx + 1) * (360.0/27.0)) % 360
        jd_nak_end = find_end_jd(jd_sunrise, 'nakshatra', target_nak_val)
        nak_end_str = format_end_time(jd_nak_end, sunrise_dt_local, target_tz)
        
        # --- Varjyam (Visha Nadi) Calculation ---
        jd_nak_start = find_end_jd(jd_sunrise - 1.5, 'nakshatra', nak_idx * (360.0/27.0))
        duration_nak1 = jd_nak_end - jd_nak_start
        v_start_jd1 = jd_nak_start + (VISHA_GHATIS[nak_idx] / 60.0) * duration_nak1
        v_end_jd1 = v_start_jd1 + (4.0 / 60.0) * duration_nak1
        
        nak_idx2 = (nak_idx + 1) % 27
        jd_nak_end2 = find_end_jd(jd_nak_end, 'nakshatra', ((nak_idx2 + 1) * (360.0/27.0)) % 360)
        duration_nak2 = jd_nak_end2 - jd_nak_end
        v_start_jd2 = jd_nak_end + (VISHA_GHATIS[nak_idx2] / 60.0) * duration_nak2
        v_end_jd2 = v_start_jd2 + (4.0 / 60.0) * duration_nak2
        
        varjyam_list = []
        def format_v_time(js, je):
            ts_s = (js - 2440587.5) * 86400
            dt_s = datetime.fromtimestamp(ts_s, tz=pytz.UTC).astimezone(target_tz)
            ts_e = (je - 2440587.5) * 86400
            dt_e = datetime.fromtimestamp(ts_e, tz=pytz.UTC).astimezone(target_tz)
            d1 = f"+{dt_s.strftime('%I:%M %p')}" if dt_s.date() > sunrise_dt_local.date() else dt_s.strftime('%I:%M %p')
            d2 = f"+{dt_e.strftime('%I:%M %p')}" if dt_e.date() > sunrise_dt_local.date() else dt_e.strftime('%I:%M %p')
            return f"{d1} - {d2}"

        if jd_sunrise - 0.2 < v_start_jd1 < jd_sunrise + 1.2:
            varjyam_list.append(format_v_time(v_start_jd1, v_end_jd1))
        if jd_sunrise - 0.2 < v_start_jd2 < jd_sunrise + 1.2:
            varjyam_list.append(format_v_time(v_start_jd2, v_end_jd2))
            
        varjyam_str = ", ".join(varjyam_list) if varjyam_list else "-"
        
        # 3. యోగం (Yoga)
        yoga_val = (moon_pos + sun_pos) % 360
        yoga_idx = int(yoga_val / (360.0/27.0))
        target_yoga_val = ((yoga_idx + 1) * (360.0/27.0)) % 360
        jd_yoga_end = find_end_jd(jd_sunrise, 'yoga', target_yoga_val)
        yoga_end_str = format_end_time(jd_yoga_end, sunrise_dt_local, target_tz)
        
        # 4. కరణం (Karana)
        karana_idx = int(tithi_val / 6)
        if karana_idx == 0: karana_name = "Kimstughna"
        elif karana_idx == 57: karana_name = "Shakuni"
        elif karana_idx == 58: karana_name = "Chatushpada"
        elif karana_idx == 59: karana_name = "Naga"
        else: karana_name = KARANAS_MOVING[(karana_idx - 1) % 7]
        target_karana_val = ((karana_idx + 1) * 6) % 360
        jd_karana_end = find_end_jd(jd_sunrise, 'karana', target_karana_val)
        karana_end_str = format_end_time(jd_karana_end, sunrise_dt_local, target_tz)
            
        res_dict = {
            'Date': current_local_date.strftime('%d-%b-%Y'),
            'Asthg': asthangatha_str,
            'Vaara': sunrise_dt_local.strftime('%A'),
            'Vaara_is_good': sunrise_dt_local.strftime('%A') in prefs.get('vaara', []),
            'Sunrise': sunrise_dt_local.strftime('%I:%M:%S %p'),
            'Maasa': maasa_name,
            'Maasa_is_good': maasa_is_good,
            'Tithi': f"{paksha} {tithi_name}",
            'Tithi_is_good': pref_tithi in prefs.get('tithi', []),
            'Tithi End': tithi_end_str,
            'Nakshatra': NAKSHATRAS[nak_idx],
            'Nakshatra_is_good': NAKSHATRAS[nak_idx] in prefs.get('nakshatra', []),
            'Nakshatra End': nak_end_str,
            'Moon Rasi': RASI_NAMES[moon_rasi_idx],
            'Yoga': YOGAS[yoga_idx],
            'Yoga_is_good': YOGAS[yoga_idx] in prefs.get('yoga', []),
            'Yoga End': yoga_end_str,
            'Karana': karana_name,
            'Karana_is_good': karana_name in prefs.get('karana', []),
            'Karana End': karana_end_str,
            'Rahu Kalam': rahu_kalam_str,
            'Yamagandam': yamagandam_str,
            'Durmuhurtham': durmuhurtham_str,
            'Varjyam': varjyam_str
        }
        
        if boy_nak_name in NAKSHATRAS:
            boy_nak_idx = NAKSHATRAS.index(boy_nak_name)
            dist = (nak_idx - boy_nak_idx + 27) % 27 + 1
            tara = TARA_NAMES[dist % 9]
            res_dict['Boy Tarabalam'] = tara
            res_dict['Boy_Tarabalam_is_good'] = tara in prefs.get('tarabalam', [])
            
            is_ashtama = any(moon_rasi_idx == (jr + 7) % 12 for jr in NAK_TO_RASI[boy_nak_idx])
            res_dict['Boy Chandra Balam'] = "Ashtama" if is_ashtama else "Good"
            res_dict['Boy_Chandra_Balam_is_good'] = not is_ashtama
            
        if girl_nak_name in NAKSHATRAS:
            girl_nak_idx = NAKSHATRAS.index(girl_nak_name)
            dist = (nak_idx - girl_nak_idx + 27) % 27 + 1
            tara = TARA_NAMES[dist % 9]
            res_dict['Girl Tarabalam'] = tara
            res_dict['Girl_Tarabalam_is_good'] = tara in prefs.get('tarabalam', [])
            
            is_ashtama = any(moon_rasi_idx == (jr + 7) % 12 for jr in NAK_TO_RASI[girl_nak_idx])
            res_dict['Girl Chandra Balam'] = "Ashtama" if is_ashtama else "Good"
            res_dict['Girl_Chandra_Balam_is_good'] = not is_ashtama
            
        results.append(res_dict)

    return jsonify(results)

@app.route('/api/match', methods=['POST'])
def api_match():
    data = request.json
    prefs = load_preferences()
    ayanamsa = prefs.get('default_ayanamsa', 'Lahiri')
    ayanamsa_map = {"Lahiri": swe.SIDM_LAHIRI, "Raman": swe.SIDM_RAMAN, "KP": swe.SIDM_KRISHNAMURTI}
    
    def get_person_info(person):
        tz_val = float(person.get('tz', 5.5))
        lat = float(person.get('lat', 0))
        lon = float(person.get('lon', 0))
        target_tz = pytz.FixedOffset(int(tz_val * 60))
        try:
            local_dt = datetime.strptime(f"{person['date']} {person['time']}", '%Y-%m-%d %H:%M:%S')
        except ValueError:
            local_dt = datetime.strptime(f"{person['date']} {person['time']}", '%Y-%m-%d %H:%M')
        
        local_dt = target_tz.localize(local_dt)
        utc_dt = local_dt.astimezone(pytz.UTC)
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
        
        swe.set_sid_mode(ayanamsa_map.get(ayanamsa, swe.SIDM_LAHIRI))
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
        
        chart_data = {i: [] for i in range(12)}
        chart_data_d9 = {i: [] for i in range(12)}
        longitudes = {}
        
        def format_lon(pos):
            deg = int(pos % 30)
            mins = int(((pos % 30) - deg) * 60)
            return f"{deg:02d}°{mins:02d}'"

        sun_pos = swe.calc_ut(jd, swe.SUN, flags)[0][0]

        planets = { 'Su': swe.SUN, 'Ch': swe.MOON, 'Ku': swe.MARS, 'Bu': swe.MERCURY, 'Gu': swe.JUPITER, 'Sk': swe.VENUS, 'Sa': swe.SATURN }
        for p_name, p_id in planets.items():
            res = swe.calc_ut(jd, p_id, flags)
            pos = res[0][0]
            speed = res[0][3]
            
            is_r = False
            is_c = False
            
            if p_id not in [swe.SUN, swe.MOON]:
                if speed < 0:
                    is_r = True
                    
                diff = min(abs(pos - sun_pos) % 360, 360 - (abs(pos - sun_pos) % 360))
                if p_id == swe.MARS and diff <= 17:
                    is_c = True
                elif p_id == swe.MERCURY and diff <= (12 if is_r else 14):
                    is_c = True
                elif p_id == swe.JUPITER and diff <= 11:
                    is_c = True
                elif p_id == swe.VENUS and diff <= (8 if is_r else 10):
                    is_c = True
                elif p_id == swe.SATURN and diff <= 15:
                    is_c = True
                    
            p_obj = {'id': p_name, 'isR': is_r, 'isC': is_c}
            chart_data[int(pos / 30)].append(p_obj)
            chart_data_d9[int((pos * 9) / 30) % 12].append(p_obj)
            longitudes[p_name] = {'lon': format_lon(pos), 'isR': is_r, 'isC': is_c}
            if p_id == swe.MOON:
                moon_pos = pos
                
        rahu_pos = swe.calc_ut(jd, swe.MEAN_NODE, flags)[0][0]
        rahu_obj = {'id': 'Ra', 'isR': False, 'isC': False}
        chart_data[int(rahu_pos / 30)].append(rahu_obj)
        chart_data_d9[int((rahu_pos * 9) / 30) % 12].append(rahu_obj)
        longitudes['Ra'] = {'lon': format_lon(rahu_pos), 'isR': False, 'isC': False}
        
        ketu_pos = (rahu_pos + 180) % 360
        ketu_obj = {'id': 'Ke', 'isR': False, 'isC': False}
        chart_data[int(ketu_pos / 30)].append(ketu_obj)
        chart_data_d9[int((ketu_pos * 9) / 30) % 12].append(ketu_obj)
        longitudes['Ke'] = {'lon': format_lon(ketu_pos), 'isR': False, 'isC': False}
        
        asc = swe.houses_ex(jd, lat, lon, b'P', flags)[1][0]
        lg_obj = {'id': 'Lg', 'isR': False, 'isC': False}
        chart_data[int(asc / 30)].append(lg_obj)
        chart_data_d9[int((asc * 9) / 30) % 12].append(lg_obj)
        longitudes['Lg'] = {'lon': format_lon(asc), 'isR': False, 'isC': False}
        
        nak_idx = int((moon_pos % 360) / (360.0/27.0))
        rasi_idx = int((moon_pos % 360) / 30)
        d9_rasi_idx = int((moon_pos * 9) / 30) % 12
        pada = int((moon_pos / (360.0/108.0)) % 4) + 1
        
        return {'chart': chart_data, 'chart_d9': chart_data_d9, 'longitudes': longitudes, 'nak': nak_idx, 'rasi': rasi_idx, 'd9_rasi': d9_rasi_idx, 'pada': pada, 'nak_name': NAKSHATRAS[nak_idx], 'rasi_name': RASI_NAMES[rasi_idx]}

    try:
        b_info = get_person_info(data['boy'])
        g_info = get_person_info(data['girl'])
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    b_rasi, g_rasi = b_info['rasi'], g_info['rasi']
    b_nak, g_nak = b_info['nak'], g_info['nak']

    # 1. Varna (1 Point)
    varna_map = [3, 2, 1, 4, 3, 2, 1, 4, 3, 2, 1, 4] # 1:Shudra, 2:Vaishya, 3:Kshatriya, 4:Brahmin
    varna_names = ["", "Shudra", "Vaishya", "Kshatriya", "Brahmin"]
    b_varna, g_varna = varna_map[b_rasi], varna_map[g_rasi]
    varna_score = 1 if b_varna >= g_varna else 0

    # 2. Vashya (2 Points)
    vashya_map = [0, 0, 1, 2, 3, 1, 1, 4, 0, 2, 1, 2] # 0:Chatushpada, 1:Manav, 2:Jalachar, 3:Vanchar, 4:Keeta
    vashya_names = ["Chatushpada", "Manav", "Jalachar", "Vanchar", "Keeta"]
    vashya_scores = { (0,0):2, (0,1):1, (0,2):1, (0,3):0, (0,4):1, (1,0):1, (1,1):2, (1,2):1, (1,3):0, (1,4):1, (2,0):1, (2,1):1, (2,2):2, (2,3):1, (2,4):1, (3,0):0, (3,1):0, (3,2):1, (3,3):2, (3,4):0, (4,0):1, (4,1):1, (4,2):1, (4,3):0, (4,4):2 }
    b_vashya, g_vashya = vashya_map[b_rasi], vashya_map[g_rasi]
    vashya_score = vashya_scores.get((b_vashya, g_vashya), 0)

    # 3. Tara (3 Points)
    b_tara = (g_nak - b_nak + 27) % 9 + 1
    g_tara = (b_nak - g_nak + 27) % 9 + 1
    tara_score = (1.5 if b_tara in [1,2,4,6,8,9] else 0) + (1.5 if g_tara in [1,2,4,6,8,9] else 0)

    # 4. Yoni (4 Points)
    yoni_map = [0, 1, 2, 3, 4, 5, 5, 2, 3, 6, 6, 7, 7, 8, 8, 9, 10, 10, 4, 11, 12, 11, 13, 0, 13, 7, 1]
    yoni_names = ["Ashwa", "Gaja", "Aja", "Sarpa", "Shwana", "Marjala", "Mushika", "Gau", "Mahisha", "Vyaghra", "Mriga", "Vanara", "Nakula", "Simha"]
    b_yoni, g_yoni = yoni_map[b_nak], yoni_map[g_nak]
    yoni_enemies = [{0,8}, {1,13}, {2,11}, {3,12}, {4,10}, {5,6}, {7,9}]
    if b_yoni == g_yoni: yoni_score = 4
    elif any({b_yoni, g_yoni} == e for e in yoni_enemies): yoni_score = 0
    else: yoni_score = 2

    # 5. Graha Maitri (5 Points)
    rasi_lords = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4] # 0:Sun, 1:Moon, 2:Mar, 3:Mer, 4:Jup, 5:Ven, 6:Sat
    planet_names = ["Surya", "Chandra", "Kuja", "Budha", "Guru", "Shukra", "Shani"]
    b_lord, g_lord = rasi_lords[b_rasi], rasi_lords[g_rasi]
    def get_rel(p1, p2):
        if p1 == p2: return 2
        friends = { 0:[1,2,4], 1:[0,3], 2:[0,1,4], 3:[0,5], 4:[0,1,2], 5:[3,6], 6:[3,5] }
        enemies = { 0:[5,6], 1:[], 2:[3], 3:[1], 4:[3,5], 5:[0,1], 6:[0,1,2] }
        return 2 if p2 in friends[p1] else 0 if p2 in enemies[p1] else 1
    b_rel, g_rel = get_rel(b_lord, g_lord), get_rel(g_lord, b_lord)
    maitri_score = {4:5, 3:4, 2:3, 1:1, 0:0}.get(b_rel + g_rel, 0)
    if (b_rel == 2 and g_rel == 0) or (b_rel == 0 and g_rel == 2): maitri_score = 2

    exceptions = []
    # Check Graha Maitri in D9 if D1 is poor (Score < 3)
    if maitri_score < 3:
        b_d9_lord, g_d9_lord = rasi_lords[b_info['d9_rasi']], rasi_lords[g_info['d9_rasi']]
        b_d9_rel, g_d9_rel = get_rel(b_d9_lord, g_d9_lord), get_rel(g_d9_lord, b_d9_lord)
        d9_maitri_score = {4:5, 3:4, 2:3, 1:1, 0:0}.get(b_d9_rel + g_d9_rel, 0)
        if (b_d9_rel == 2 and g_d9_rel == 0) or (b_d9_rel == 0 and g_d9_rel == 2): d9_maitri_score = 2
        
        if d9_maitri_score >= 3:
            exceptions.append(f"Graha Maitri matched in Navamsha chart ({planet_names[b_d9_lord]} - {planet_names[g_d9_lord]}).")

    # 6. Gana (6 Points)
    gana_map = [0, 1, 2, 1, 0, 1, 0, 0, 2, 2, 1, 1, 0, 2, 0, 2, 0, 2, 2, 1, 1, 0, 2, 2, 1, 1, 0]
    gana_names = ["Deva", "Manushya", "Rakshasa"]
    b_gana, g_gana = gana_map[b_nak], gana_map[g_nak]
    gana_matrix = { (0,0):6, (0,1):6, (0,2):1, (1,0):5, (1,1):6, (1,2):0, (2,0):0, (2,1):0, (2,2):6 }
    gana_score = gana_matrix.get((b_gana, g_gana), 0)

    # 7. Bhakoot (7 Points)
    dist = (g_rasi - b_rasi + 12) % 12 + 1
    bhakoot_score = 7 if dist in [1, 3, 4, 7, 10, 11] else 0

    # 8. Nadi (8 Points)
    nadi_map = [0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2]
    nadi_names = ["Aadi", "Madhya", "Antya"]
    b_nadi, g_nadi = nadi_map[b_nak], nadi_map[g_nak]
    nadi_score = 8 if b_nadi != g_nadi else 0

    if nadi_score == 0:
        amsha_nadi_dict = get_amsha_nadi_dict()
        b_amsha_key = f"{b_nak + 1}-{b_info['pada']}"
        g_amsha_key = f"{g_nak + 1}-{g_info['pada']}"
        b_amsha = amsha_nadi_dict.get(b_amsha_key)
        g_amsha = amsha_nadi_dict.get(g_amsha_key)
        if b_amsha and g_amsha and b_amsha.lower() != g_amsha.lower():
            exceptions.append(f"Amsha Nadi matched ({b_amsha} - {g_amsha})")

    koota_results = [
        {"name": "Nadi", "max": 8, "score": nadi_score, "boy": nadi_names[b_nadi], "girl": nadi_names[g_nadi]},
        {"name": "Bhakoot", "max": 7, "score": bhakoot_score, "boy": b_info['rasi_name'], "girl": g_info['rasi_name']},
        {"name": "Gana", "max": 6, "score": gana_score, "boy": gana_names[b_gana], "girl": gana_names[g_gana]},
        {"name": "Graha Maitri", "max": 5, "score": maitri_score, "boy": planet_names[b_lord], "girl": planet_names[g_lord]},
        {"name": "Yoni", "max": 4, "score": yoni_score, "boy": yoni_names[b_yoni], "girl": yoni_names[g_yoni]},
        {"name": "Tara", "max": 3, "score": tara_score, "boy": TARA_NAMES[b_tara % 9], "girl": TARA_NAMES[g_tara % 9]},
        {"name": "Vashya", "max": 2, "score": vashya_score, "boy": vashya_names[b_vashya], "girl": vashya_names[g_vashya]},
        {"name": "Varna", "max": 1, "score": varna_score, "boy": varna_names[b_varna], "girl": varna_names[g_varna]}
    ]

    total_score = sum(k['score'] for k in koota_results)

    return jsonify({
        "boy": { "chart": b_info['chart'], "chart_d9": b_info['chart_d9'], "longitudes": b_info['longitudes'], "nakshatra": b_info['nak_name'], "rasi": b_info['rasi_name'], "pada": b_info['pada'] },
        "girl": { "chart": g_info['chart'], "chart_d9": g_info['chart_d9'], "longitudes": g_info['longitudes'], "nakshatra": g_info['nak_name'], "rasi": g_info['rasi_name'], "pada": g_info['pada'] },
        "koota": koota_results,
        "total_score": total_score,
        "exceptions": exceptions
    })

@app.route('/api/jataka', methods=['POST'])
def api_jataka():
    try:
        data = request.json
        person = data.get('person')
        if not person:
            return jsonify({'error': 'No person data provided'}), 400
            
        prefs = load_preferences()
        ayanamsa = prefs.get('default_ayanamsa', 'Lahiri')
        ayanamsa_map = {"Lahiri": swe.SIDM_LAHIRI, "Raman": swe.SIDM_RAMAN, "KP": swe.SIDM_KRISHNAMURTI}
        
        tz_val = float(person.get('tz', 5.5))
        lat = float(person.get('lat', 0))
        lon = float(person.get('lon', 0))
        target_tz = pytz.FixedOffset(int(tz_val * 60))
        
        try:
            local_dt = datetime.strptime(f"{person['date']} {person['time']}", '%Y-%m-%d %H:%M:%S')
        except ValueError:
            local_dt = datetime.strptime(f"{person['date']} {person['time']}", '%Y-%m-%d %H:%M')
        
        local_dt = target_tz.localize(local_dt)
        utc_dt = local_dt.astimezone(pytz.UTC)
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
        
        swe.set_sid_mode(ayanamsa_map.get(ayanamsa, swe.SIDM_LAHIRI))
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
        
        chart_data = {i: [] for i in range(12)}
        chart_data_d9 = {i: [] for i in range(12)}
        chart_data_d3 = {i: [] for i in range(12)}
        chart_data_d7 = {i: [] for i in range(12)}
        chart_data_d10 = {i: [] for i in range(12)}
        chart_data_d12 = {i: [] for i in range(12)}
        rasi_positions = {}
        longitudes = {}
        
        def format_lon(pos):
            deg = int(pos % 30)
            mins = int(((pos % 30) - deg) * 60)
            return f"{deg:02d}°{mins:02d}'"

        def get_varga_rasi(pos, varga):
            rasi = int(pos / 30)
            deg_in_rasi = pos % 30
            if varga == 'D9':
                return int((pos * 9) / 30) % 12
            elif varga == 'D3': # Parashari Drekkana (1, 5, 9 logic)
                part = int(deg_in_rasi / 10.0)
                return (rasi + (part * 4)) % 12
            elif varga == 'D7': # Saptamsha (Odd starts from same, Even from 7th)
                part = int(deg_in_rasi / (30.0 / 7.0))
                if rasi % 2 == 0: return (rasi + part) % 12
                else: return (rasi + 6 + part) % 12
            elif varga == 'D10': # Dasamsha (Odd starts from same, Even from 9th)
                part = int(deg_in_rasi / 3.0)
                if rasi % 2 == 0: return (rasi + part) % 12
                else: return (rasi + 8 + part) % 12
            elif varga == 'D12': # Dwadashamsha (Continuous from same sign)
                part = int(deg_in_rasi / 2.5)
                return (rasi + part) % 12
            return rasi

        sun_pos = swe.calc_ut(jd, swe.SUN, flags)[0][0]

        planets = { 'Su': swe.SUN, 'Ch': swe.MOON, 'Ku': swe.MARS, 'Bu': swe.MERCURY, 'Gu': swe.JUPITER, 'Sk': swe.VENUS, 'Sa': swe.SATURN }
        for p_name, p_id in planets.items():
            res = swe.calc_ut(jd, p_id, flags)
            pos = res[0][0]
            rasi_positions[p_name] = int(pos / 30)
            speed = res[0][3]
            
            is_r = False
            is_c = False
            
            if p_id not in [swe.SUN, swe.MOON]:
                if speed < 0:
                    is_r = True
                diff = min(abs(pos - sun_pos) % 360, 360 - (abs(pos - sun_pos) % 360))
                if p_id == swe.MARS and diff <= 17:
                    is_c = True
                elif p_id == swe.MERCURY and diff <= (12 if is_r else 14):
                    is_c = True
                elif p_id == swe.JUPITER and diff <= 11:
                    is_c = True
                elif p_id == swe.VENUS and diff <= (8 if is_r else 10):
                    is_c = True
                elif p_id == swe.SATURN and diff <= 15:
                    is_c = True
                    
            p_obj = {'id': p_name, 'isR': is_r, 'isC': is_c}
            chart_data[int(pos / 30)].append(p_obj)
            chart_data_d9[get_varga_rasi(pos, 'D9')].append(p_obj)
            chart_data_d3[get_varga_rasi(pos, 'D3')].append(p_obj)
            chart_data_d7[get_varga_rasi(pos, 'D7')].append(p_obj)
            chart_data_d10[get_varga_rasi(pos, 'D10')].append(p_obj)
            chart_data_d12[get_varga_rasi(pos, 'D12')].append(p_obj)
            longitudes[p_name] = {'lon': format_lon(pos), 'isR': is_r, 'isC': is_c, 'deg': pos}
            if p_id == swe.MOON:
                moon_pos = pos
                
        rahu_pos = swe.calc_ut(jd, swe.MEAN_NODE, flags)[0][0]
        rahu_obj = {'id': 'Ra', 'isR': False, 'isC': False}
        chart_data[int(rahu_pos / 30)].append(rahu_obj)
        chart_data_d9[get_varga_rasi(rahu_pos, 'D9')].append(rahu_obj)
        chart_data_d3[get_varga_rasi(rahu_pos, 'D3')].append(rahu_obj)
        chart_data_d7[get_varga_rasi(rahu_pos, 'D7')].append(rahu_obj)
        chart_data_d10[get_varga_rasi(rahu_pos, 'D10')].append(rahu_obj)
        chart_data_d12[get_varga_rasi(rahu_pos, 'D12')].append(rahu_obj)
        longitudes['Ra'] = {'lon': format_lon(rahu_pos), 'isR': False, 'isC': False, 'deg': rahu_pos}
        
        ketu_pos = (rahu_pos + 180) % 360
        ketu_obj = {'id': 'Ke', 'isR': False, 'isC': False}
        chart_data[int(ketu_pos / 30)].append(ketu_obj)
        chart_data_d9[get_varga_rasi(ketu_pos, 'D9')].append(ketu_obj)
        chart_data_d3[get_varga_rasi(ketu_pos, 'D3')].append(ketu_obj)
        chart_data_d7[get_varga_rasi(ketu_pos, 'D7')].append(ketu_obj)
        chart_data_d10[get_varga_rasi(ketu_pos, 'D10')].append(ketu_obj)
        chart_data_d12[get_varga_rasi(ketu_pos, 'D12')].append(ketu_obj)
        longitudes['Ke'] = {'lon': format_lon(ketu_pos), 'isR': False, 'isC': False, 'deg': ketu_pos}
        
        asc = swe.houses_ex(jd, lat, lon, b'P', flags)[1][0]
        rasi_positions['Lg'] = int(asc / 30)
        lg_obj = {'id': 'Lg', 'isR': False, 'isC': False}
        chart_data[int(asc / 30)].append(lg_obj)
        chart_data_d9[get_varga_rasi(asc, 'D9')].append(lg_obj)
        chart_data_d3[get_varga_rasi(asc, 'D3')].append(lg_obj)
        chart_data_d7[get_varga_rasi(asc, 'D7')].append(lg_obj)
        chart_data_d10[get_varga_rasi(asc, 'D10')].append(lg_obj)
        chart_data_d12[get_varga_rasi(asc, 'D12')].append(lg_obj)
        longitudes['Lg'] = {'lon': format_lon(asc), 'isR': False, 'isC': False, 'deg': asc}
        
        nak_idx = int((moon_pos % 360) / (360.0/27.0))
        rasi_idx = int((moon_pos % 360) / 30)
        pada = int((moon_pos / (360.0/108.0)) % 4) + 1
        
        tithi_val = (moon_pos - sun_pos) % 360
        tithi_idx = int(tithi_val / 12)
        paksha = "Shukla" if tithi_idx < 15 else "Krishna"
        tithi_name = "Purnima" if tithi_idx == 14 else "Amavasya" if tithi_idx == 29 else TITHIS[tithi_idx % 15]

        yoga_val = (moon_pos + sun_pos) % 360
        yoga_idx = int(yoga_val / (360.0/27.0))
        
        karana_idx = int(tithi_val / 6)
        if karana_idx == 0: karana_name = "Kimstughna"
        elif karana_idx == 57: karana_name = "Shakuni"
        elif karana_idx == 58: karana_name = "Chatushpada"
        elif karana_idx == 59: karana_name = "Naga"
        else: karana_name = KARANAS_MOVING[(karana_idx - 1) % 7]

        # --- Vimshottari Dasha Calculation ---
        dasha_lords = [
            {'name': 'Ketu', 'years': 7}, {'name': 'Shukra', 'years': 20}, {'name': 'Surya', 'years': 6},
            {'name': 'Chandra', 'years': 10}, {'name': 'Kuja', 'years': 7}, {'name': 'Rahu', 'years': 18},
            {'name': 'Guru', 'years': 16}, {'name': 'Shani', 'years': 19}, {'name': 'Budha', 'years': 17}
        ]
        nakshatra_span = 360.0 / 27.0
        nak_lord_idx = nak_idx % 9
        
        passed_span = moon_pos % nakshatra_span
        rem_fraction = 1.0 - (passed_span / nakshatra_span)
        first_dasha_years = dasha_lords[nak_lord_idx]['years'] * rem_fraction
        
        bal_y = int(first_dasha_years)
        bal_m_float = (first_dasha_years - bal_y) * 12
        bal_m = int(bal_m_float)
        bal_d = int((bal_m_float - bal_m) * 30.436875)
        dasha_balance = f"{dasha_lords[nak_lord_idx]['name']} {bal_y}Y - {bal_m}M - {bal_d}D"
        
        dashas = []
        def add_years(dt, y):
            return dt + timedelta(days=y * 365.2425)

        current_dt = local_dt
        real_now_dt = datetime.now(target_tz)
        md_start_dt = current_dt
        theoretical_start_dt = add_years(current_dt, - (dasha_lords[nak_lord_idx]['years'] - first_dasha_years))
        
        for i in range(9):
            md_idx = (nak_lord_idx + i) % 9
            md_lord = dasha_lords[md_idx]
            md_total_years = md_lord['years']
            
            if i == 0:
                md_end_dt = add_years(current_dt, first_dasha_years)
                act_md_start = current_dt
            else:
                act_md_start = md_start_dt
                md_end_dt = add_years(act_md_start, md_total_years)
                theoretical_start_dt = act_md_start
                
            md_is_current = act_md_start <= real_now_dt < md_end_dt
                
            antardashas = []
            ad_start_dt = theoretical_start_dt
            for j in range(9):
                ad_idx = (md_idx + j) % 9
                ad_lord = dasha_lords[ad_idx]
                ad_years = (md_total_years * ad_lord['years']) / 120.0
                ad_end_dt = add_years(ad_start_dt, ad_years)
                
                ad_is_current = max(current_dt, ad_start_dt) <= real_now_dt < ad_end_dt
                
                pratyantardashas = []
                pd_start_dt = ad_start_dt
                for k in range(9):
                    pd_idx = (ad_idx + k) % 9
                    pd_lord = dasha_lords[pd_idx]
                    pd_years = (ad_years * pd_lord['years']) / 120.0
                    pd_end_dt = add_years(pd_start_dt, pd_years)
                    
                    pd_is_current = max(current_dt, pd_start_dt) <= real_now_dt < pd_end_dt
                    
                    pratyantardashas.append({
                        'lord': pd_lord['name'],
                        'end': pd_end_dt.strftime('%d-%b-%Y'),
                        'is_current': pd_is_current
                    })
                    pd_start_dt = pd_end_dt

                antardashas.append({
                    'lord': ad_lord['name'],
                    'end': ad_end_dt.strftime('%d-%b-%Y'),
                    'pratyantardashas': pratyantardashas,
                    'is_current': ad_is_current
                })
                ad_start_dt = ad_end_dt
                
            dashas.append({
                'lord': md_lord['name'],
                'end': md_end_dt.strftime('%d-%b-%Y'),
                'antardashas': antardashas,
                'is_current': md_is_current
            })
            
            md_start_dt = md_end_dt

        # --- Ashtakavarga Calculation ---
        AV_TABLES = {
            'Su': {'Su': [1,2,4,7,8,9,10,11], 'Ch': [3,6,10,11], 'Ku': [1,2,4,7,8,9,10,11], 'Bu': [3,5,6,9,10,11,12], 'Gu': [5,6,9,11], 'Sk': [6,7,12], 'Sa': [1,2,4,7,8,9,10,11], 'Lg': [3,4,6,10,11,12]},
            'Ch': {'Su': [3,6,7,8,10,11], 'Ch': [1,3,6,7,10,11], 'Ku': [2,3,5,6,9,10,11], 'Bu': [1,3,4,5,7,8,10,11], 'Gu': [1,4,7,8,10,11,12], 'Sk': [3,4,5,7,9,10,11], 'Sa': [3,5,6,11], 'Lg': [3,6,10,11]},
            'Ku': {'Su': [3,5,6,10,11], 'Ch': [3,6,11], 'Ku': [1,2,4,7,8,10,11], 'Bu': [3,5,6,11], 'Gu': [6,10,11,12], 'Sk': [6,8,11,12], 'Sa': [1,4,7,8,9,10,11], 'Lg': [1,3,6,10,11]},
            'Bu': {'Su': [5,6,9,11,12], 'Ch': [2,4,6,8,10,11], 'Ku': [1,2,4,7,8,9,10,11], 'Bu': [1,3,5,6,9,10,11,12], 'Gu': [6,8,11,12], 'Sk': [1,2,3,4,5,8,9,11], 'Sa': [1,2,4,7,8,9,10,11], 'Lg': [1,2,4,6,8,10,11]},
            'Gu': {'Su': [1,2,3,4,7,8,9,10,11], 'Ch': [2,5,7,9,11], 'Ku': [1,2,4,7,8,10,11], 'Bu': [1,2,4,5,6,9,10,11], 'Gu': [1,2,3,4,7,8,10,11], 'Sk': [2,5,6,9,10,11], 'Sa': [3,5,6,12], 'Lg': [1,2,4,5,6,9,10,11,12]},
            'Sk': {'Su': [8,11,12], 'Ch': [1,2,3,4,5,8,9,11,12], 'Ku': [3,5,6,9,11,12], 'Bu': [3,5,6,9,11], 'Gu': [5,8,9,10,11], 'Sk': [1,2,3,4,5,8,9,10,11], 'Sa': [3,4,5,8,9,10,11], 'Lg': [1,2,3,4,5,8,9,11]},
            'Sa': {'Su': [1,2,4,7,8,10,11], 'Ch': [3,6,11], 'Ku': [3,5,6,10,11,12], 'Bu': [6,8,9,10,11,12], 'Gu': [5,6,11,12], 'Sk': [6,11,12], 'Sa': [3,5,6,11], 'Lg': [1,3,4,6,10,11]}
        }
        
        bav = {}
        sav = [0] * 12
        for tp in ['Su', 'Ch', 'Ku', 'Bu', 'Gu', 'Sk', 'Sa']:
            bav[tp] = [0] * 12
            for cp in ['Su', 'Ch', 'Ku', 'Bu', 'Gu', 'Sk', 'Sa', 'Lg']:
                base_r = rasi_positions[cp]
                for offset in AV_TABLES[tp][cp]:
                    target_r = (base_r + offset - 1) % 12
                    bav[tp][target_r] += 1
            for i in range(12):
                sav[i] += bav[tp][i]

        # --- Shadbala Calculation (Planetary Strengths) ---
        shadbala = {}
        uchha_deg = {'Su': 10, 'Ch': 33, 'Ku': 298, 'Bu': 165, 'Gu': 95, 'Sk': 357, 'Sa': 200}
        dig_targets = {'Su': 270, 'Ku': 270, 'Sa': 180, 'Ch': 90, 'Sk': 90, 'Gu': 0, 'Bu': 0}
        naisargika = {'Su': 60.0, 'Ch': 51.43, 'Sk': 42.85, 'Gu': 34.28, 'Bu': 25.71, 'Ku': 17.14, 'Sa': 8.57}
        
        sun_dist_asc = (sun_pos - asc) % 360
        is_day = 180 <= sun_dist_asc <= 360 # సూర్యుడు లగ్నం నుండి 7-12 స్థానాల్లో ఉంటే పగలు
        
        for p in ['Su', 'Ch', 'Ku', 'Bu', 'Gu', 'Sk', 'Sa']:
            pos = longitudes[p]['deg']
            
            # 1. Sthana Bala (Uchha Bala based)
            dist_uchha = min(abs(pos - uchha_deg[p]), 360 - abs(pos - uchha_deg[p]))
            sthana = round((180 - dist_uchha) / 3.0, 2)
            
            # 2. Dig Bala (Directional Strength)
            target = (asc + dig_targets[p]) % 360
            dist_dig = min(abs(pos - target), 360 - abs(pos - target))
            dig = round((180 - dist_dig) / 3.0, 2)
            
            # 3. Kala Bala (Time Strength - Approx Natonnatha & Paksha)
            if p in ['Su', 'Gu', 'Sk']: kala = 60 if is_day else 0
            elif p in ['Ch', 'Ku', 'Sa']: kala = 0 if is_day else 60
            else: kala = 60
            
            if p == 'Ch':
                dist_sun = (moon_pos - sun_pos) % 360
                paksha_bala = dist_sun / 3.0 if dist_sun <= 180 else (360 - dist_sun) / 3.0
                kala += paksha_bala
            kala = round(kala, 2)
            
            # 4. Chesta Bala (Motional Strength)
            is_retro = longitudes[p]['isR']
            if p in ['Su', 'Ch']: chesta = 30.0
            else: chesta = 60.0 if is_retro else 15.0
            
            # 5. Naisargika Bala (Natural Strength)
            nais = naisargika[p]
            
            # 6. Drik Bala (Aspect Strength - Base default)
            drik = 30.0
            
            total_shashtiamsha = sthana + dig + kala + chesta + nais + drik
            rupas = round(total_shashtiamsha / 60.0, 2)
            
            shadbala[p] = {
                'sthana': sthana, 'dig': dig, 'kala': kala, 
                'chesta': chesta, 'naisargika': nais, 'drik': drik, 
                'total': round(total_shashtiamsha, 2), 'rupas': rupas
            }

        return jsonify({
            'chart': chart_data,
            'chart_d9': chart_data_d9,
            'chart_d3': chart_data_d3,
            'chart_d7': chart_data_d7,
            'chart_d10': chart_data_d10,
            'chart_d12': chart_data_d12,
            'longitudes': longitudes,
            'nakshatra': NAKSHATRAS[nak_idx],
            'rasi': RASI_NAMES[rasi_idx],
            'pada': pada,
            'tithi': f"{paksha} {tithi_name}",
            'yoga': YOGAS[yoga_idx],
            'karana': karana_name,
            'vimshottari': dashas,
            'dasha_balance': dasha_balance,
            'lagna_rasi_idx': rasi_positions['Lg'],
            'ashtakavarga': {'bav': bav, 'sav': sav},
            'shadbala': shadbala
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)