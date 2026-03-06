import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class MockDatabase:
    """Sahte veritabanı sınıfı"""
    
    def __init__(self, data_path: str = "data"):
        self.data_path = data_path
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Veritabanı verilerini JSON dosyasından yükler"""
        db_path = os.path.join(self.data_path, "mock_database.json")
        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _save_data(self):
        """Veritabanı verilerini JSON dosyasına kaydeder"""
        db_path = os.path.join(self.data_path, "mock_database.json")
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """E-posta adresine göre kullanıcı bulur"""
        for user in self.data["users"]:
            if user["email"].lower() == email.lower():
                return user
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Kullanıcı ID'sine göre kullanıcı bulur"""
        for user in self.data["users"]:
            if user["user_id"] == user_id:
                return user
        return None
    
    def get_transactions_by_user(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Kullanıcının işlemlerini getirir"""
        user_transactions = [
            tx for tx in self.data["transactions"] 
            if tx["user_id"] == user_id
        ]
        
        # Tarih sırasına göre sırala (en yeni üstte)
        user_transactions.sort(
            key=lambda x: datetime.fromisoformat(x["timestamp"]), 
            reverse=True
        )
        
        return user_transactions[:limit]
    
    def get_transaction_by_id(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """İşlem ID'sine göre işlem bulur"""
        for tx in self.data["transactions"]:
            if tx["transaction_id"] == transaction_id:
                return tx
        return None
    
    def get_fraud_reason(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """İşlemin fraud nedenini getirir"""
        for fraud in self.data["fraud_reasons"]:
            if fraud["transaction_id"] == transaction_id:
                return fraud
        return None
    
    def add_user(self, user_data: Dict[str, Any]) -> str:
        """Yeni kullanıcı ekler"""
        # Yeni kullanıcı ID oluştur
        new_id = f"USR{len(self.data['users']) + 1:03d}"
        user_data["user_id"] = new_id
        user_data["created_date"] = datetime.now().isoformat()
        user_data["last_login"] = datetime.now().isoformat()
        
        self.data["users"].append(user_data)
        self._save_data()
        
        return new_id
    
    def add_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """Yeni işlem ekler"""
        # Yeni işlem ID oluştur
        new_id = f"TRX{len(self.data['transactions']) + 1:03d}"
        transaction_data["transaction_id"] = new_id
        transaction_data["timestamp"] = datetime.now().isoformat()
        
        self.data["transactions"].append(transaction_data)
        self._save_data()
        
        return new_id
    
    def add_fraud_reason(self, fraud_data: Dict[str, Any]):
        """Fraud nedeni ekler"""
        fraud_data["detected_at"] = datetime.now().isoformat()
        self.data["fraud_reasons"].append(fraud_data)
        self._save_data()
    
    def update_user_status(self, user_id: str, status: str):
        """Kullanıcı durumunu günceller"""
        for user in self.data["users"]:
            if user["user_id"] == user_id:
                user["status"] = status
                self._save_data()
                return True
        return False
    
    def get_failed_transactions(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Başarısız işlemleri getirir"""
        failed_tx = [
            tx for tx in self.data["transactions"] 
            if tx["status"] == "failed"
        ]
        
        if user_id:
            failed_tx = [tx for tx in failed_tx if tx["user_id"] == user_id]
        
        return failed_tx
