"""
Database comment loader for table and column comments from CSV files.
"""
import csv
from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from phase1.models.database import DbTable, DbColumn


class DbCommentLoader:
    """Loads table and column comments from CSV files"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def load_table_comments(self, csv_path: str) -> Dict[str, int]:
        """
        Load table comments from CSV file.
        Expected format: OWNER, TABLE_NAME, COMMENTS
        
        Returns:
            Dict with counts: {'loaded': int, 'skipped': int}
        """
        if not Path(csv_path).exists():
            return {'loaded': 0, 'skipped': 0}
        
        loaded = 0
        skipped = 0
        
        try:
            with open(csv_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    owner = (row.get('OWNER') or '').upper().strip()
                    table_name = (row.get('TABLE_NAME') or '').upper().strip()
                    comment = row.get('COMMENTS', '').strip()
                    
                    if not table_name:
                        skipped += 1
                        continue
                    
                    # Find matching table
                    query = self.session.query(DbTable).filter(
                        DbTable.table_name == table_name
                    )
                    
                    if owner:
                        query = query.filter(DbTable.owner == owner)
                    
                    table = query.first()
                    
                    if table:
                        table.table_comment = comment if comment else None
                        loaded += 1
                    else:
                        skipped += 1
                
                self.session.commit()
                
        except Exception as e:
            print(f"Error loading table comments from {csv_path}: {e}")
            self.session.rollback()
            
        return {'loaded': loaded, 'skipped': skipped}
    
    def load_column_comments(self, csv_path: str) -> Dict[str, int]:
        """
        Load column comments from CSV file.
        Expected format: OWNER, TABLE_NAME, COLUMN_NAME, COMMENTS
        
        Returns:
            Dict with counts: {'loaded': int, 'skipped': int}
        """
        if not Path(csv_path).exists():
            return {'loaded': 0, 'skipped': 0}
        
        loaded = 0
        skipped = 0
        
        try:
            with open(csv_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    owner = (row.get('OWNER') or '').upper().strip()
                    table_name = (row.get('TABLE_NAME') or '').upper().strip()
                    column_name = (row.get('COLUMN_NAME') or '').upper().strip()
                    comment = row.get('COMMENTS', '').strip()
                    
                    if not table_name or not column_name:
                        skipped += 1
                        continue
                    
                    # Find matching column
                    query = self.session.query(DbColumn).join(DbTable)
                    
                    query = query.filter(
                        DbTable.table_name == table_name,
                        DbColumn.column_name == column_name
                    )
                    
                    if owner:
                        query = query.filter(DbTable.owner == owner)
                    
                    column = query.first()
                    
                    if column:
                        column.column_comment = comment if comment else None
                        loaded += 1
                    else:
                        skipped += 1
                
                self.session.commit()
                
        except Exception as e:
            print(f"Error loading column comments from {csv_path}: {e}")
            self.session.rollback()
            
        return {'loaded': loaded, 'skipped': skipped}
    
    def load_comments_from_directory(self, data_dir: str) -> Dict[str, Dict[str, int]]:
        """
        Load comments from standard CSV files in data directory.
        Expected files: ALL_TAB_COMMENTS.csv, ALL_COL_COMMENTS.csv
        
        Returns:
            Dict with results for each type: {'table_comments': {...}, 'column_comments': {...}}
        """
        data_path = Path(data_dir)
        results = {}
        
        # Load table comments
        table_csv = data_path / "ALL_TAB_COMMENTS.csv"
        results['table_comments'] = self.load_table_comments(str(table_csv))
        
        # Load column comments
        column_csv = data_path / "ALL_COL_COMMENTS.csv" 
        results['column_comments'] = self.load_column_comments(str(column_csv))
        
        return results