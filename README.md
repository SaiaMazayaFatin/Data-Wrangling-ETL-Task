# ETL Pipeline - Log Data Cleaning

A complete ETL (Extract, Transform, Load) pipeline for cleaning and processing dirty log data using **Prefect** for workflow orchestration.

---

## 📁 Project Structure

```
ETL/
├── main_flow.py              # Main Prefect flow orchestrator
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── data/
│   ├── raw/
│   │   └── dirty_logs.txt    # Raw input data (dirty logs)
│   └── processed/
│       └── cleaned_data.csv  # Cleaned output data
├── notebooks/
│   └── 01_eda_initial_check.ipynb  # Exploratory Data Analysis
├── src/
│   ├── __init__.py
│   ├── extract.py            # Data extraction task
│   ├── transform.py          # Data transformation & validation
│   ├── load.py               # Data loading task
│   └── utils.py              # Utility functions
└── tests/
    ├── __init__.py
    └── test_transforms.py    # Unit tests
```

---

## 🔄 ETL Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           ETL PIPELINE FLOW                             │
└─────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
  │   EXTRACT    │ ───▶ │  TRANSFORM   │ ───▶ │     LOAD     │
  │              │      │              │      │              │
  │ dirty_logs   │      │  Clean &     │      │ cleaned_data │
  │   .txt       │      │  Validate    │      │    .csv      │
  └──────────────┘      └──────────────┘      └──────────────┘
```

---

## 📊 Phase 1: Exploratory Data Analysis (EDA)

**File:** [notebooks/01_eda_initial_check.ipynb](notebooks/01_eda_initial_check.ipynb)

The EDA notebook explores the raw data to identify data quality issues:

### Findings from EDA:

| Issue | Description | Example |
|-------|-------------|---------|
| **Timestamp Formats** | Multiple formats exist | Unix (`1759380000`), ISO (`2025-10-10T13:40:12+00:00`), European (`DD/MM/YYYY`) |
| **Invalid User IDs** | Contains invalid entries | `guest`, empty strings, `null`, integers without prefix |
| **Platform Inconsistency** | Same platform, different names | `android`, `Android`, `google` (all should be `Android`) |
| **Negative Duration** | Invalid session durations | `-50`, `120s` (with suffix) |
| **Irrelevant Events** | System events to filter | `system_heartbeat`, `ad_load` |

---

## ⚙️ Phase 2: Extract

**File:** [src/extract.py](src/extract.py)

Reads the raw log file and converts it to a pandas DataFrame.

```python
@task(name="Extract Data")
def extract_data(file_path: str) -> pd.DataFrame
```

**Note:** The input file uses Python-style syntax (`logs = [...]`) with JSON-style `null` values, requiring special parsing logic.

---

## 🔧 Phase 3: Transform

**File:** [src/transform.py](src/transform.py)

Applies data cleaning and transformation rules:

| Step | Transformation | Rule |
|------|---------------|------|
| 1 | Filter Events | Remove `system_heartbeat`, `ad_load`, `None` |
| 2 | Validate User ID | Remove `null`, empty string, `guest` |
| 3 | Standardize User ID | Convert integers to `U-XXXXX` format |
| 4 | Standardize Platform | Map to `Android`, `iOS`, `Web`, `Other` |
| 5 | Clean Duration | Remove `s` suffix, handle negatives (clip to 0) |
| 6 | Normalize Timestamp | Convert all formats to ISO 8601 UTC |
| 7 | Feature Engineering | Add `device_type` column (`Mobile`/`Desktop`/`Other`) |

### Platform Mapping:
```
android, Android, google  →  Android
ios, iOS, Apple           →  iOS
web, WebApp               →  Web
Others                    →  Other
```

### Data Integrity Checks:
- ✅ No null User IDs
- ✅ No null Timestamps
- ✅ No negative session durations

---

## 💾 Phase 4: Load

**File:** [src/load.py](src/load.py)

Saves the cleaned DataFrame to CSV with ordered columns:

```python
@task(name="Load Data")
def load_data(df: pd.DataFrame, output_path: str)
```

**Output Columns:**
```
log_id | timestamp | user_id | device_type | device_platform | event_type | session_duration_sec
```

---

## 🛠️ Utility Functions

**File:** [src/utils.py](src/utils.py)

| Function | Description |
|----------|-------------|
| `parse_timestamp(ts)` | Converts multiple timestamp formats to ISO 8601 UTC |
| `standardize_uid(uid)` | Converts integer User IDs to `U-XXXXX` format |

### Supported Timestamp Formats:
1. **Unix Timestamp:** `1759380000` → `2025-10-01T12:00:00Z`
2. **European Format:** `01/10/2025 12:00:00` → `2025-10-01T12:00:00Z`
3. **ISO 8601:** `2025-10-01T12:00:00+00:00` → `2025-10-01T12:00:00Z`

---

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the ETL Pipeline
```bash
python main_flow.py
```

### 3. Expected Output
```
Reading data from data/raw/dirty_logs.txt...
🔄 Running transformation logic...
✅ Data Cleaned & Validated. Rows remaining: XXXX
Saving to data/processed/cleaned_data.csv...
```

---

## 📦 Dependencies

```
pandas
numpy
prefect
pytest
python-dateutil
```

---

## 🧪 Testing

Run unit tests with pytest:
```bash
pytest tests/
```

---

## 📈 Data Flow Summary

```
Input: data/raw/dirty_logs.txt
  │
  ▼
┌────────────────────────────────────────┐
│            EDA (Notebook)              │
│  - Identify data quality issues        │
│  - Analyze timestamp formats           │
│  - Find invalid user IDs               │
│  - Check platform inconsistencies      │
└────────────────────────────────────────┘
  │
  ▼
┌────────────────────────────────────────┐
│         EXTRACT (extract.py)           │
│  - Read dirty_logs.txt                 │
│  - Parse Python-style data format      │
│  - Convert to DataFrame                │
└────────────────────────────────────────┘
  │
  ▼
┌────────────────────────────────────────┐
│        TRANSFORM (transform.py)        │
│  - Filter irrelevant events            │
│  - Validate & standardize user IDs     │
│  - Normalize platforms                 │
│  - Clean session durations             │
│  - Parse & normalize timestamps        │
│  - Add device_type feature             │
│  - Data integrity checks               │
└────────────────────────────────────────┘
  │
  ▼
┌────────────────────────────────────────┐
│           LOAD (load.py)               │
│  - Reorder columns                     │
│  - Save to CSV                         │
└────────────────────────────────────────┘
  │
  ▼
Output: data/processed/cleaned_data.csv
```

---

## 📝 License

This project is for technical assessment purposes.
