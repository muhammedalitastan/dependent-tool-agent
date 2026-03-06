from typing import Dict, Any, Optional, List
from database import MockDatabase
import json

class ToolError(Exception):
    """Tool hataları için özel exception"""
    pass

class ToolManager:
    """API araçlarını yöneten sınıf"""
    
    def __init__(self):
        self.db = MockDatabase()
    
    def get_user_details(self, email: str) -> Dict[str, Any]:
        """
        E-posta adresine göre kullanıcı detaylarını getirir.
        
        Args:
            email: Kullanıcı e-posta adresi
            
        Returns:
            Kullanıcı bilgileri
            
        Raises:
            ToolError: Kullanıcı bulunamadığında
        """
        if not email or "@" not in email:
            raise ToolError("Geçersiz e-posta adresi")
        
        user = self.db.get_user_by_email(email)
        
        if not user:
            raise ToolError(f"Kullanıcı bulunamadı: {email}")
        
        return {
            "success": True,
            "user_id": user["user_id"],
            "email": user["email"],
            "name": user["name"],
            "status": user["status"],
            "created_date": user["created_date"],
            "last_login": user["last_login"]
        }
    
    def get_recent_transactions(self, user_id: str, limit: int = 5) -> Dict[str, Any]:
        """
        Kullanıcının son işlemlerini getirir.
        
        Args:
            user_id: Kullanıcı ID'si
            limit: Getirilecek işlem sayısı
            
        Returns:
            İşlem listesi
            
        Raises:
            ToolError: Kullanıcı bulunamadığında veya limit geçersiz olduğunda
        """
        if not user_id:
            raise ToolError("Kullanıcı ID'si gerekli")
        
        if limit <= 0 or limit > 50:
            raise ToolError("Limit 1-50 arasında olmalı")
        
        # Kullanıcının varlığını kontrol et
        user = self.db.get_user_by_id(user_id)
        if not user:
            raise ToolError(f"Kullanıcı bulunamadı: {user_id}")
        
        transactions = self.db.get_transactions_by_user(user_id, limit)
        
        return {
            "success": True,
            "user_id": user_id,
            "transactions": transactions,
            "total_count": len(transactions)
        }
    
    def check_fraud_reason(self, transaction_id: str) -> Dict[str, Any]:
        """
        Başarısız işlemin fraud nedenini kontrol eder.
        
        Args:
            transaction_id: İşlem ID'si
            
        Returns:
            Fraud nedeni bilgileri
            
        Raises:
            ToolError: İşlem bulunamadığında veya fraud kaydı bulunamadığında
        """
        if not transaction_id:
            raise ToolError("İşlem ID'si gerekli")
        
        # İşlemin varlığını kontrol et
        transaction = self.db.get_transaction_by_id(transaction_id)
        if not transaction:
            raise ToolError(f"İşlem bulunamadı: {transaction_id}")
        
        # Fraud nedenini kontrol et
        fraud_reason = self.db.get_fraud_reason(transaction_id)
        
        if not fraud_reason:
            raise ToolError(f"Fraud kaydı bulunamadı: {transaction_id}")
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "fraud_reason": fraud_reason["reason"],
            "detailed_code": fraud_reason["detailed_code"],
            "detected_at": fraud_reason["detected_at"],
            "transaction_status": transaction["status"],
            "transaction_amount": transaction["amount"]
        }
    
    def get_failed_transactions_for_user(self, email: str) -> Dict[str, Any]:
        """
        Kullanıcının başarısız işlemlerini getirir (yardımcı araç).
        
        Args:
            email: Kullanıcı e-posta adresi
            
        Returns:
            Başarısız işlemler listesi
        """
        # Önce kullanıcı detaylarını al
        user_details = self.get_user_details(email)
        user_id = user_details["user_id"]
        
        # Başarısız işlemleri filtrele
        all_transactions = self.db.get_transactions_by_user(user_id, limit=50)
        failed_transactions = [
            tx for tx in all_transactions 
            if tx["status"] == "failed"
        ]
        
        return {
            "success": True,
            "user_id": user_id,
            "email": email,
            "failed_transactions": failed_transactions,
            "failed_count": len(failed_transactions)
        }
    
    def analyze_user_activity(self, email: str) -> Dict[str, Any]:
        """
        Kullanıcı aktivitesini analiz eder (yardımcı araç).
        
        Args:
            email: Kullanıcı e-posta adresi
            
        Returns:
            Aktivite analizi
        """
        user_details = self.get_user_details(email)
        user_id = user_details["user_id"]
        
        transactions = self.db.get_transactions_by_user(user_id, limit=50)
        
        # İstatistikleri hesapla
        total_transactions = len(transactions)
        successful_transactions = len([tx for tx in transactions if tx["status"] == "success"])
        failed_transactions = len([tx for tx in transactions if tx["status"] == "failed"])
        
        total_amount = sum(tx["amount"] for tx in transactions if tx["status"] == "success")
        
        return {
            "success": True,
            "user_details": user_details,
            "total_transactions": total_transactions,
            "successful_transactions": successful_transactions,
            "failed_transactions": failed_transactions,
            "success_rate": (successful_transactions / total_transactions * 100) if total_transactions > 0 else 0,
            "total_amount": total_amount
        }

# Tool instance oluştur
tool_manager = ToolManager()
