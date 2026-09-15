import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataValidator:

    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?[\d\s\-\(\)]{10,20}$')
    IBAN_PATTERN = re.compile(r'^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$')
    
    def __init__(self, verbose: bool = True):
   
        self.verbose = verbose
        self.validation_report = {
            'duplicates_removed': 0,
            'missing_values_imputed': 0,
            'invalid_emails': 0,
            'invalid_phones': 0,
            'invalid_ibans': 0,
            'outliers_detected': 0
        }
    
    def validate_email(self, email: str) -> bool:
        if pd.isna(email) or not isinstance(email, str):
            return False
        return bool(self.EMAIL_PATTERN.match(email.strip()))
    
    def validate_phone(self, phone: str) -> bool:
        if pd.isna(phone) or not isinstance(phone, str):
            return False
        return bool(self.PHONE_PATTERN.match(phone.strip()))
    
    def validate_iban(self, iban: str) -> bool:
        if pd.isna(iban) or not isinstance(iban, str):
            return False
        iban_clean = iban.replace(' ', '').upper()
        return bool(self.IBAN_PATTERN.match(iban_clean))
    
    def sanitize_string(self, value: Any) -> str:
        if pd.isna(value):
            return ''
        
        cleaned = str(value).strip()
        
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'--',
            r';.*--',
        ]
        
        for pattern in dangerous_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        return cleaned
    
    def remove_duplicates(self, df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
        initial_count = len(df)
        df_clean = df.drop_duplicates(subset=subset, keep='first')
        duplicates_count = initial_count - len(df_clean)
        
        self.validation_report['duplicates_removed'] += duplicates_count
        
        if self.verbose and duplicates_count > 0:
            logger.info(f"[OK] Usunieto {duplicates_count} duplikatow")
        
        return df_clean
    
    def impute_missing_values(self, df: pd.DataFrame, strategy: Dict[str, str] = None) -> pd.DataFrame:
        
        if strategy is None:
            strategy = {}
        
        df_imputed = df.copy()
        missing_before = df_imputed.isna().sum().sum()
        
        for column in df_imputed.columns:
            missing_count = df_imputed[column].isna().sum()
            
            if missing_count == 0:
                continue
            
            col_strategy = strategy.get(column, 'auto')
            
            if col_strategy == 'auto':
                if df_imputed[column].dtype in ['int64', 'float64']:
                    col_strategy = 'median'
                elif df_imputed[column].dtype == 'object':
                    col_strategy = 'mode'
                else:
                    col_strategy = 'ffill'
            
            try:
                if col_strategy == 'mean':
                    df_imputed[column] = df_imputed[column].fillna(df_imputed[column].mean())
                elif col_strategy == 'median':
                    df_imputed[column] = df_imputed[column].fillna(df_imputed[column].median())
                elif col_strategy == 'mode':
                    mode_value = df_imputed[column].mode()
                    if len(mode_value) > 0:
                        df_imputed[column] = df_imputed[column].fillna(mode_value[0])
                elif col_strategy == 'ffill':
                    df_imputed[column] = df_imputed[column].ffill()
                elif col_strategy == 'bfill':
                    df_imputed[column] = df_imputed[column].bfill()
                elif col_strategy == 'zero':
                    df_imputed[column] = df_imputed[column].fillna(0)
                elif col_strategy == 'empty':
                    df_imputed[column] = df_imputed[column].fillna('')
                
                if self.verbose:
                    logger.info(f"[OK] Uzupelniono {missing_count} brakujacych wartosci w kolumnie '{column}' strategia '{col_strategy}'")
            
            except Exception as e:
                logger.warning(f"[WARN] Nie udalo sie uzupelnic kolumny '{column}': {e}")
        
        missing_after = df_imputed.isna().sum().sum()
        self.validation_report['missing_values_imputed'] += (missing_before - missing_after)
        
        return df_imputed
    
    def validate_dataframe_emails(self, df: pd.DataFrame, email_column: str) -> Tuple[pd.DataFrame, List[int]]:
        
        if email_column not in df.columns:
            logger.warning(f"[WARN] Kolumna '{email_column}' nie istnieje w DataFrame")
            return df, []
        
        df_validated = df.copy()
        valid_mask = df_validated[email_column].fillna('').astype(str).str.match(self.EMAIL_PATTERN)
        invalid_indices = df_validated[~valid_mask].index.tolist()
        
        invalid_count = len(invalid_indices)
        self.validation_report['invalid_emails'] += invalid_count
        
        if self.verbose and invalid_count > 0:
            logger.warning(f"[WARN] Znaleziono {invalid_count} niepoprawnych adresow email")
        
        return df_validated, invalid_indices
    
    def validate_dataframe_phones(self, df: pd.DataFrame, phone_column: str) -> Tuple[pd.DataFrame, List[int]]:
        
        if phone_column not in df.columns:
            logger.warning(f"[WARN] Kolumna '{phone_column}' nie istnieje w DataFrame")
            return df, []
        
        valid_mask = df[phone_column].fillna('').astype(str).str.match(self.PHONE_PATTERN)
        invalid_indices = df[~valid_mask & df[phone_column].notna()].index.tolist()
        
        invalid_count = len(invalid_indices)
        self.validation_report['invalid_phones'] += invalid_count
        
        if self.verbose and invalid_count > 0:
            logger.warning(f"[WARN] Znaleziono {invalid_count} niepoprawnych numerow telefonu")
        
        return df, invalid_indices
    
    def sanitize_dataframe(self, df: pd.DataFrame, text_columns: Optional[List[str]] = None) -> pd.DataFrame:
        
        df_sanitized = df.copy()
        
        if text_columns is None:
            text_columns = df_sanitized.select_dtypes(include=['object']).columns.tolist()
        
        dangerous_pattern = r'<script[^>]*>.*?</script>|javascript:|on\w+\s*=|--|;.*--'
        
        for column in text_columns:
            if column in df_sanitized.columns:
                df_sanitized[column] = df_sanitized[column].fillna('').astype(str).str.strip()
                df_sanitized[column] = df_sanitized[column].str.replace(dangerous_pattern, '', regex=True, flags=re.IGNORECASE)
                
                if self.verbose:
                    logger.info(f"[OK] Zsanityzowano kolumne '{column}'")
        
        return df_sanitized
    
    def detect_outliers_zscore(self, df: pd.DataFrame, column: str, threshold: float = 3.0) -> List[int]:
        
        if column not in df.columns:
            logger.warning(f"[WARN] Kolumna '{column}' nie istnieje w DataFrame")
            return []
        
        mean = df[column].mean()
        std = df[column].std()
        
        if std == 0:
            return []
        
        z_scores = np.abs((df[column] - mean) / std)
        outliers = df[z_scores > threshold].index.tolist()
        
        self.validation_report['outliers_detected'] += len(outliers)
        
        if self.verbose and len(outliers) > 0:
            logger.info(f"[OK] Wykryto {len(outliers)} wartosci odst w kolumnie '{column}' (Z-score > {threshold})")
        
        return outliers
    
    def detect_outliers_iqr(self, df: pd.DataFrame, column: str, multiplier: float = 1.5) -> List[int]:
       
        if column not in df.columns:
            logger.warning(f"[WARN] Kolumna '{column}' nie istnieje w DataFrame")
            return []
        
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)].index.tolist()
        
        self.validation_report['outliers_detected'] += len(outliers)
        
        if self.verbose and len(outliers) > 0:
            logger.info(f"[OK] Wykryto {len(outliers)} wartosci odst w kolumnie '{column}' (IQR, zakres: {lower_bound:.2f} - {upper_bound:.2f})")
        
        return outliers
    
    def generate_quality_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        
        report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isna().sum().to_dict(),
            'missing_percentage': (df.isna().sum() / len(df) * 100).to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'data_types': df.dtypes.astype(str).to_dict(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'validation_summary': self.validation_report.copy()
        }
        
        return report
    
    def print_quality_report(self, report: Dict[str, Any]):
        
        print("\n" + "="*70)
        print("RAPORT JAKOSCI DANYCH")
        print("="*70)
        print(f"Wymiary: {report['total_rows']} wierszy x {report['total_columns']} kolumn")
        print(f"Pamiec: {report['memory_usage_mb']:.2f} MB")
        print(f"Duplikaty: {report['duplicate_rows']} wierszy")
        
        print("\nBrakujace wartosci:")
        missing = {k: v for k, v in report['missing_values'].items() if v > 0}
        if missing:
            for col, count in missing.items():
                pct = report['missing_percentage'][col]
                print(f"   • {col}: {count} ({pct:.1f}%)")
        else:
            print("   [OK] Brak brakujacych wartosci")
        
        print("\n[OK] Podsumowanie walidacji:")
        summary = report['validation_summary']
        print(f"   • Usunięte duplikaty: {summary['duplicates_removed']}")
        print(f"   • Uzupełnione wartości: {summary['missing_values_imputed']}")
        print(f"   • Niepoprawne emaile: {summary['invalid_emails']}")
        print(f"   • Niepoprawne telefony: {summary['invalid_phones']}")
        print(f"   • Wykryte outliers: {summary['outliers_detected']}")
        print("="*70 + "\n")
    
    def clean_and_validate(self, df: pd.DataFrame, config: Dict[str, Any] = None) -> pd.DataFrame:
        
        if config is None:
            config = {}
        
        df_clean = df.copy()
        
        print("\n" + "="*70)
        print("PROCES CZYSZCZENIA I WALIDACJI DANYCH")
        print("="*70)
        
        if config.get('remove_duplicates', True):
            print("\n[1] Usuwanie duplikatow...")
            subset = config.get('duplicate_subset', None)
            df_clean = self.remove_duplicates(df_clean, subset=subset)
        
        if config.get('impute_strategy'):
            print("\n[2] Imputacja brakujacych wartosci...")
            df_clean = self.impute_missing_values(df_clean, strategy=config['impute_strategy'])
        
        if config.get('validate_emails'):
            print("\n[3] Walidacja adresow email (Regex)...")
            df_clean, invalid = self.validate_dataframe_emails(df_clean, config['validate_emails'])
        
        if config.get('validate_phones'):
            print("\n[4] Walidacja numerow telefonu (Regex)...")
            df_clean, invalid = self.validate_dataframe_phones(df_clean, config['validate_phones'])
        
        if config.get('sanitize_columns'):
            print("\n[5] Sanityzacja kolumn tekstowych...")
            df_clean = self.sanitize_dataframe(df_clean, text_columns=config['sanitize_columns'])
        
        if config.get('detect_outliers'):
            print("\n[6] Detekcja wartosci odstajaacych...")
            for column, params in config['detect_outliers'].items():
                method = params.get('method', 'iqr')
                if method == 'zscore':
                    threshold = params.get('threshold', 3.0)
                    self.detect_outliers_zscore(df_clean, column, threshold=threshold)
                elif method == 'iqr':
                    multiplier = params.get('multiplier', 1.5)
                    self.detect_outliers_iqr(df_clean, column, multiplier=multiplier)
        
        print("\n[OK] Proces czyszczenia zakonczony!")
        print("="*70)
        
        return df_clean


def quick_clean(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    
    validator = DataValidator(verbose=verbose)
    
    config = {
        'remove_duplicates': True,
        'impute_strategy': {},
    }
    
    for col in df.columns:
        col_lower = col.lower()
        if 'email' in col_lower:
            config['validate_emails'] = col
        if 'phone' in col_lower or 'telefon' in col_lower:
            config['validate_phones'] = col
    
    return validator.clean_and_validate(df, config)


def validate_csv_file(input_path: str, output_path: str = None, config: Dict[str, Any] = None):
    
    print(f"\n📂 Wczytywanie pliku: {input_path}")
    df = pd.read_csv(input_path)
    
    validator = DataValidator(verbose=True)
    df_clean = validator.clean_and_validate(df, config)
    
    report = validator.generate_quality_report(df_clean)
    validator.print_quality_report(report)
    
    if output_path is None:
        output_path = input_path
    
    df_clean.to_csv(output_path, index=False)
    print(f"[OK] Zapisano oczyszczone dane do: {output_path}")
    
    return df_clean
