# Plan: Expand `${DATA_HOME}` in CSV path columns

## Context

The `.csv` files in `NMT/data/CharLOTTE/PLAIN/` and `NMT/data/CharLOTTE/SC/` were updated to use `${DATA_HOME}` as a prefix in their `src_path` and `tgt_path` columns (e.g., `${DATA_HOME}/data/CharLOTTE_data/an-en/train.an.txt`). The scripts that read these CSVs and then open the referenced files do not currently expand environment variables, so file opens will fail with unresolved `${DATA_HOME}` in the path. The fix is to call `os.path.expandvars()` on each path immediately after it is read from the CSV.

## Files to Modify

### 1. `NMT/parallel_datasets.py`

**Problem:** `MultilingualDataset.read_csv()` reads `src_path`/`tgt_path` from CSV rows and passes them directly to `self.read_file()`. `os` is not imported.

**Changes:**
- Add `import os` at the top of the file.
- In `read_csv()`, after unpacking each row and before any assertions, add:
  ```python
  src_path = os.path.expandvars(src_path)
  tgt_path = os.path.expandvars(tgt_path)
  ```
  Insert at line ~122, immediately after the `for src_lang, tgt_lang, src_path, tgt_path in rows:` line.

---

### 2. `NMT/assert_no_data_overlap.py`

**Problem:** `read_csv_by_file()` reads `src_path`/`tgt_path` from CSV rows and passes them to `read_f()` without expansion. `os` is already imported.

**Changes:**
- In `read_csv_by_file()`, after unpacking each row and before calling `read_f()`, add:
  ```python
  src_path = os.path.expandvars(src_path)
  tgt_path = os.path.expandvars(tgt_path)
  ```
  Insert at line ~87, immediately after the `for src_lang, tgt_lang, src_path, tgt_path in data:` line.

---

### 3. `Pipeline/make_tok_training_data.py`

**Problem:** `get_lang_paths()` collects `src_f`/`tgt_f` paths from CSV rows into lists; those paths are later opened in `write_data()`. `os` is already imported.

**Changes:**
- In `get_lang_paths()`, after unpacking each row and before any assertions, add:
  ```python
  src_f = os.path.expandvars(src_f)
  tgt_f = os.path.expandvars(tgt_f)
  ```
  Insert at line ~111, immediately after the `for src_lang, tgt_lang, src_f, tgt_f in rows:` line.

---

## Notes

- `Pipeline/make_SC_training_data.py` uses `MultilingualDataset` directly, so it is covered by fix #1.
- The `{SC_MODEL_ID}` placeholder in paths uses `{}` (not `${}`), so `os.path.expandvars()` will not interfere with it.
- All fixes follow the same pattern: expand env vars immediately after parsing from the CSV row, before any path is used.

## Verification

After changes:
1. Ensure `DATA_HOME` is set in the environment (via `.env` or shell).
2. Run `NMT/train.py` with a config that references one of the updated CSVs (e.g., `NMT/configs/CONFIGS/an-en/NMT.an-en.yaml`) in TEST mode and confirm data loads without path errors.
3. Run `NMT/assert_no_data_overlap.py` on a PLAIN data directory and confirm it reads files successfully.
4. Run `Pipeline/make_tok_training_data.py` with a PLAIN CSV and confirm it writes output without path errors.
