import re
from typing import Dict, Any, List, Optional, Tuple
from tools import tool_manager, ToolError

class ToolCallingAgent:
    """Kullanıcı taleplerini analiz edip gerekli araçları çağıran agent"""
    
    def __init__(self):
        self.tool_manager = tool_manager
        self.conversation_history = []
    
    def process_request(self, user_input: str) -> Dict[str, Any]:
        """
        Kullanıcı talebini işler ve gerekli araçları çağırır.
        
        Args:
            user_input: Kullanıcının girdisi
            
        Returns:
            İşlem sonucu
        """
        try:
            # Girdiyi analiz et
            intent, entities = self._analyze_input(user_input)
            
            # İntent'e göre araçları çağır
            result = self._execute_intent(intent, entities)
            
            # Sonucu formatla
            return self._format_response(result, intent, entities)
            
        except ToolError as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"İşlem hatası: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "İsteğiniz işlenirken beklenmedik bir hata oluştu. Lütfen daha sonra tekrar deneyin."
            }
    
    def _analyze_input(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        """
        Kullanıcı girdisini analiz edip intent ve entity'leri çıkarır.
        """
        user_input = user_input.lower().strip()
        entities = {}
        
        # E-posta adresini çıkar
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        email_match = re.search(email_pattern, user_input)
        if email_match:
            entities["email"] = email_match.group()
        
        # İşlem ID'sini çıkar
        transaction_pattern = r'trx\d+|transaction\s+\w+'
        transaction_match = re.search(transaction_pattern, user_input)
        if transaction_match:
            entities["transaction_id"] = transaction_match.group().upper()
        
        # Limit sayısını çıkar
        limit_pattern = r'son\s+(\d+)|(\d+)\s+adet|limit\s+(\d+)'
        limit_match = re.search(limit_pattern, user_input)
        if limit_match:
            limit = limit_match.group(1) or limit_match.group(2) or limit_match.group(3)
            entities["limit"] = int(limit)
        
        # Intent'i belirle
        if any(keyword in user_input for keyword in ["ödeme", "işlem", "transaction"]):
            if any(keyword in user_input for keyword in ["neden", "red", "başarısız", "failed", "hata"]):
                intent = "check_payment_failure"
            elif any(keyword in user_input for keyword in ["geçmiş", "son", "recent"]):
                intent = "get_transaction_history"
            else:
                intent = "payment_inquiry"
        
        elif any(keyword in user_input for keyword in ["hesap", "kullanıcı", "user", "bilgi"]):
            intent = "get_user_info"
        
        elif any(keyword in user_input for keyword in ["aktivite", "analiz", "durum"]):
            intent = "analyze_activity"
        
        elif any(keyword in user_input for keyword in ["yardım", "help", "nasıl"]):
            intent = "help"
        
        else:
            intent = "general_inquiry"
        
        return intent, entities
    
    def _execute_intent(self, intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intent'e göre ilgili araçları çağırır.
        """
        if intent == "check_payment_failure":
            return self._handle_payment_failure(entities)
        
        elif intent == "get_transaction_history":
            return self._get_transaction_history(entities)
        
        elif intent == "get_user_info":
            return self._get_user_info(entities)
        
        elif intent == "analyze_activity":
            return self._analyze_user_activity(entities)
        
        elif intent == "help":
            return self._provide_help()
        
        else:
            return self._handle_general_inquiry(entities)
    
    def _handle_payment_failure(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ödeme başarısızlık durumunu işler.
        """
        if "email" not in entities:
            return {
                "success": False,
                "error": "Ödeme sorunu için e-posta adresi gerekli",
                "message": "Ödeme sorunu sorgulamak için lütfen e-posta adresinizi belirtin. Örnek: 'ali@sirket.com adresli hesabımla dün yapmaya çalıştığım ödeme neden reddedildi?'"
            }
        
        email = entities["email"]
        
        # 1. Kullanıcı detaylarını al
        user_details = self.tool_manager.get_user_details(email)
        user_id = user_details["user_id"]
        
        # 2. Başarısız işlemleri bul
        failed_result = self.tool_manager.get_failed_transactions_for_user(email)
        
        if not failed_result["failed_transactions"]:
            return {
                "success": True,
                "message": f"{email} adresli hesapta başarısız işlem bulunamadı.",
                "user_details": user_details
            }
        
        # 3. En son başarısız işlemin nedenini kontrol et
        latest_failed = failed_result["failed_transactions"][0]
        transaction_id = latest_failed["transaction_id"]
        
        fraud_result = self.tool_manager.check_fraud_reason(transaction_id)
        
        return {
            "success": True,
            "user_details": user_details,
            "failed_transaction": latest_failed,
            "fraud_reason": fraud_result,
            "message": f"{email} adresli hesabınızın en son başarısız işlemi: {fraud_result['fraud_reason']}"
        }
    
    def _get_transaction_history(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        İşlem geçmişini getirir.
        """
        if "email" not in entities:
            return {
                "success": False,
                "error": "İşlem geçmişi için e-posta adresi gerekli",
                "message": "İşlem geçmişi sorgulamak için lütfen e-posta adresinizi belirtin. Örnek: 'ayse@sirket.com adresli hesabımın son 5 işlemini göster'"
            }
        
        email = entities["email"]
        limit = entities.get("limit", 5)
        
        # Kullanıcı detaylarını al
        user_details = self.tool_manager.get_user_details(email)
        user_id = user_details["user_id"]
        
        # İşlemleri getir
        transactions_result = self.tool_manager.get_recent_transactions(user_id, limit)
        
        return {
            "success": True,
            "user_details": user_details,
            "transactions": transactions_result["transactions"],
            "message": f"{email} adresli hesabın son {len(transactions_result['transactions'])} işlemi listelendi."
        }
    
    def _get_user_info(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kullanıcı bilgilerini getirir.
        """
        if "email" not in entities:
            return {
                "success": False,
                "error": "Kullanıcı bilgisi için e-posta adresi gerekli",
                "message": "Kullanıcı bilgisi sorgulamak için lütfen e-posta adresinizi belirtin. Örnek: 'mehmet@sirket.com hakkında bilgi ver'"
            }
        
        email = entities["email"]
        user_details = self.tool_manager.get_user_details(email)
        
        return {
            "success": True,
            "user_details": user_details,
            "message": f"{email} adresli kullanıcı bilgileri getirildi."
        }
    
    def _analyze_user_activity(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kullanıcı aktivitesini analiz eder.
        """
        if "email" not in entities:
            return {
                "success": False,
                "error": "Aktivite analizi için e-posta adresi gerekli",
                "message": "Aktivite analizi için lütfen e-posta adresinizi belirtin. Örnek: 'zeynep@sirket.com adresli hesabın aktivitesini analiz et'"
            }
        
        email = entities["email"]
        analysis_result = self.tool_manager.analyze_user_activity(email)
        
        return {
            "success": True,
            "analysis": analysis_result,
            "message": f"{email} adresli hesabın aktivite analizi tamamlandı."
        }
    
    def _provide_help(self) -> Dict[str, Any]:
        """
        Yardım bilgisi sağlar.
        """
        help_text = """
        Yardım Menüsü:
        
        1. Ödeme sorunları için: "ali@sirket.com adresli hesabımla dün yapmaya çalıştığım ödeme neden reddedildi?"
        2. İşlem geçmişi için: "ayse@sirket.com adresli hesabımın son 5 işlemini göster"
        3. Kullanıcı bilgileri için: "mehmet@sirket.com hakkında bilgi ver"
        4. Aktivite analizi için: "zeynep@sirket.com adresli hesabın aktivitesini analiz et"
        
        Not: İşlemler için e-posta adresini belirtmeniz gerekmektedir.
        """
        
        return {
            "success": True,
            "help_text": help_text,
            "message": "Yardım menüsü gösterildi."
        }
    
    def _handle_general_inquiry(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genel soruları işler.
        """
        return {
            "success": True,
            "message": "Sorunuzu anlayamadım. 'yardım' yazarak kullanım talimatlarını görebilirsiniz.",
            "suggestions": [
                "Ödeme sorunlarını sorgulamak için e-posta adresinizi belirtin",
                "İşlem geçmişini görmek için e-posta adresinizi belirtin",
                "Kullanıcı bilgilerini öğrenmek için e-posta adresinizi belirtin"
            ]
        }
    
    def _format_response(self, result: Dict[str, Any], intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        API yanıtını kullanıcı dostu formata çevirir.
        """
        if not result.get("success", False):
            return result
        
        # Başarılı yanıtları formatla
        formatted_response = {
            "success": True,
            "message": result.get("message", "İşlem başarılı"),
            "intent": intent,
            "entities": entities
        }
        
        # İntent'e göre ek bilgiler ekle
        if intent == "check_payment_failure":
            user = result.get("user_details", {})
            fraud = result.get("fraud_reason", {})
            formatted_response["details"] = {
                "kullanici": f"{user.get('name', 'Bilinmeyen')} ({user.get('email', 'Bilinmeyen')})",
                "islem_tutari": f"{fraud.get('transaction_amount', 0)} TL",
                "red_sebebi": fraud.get('fraud_reason', 'Belirtilmemiş'),
                "islem_id": fraud.get('transaction_id', 'Bilinmeyen')
            }
        
        elif intent == "get_transaction_history":
            user = result.get("user_details", {})
            transactions = result.get("transactions", [])
            formatted_response["details"] = {
                "kullanici": f"{user.get('name', 'Bilinmeyen')} ({user.get('email', 'Bilinmeyen')})",
                "islem_sayisi": len(transactions),
                "islemler": [
                    {
                        "id": tx.get("transaction_id"),
                        "tutar": f"{tx.get('amount', 0)} TL",
                        "durum": tx.get("status"),
                        "tarih": tx.get("timestamp"),
                        "aciklama": tx.get("description")
                    }
                    for tx in transactions
                ]
            }
        
        elif intent == "get_user_info":
            user = result.get("user_details", {})
            formatted_response["details"] = {
                "kullanici_adi": user.get("name"),
                "e_posta": user.get("email"),
                "durum": user.get("status"),
                "kayit_tarihi": user.get("created_date"),
                "son_giris": user.get("last_login")
            }
        
        elif intent == "analyze_activity":
            analysis = result.get("analysis", {})
            user = analysis.get("user_details", {})
            formatted_response["details"] = {
                "kullanici": f"{user.get('name', 'Bilinmeyen')} ({user.get('email', 'Bilinmeyen')})",
                "toplam_islem": analysis.get("total_transactions", 0),
                "basarili_islem": analysis.get("successful_transactions", 0),
                "basarisiz_islem": analysis.get("failed_transactions", 0),
                "basari_orani": f"{analysis.get('success_rate', 0):.1f}%",
                "toplam_tutar": f"{analysis.get('total_amount', 0):.2f} TL"
            }
        
        elif intent == "help":
            formatted_response["details"] = {
                "yardim_metni": result.get("help_text", "")
            }
        
        return formatted_response
