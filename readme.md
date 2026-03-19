# 🕉️ Panchanga & Muhurtha Generator

A professional-grade, highly accurate Hindu astrological software built with Python (Flask) and Swiss Ephemeris (`pyswisseph`). This application generates detailed daily Panchangam, evaluates Muhurthams (auspicious times), calculates complex astrological charts (D1 & D9), and exports beautifully formatted traditional PDFs.

---

## ✨ Key Features

### 1. Advanced Panchanga Calculations
* **Core Elements:** Calculates exact start and end times for Tithi, Vaara, Nakshatra, Yoga, and Karana.
* **Lunar Month (Maasa):** Automatically identifies Adhika (Intercalary) and Nija (Regular) Maasas.
* **Inauspicious Timings:** Computes exact timings for Rahu Kalam, Yamagandam, Durmuhurtham, and Varjyam (Visha Nadi) based on local sunrise/sunset.
* **Combustion (Asthangatha):** Checks for Venus (Shukra) and Jupiter (Guru) Moudhyami/Combustion automatically.

### 2. Muhurtha Evaluation & Filtering
* **Tarabalam & Chandra Balam:** Computes exact Tarabalam and Ashtama Chandra Dosham for both Boy and Girl simultaneously.
* **Panchanga Shudhi Filter:** A powerful 1-click filter to instantly discard bad days and keep only the dates where all 5 elements (Tithi, Vaara, Nakshatra, Yoga, Karana) are auspicious according to user preferences.
* **Profile Management:** Save shortlisted Muhurtha dates into custom profiles. Add priorities, custom notes, and manage them effortlessly.

### 3. Interactive Astrology Charts (Muhurtha Chakra)
* **Dynamic D1 (Rasi) & D9 (Navamsha) Charts:** Real-time South Indian style chart generation for any selected date and time.
* **Lagna Calculation:** Highly precise Ascendant (Lagna) degrees and percentages.
* **Mid-Lagna Window:** Calculates the exact ±24 minute window around the center of the Lagna for absolute precision (Abhijit/Mid-Lagna).
* **Panchaka Rahitam:** Live calculation of Agni, Chora, Roga, Raja, and Mrityu Panchakas.

### 4. Professional Export System
* **PDF Generation:** Generates traditional, customizable, and print-ready PDF reports with a logo, client notes, priority-based sorting, and time-stamped footers using `jsPDF` & `AutoTable`.
* **CSV & JSON Exports:** Fully supports exporting data to CSV or JSON formats for further processing.
* **Dynamic UI & Export Columns:** Decoupled settings to customize what you see on the screen vs. what prints on the PDF.

---

## 🛠️ Technology Stack
* **Backend:** Python, Flask, PySwissEph (`pyswisseph`), Pytz
* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **Libraries:** `jsPDF`, `jsPDF-AutoTable` (for PDF generation)

---

## 🚀 Installation & Setup

1. **Clone or Download the Repository**
2. **Install Required Python Packages:**
   Make sure you have Python 3.7+ installed. Run the following command:
   ```bash
   pip install flask pyswisseph pytz
   ```
3. **Run the Application:**
   ```bash
   python app.py
   ```
4. **Access the App:**
   Open your web browser and go to `http://127.0.0.1:5000/`

---

## 📂 Project Structure

```text
Panchanga/
│
├── app.py                     # Main Flask backend & Astrological calculations
├── logo.png                   # Custom logo for PDF exports
├── preferences.json           # Auto-generated file storing user settings
├── README.md                  # Project documentation
│
├── static/
│   └── cities_short.json      # Database of cities with Lat, Lon, and Timezone
│
└── templates/
    ├── index.html             # Main Frontend UI (Panchanga & Muhurtha Tabs)
    └── settings.html          # UI for Preferences & Customizations
```

---

## 📖 How to Use

1. **Set Preferences:** Go to `⚙️ Settings` to define which Tithis, Nakshatras, etc., are considered "Good", and customize the columns you want to see/export.
2. **Generate Panchangam:** Select a date, location, and the number of days in the `Panchanga` tab. Click **Calculate**.
3. **Apply Pan Shudhi:** Click `✨ Pan Shudhi` to filter out inauspicious days automatically.
4. **Save Profile:** Select the filtered dates and click `💾 Save Table` to push them to the Muhurtha tab.
5. **Refine Muhurtham:** Switch to the `Muhurtha` tab, load your profile, enter priorities, and add client-specific notes.
6. **Check Muhurtha Chakra:** Select a specific date from the table to view the exact planetary alignments, Lagna times, and Panchaka Rahitam for that given minute.
7. **Export:** Click `📄 Export (PDF)` to download a beautifully formatted, traditional Muhurtha Patrike.

---

## 🔮 Future Scope
* **Ekavimshathi Mahadosha Integration:** Implementation of the 21 Great Doshas for marriage (like Latta, Pata, Ekargala, Kranti, etc.).
* **Saptama Shuddhi Check:** Live alerts for the presence of malefic planets in the 7th house during the selected Lagna.
* **Hora Muhurtham:** Dynamic integration of planetary Horas for micro-level timing selection.
* **Regional Customizations:** Toggle support for traditional Telugu/Sanskrit fonts in the PDF exports.

---

*Developed with passion for pure and accurate Vedic Astrological computations.* 🕉️