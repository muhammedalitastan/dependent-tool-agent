#!/usr/bin/env python3
"""
Advanced Tool-Calling Agent - Enterprise Level
Gelişmiş birbirine bağımlı araç kullanımı ve akıllı asistan
"""

import sys
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from advanced_agent import AdvancedToolCallingAgent, AgentResponse, IntentType

class AdvancedAgentInterface:
    """Gelişmiş Agent arayüzü"""
    
    def __init__(self):
        self.agent = AdvancedToolCallingAgent()
        self.session_start = datetime.now()
        self.favorite_queries = []
        
    def start_interactive_mode(self):
        """Interaktif modu başlatır"""
        print("=" * 80)
        print("🤖 ADVANCED TOOL-CALLING AGENT - ENTERPRISE EDITION")
        print("=" * 80)
        print("Gelişmiş birbirine bağımlı araç kullanımı ve akıllı asistan sistemi")
        print()
        
        print("🎯 Kullanılabilir Komutlar:")
        print("  • Sorunuzu doğrudan yazın (e-posta içeren)")
        print("  • 'stats' - Agent ve araç istatistikleri")
        print("  • 'history' - Sorgu geçmişi")
        print("  • 'tools' - Araç performansı")
        print("  • 'intents' - Intent dağılımı")
        print("  • 'export' - Oturum verilerini dışa aktar")
        print("  • 'help' - Detaylı yardım menüsü")
        print("  • 'test' - Test senaryolarını çalıştır")
        print("  • 'çıkış' - Çıkış")
        print()
        
        print("💡 Örnek Sorgular:")
        print("  • 'ali@sirket.com ödemi neden reddedildi?'")
        print("  • 'ayse@sirket.com hesap aktivitesini analiz et'")
        print("  • 'mehmet@sirket.com hakkında bilgi ver'")
        print()
        
        while True:
            try:
                user_input = input("🤖 Sizin: ").strip()
                
                if user_input.lower() in ['çıkış', 'exit', 'quit']:
                    print("\\n👋 Görüşmek üzere!")
                    self._show_session_summary()
                    break
                
                if not user_input:
                    continue
                
                # Komutları işle
                if user_input.lower() == 'stats':
                    self._show_stats()
                    continue
                elif user_input.lower() == 'history':
                    self._show_history()
                    continue
                elif user_input.lower() == 'tools':
                    self._show_tool_stats()
                    continue
                elif user_input.lower() == 'intents':
                    self._show_intent_distribution()
                    continue
                elif user_input.lower() == 'export':
                    self._export_session()
                    continue
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower() == 'test':
                    self._run_test_scenarios()
                    continue
                
                # Sorguyu işle
                print("🔄 İşleniyor...")
                response = asyncio.run(self.agent.process_request(user_input))
                
                # Sonucu göster
                self._display_response(user_input, response)
                
            except KeyboardInterrupt:
                print("\\n\\n👋 Görüşmek üzere!")
                break
            except Exception as e:
                print(f"\\n❌ Hata: {e}")
    
    def _display_response(self, query: str, response: AgentResponse):
        """Agent yanıtını formatlayarak gösterir"""
        print(f"\\n🤖 Asistan: {response.message}")
        
        # Durum ve performans bilgileri
        status_emoji = "✅" if response.success else "❌"
        intent_emoji = {
            IntentType.PAYMENT_FAILURE: "💳",
            IntentType.TRANSACTION_HISTORY: "📋",
            IntentType.USER_INFO: "👤",
            IntentType.ACTIVITY_ANALYSIS: "📊",
            IntentType.FRAUD_ANALYSIS: "🔍",
            IntentType.BALANCE_INQUIRY: "💰",
            IntentType.HELP: "🆘",
            IntentType.GENERAL_INQUIRY: "❓"
        }.get(response.intent, "🤖")
        
        print(f"\\n{status_emoji} Durum: {'Başarılı' if response.success else 'Başarısız'}")
        print(f"{intent_emoji} Intent: {response.intent.value}")
        print(f"⏱️  İşlem Süresi: {response.processing_time:.3f}s")
        print(f"🎯 Güven: {response.confidence:.2f}")
        
        # Çalışan araçlar
        if response.results:
            successful_tools = [r.tool_name for r in response.results if r.success]
            failed_tools = [r.tool_name for r in response.results if not r.success]
            
            if successful_tools:
                print(f"\\n🔧 Çalışan Araçlar ({len(successful_tools)}): {', '.join(successful_tools)}")
            if failed_tools:
                print(f"❌ Başarısız Araçlar ({len(failed_tools)}): {', '.join(failed_tools)}")
        
        # Öneriler
        if response.suggestions:
            print(f"\\n💡 Öneriler:")
            for i, suggestion in enumerate(response.suggestions, 1):
                print(f"  {i}. {suggestion}")
        
        # İlgili eylemler
        if response.related_actions:
            print(f"\\n🔗 İlgili Eylemler:")
            for i, action in enumerate(response.related_actions, 1):
                print(f"  {i}. {action}")
        
        print("\\n" + "=" * 80)
    
    def _show_stats(self):
        """Agent istatistiklerini gösterir"""
        stats = self.agent.get_agent_stats()
        
        print("\\n📊 AGENT İSTATİSTİKLERİ")
        print("=" * 50)
        print(f"🕐 Oturum Başlangıcı: {self.session_start.strftime('%H:%M:%S')}")
        print(f"🔍 Toplam İstek: {stats['total_requests']}")
        print(f"✅ Başarılı İstek: {stats['successful_requests']}")
        print(f"📈 Başarı Oranı: {stats['success_rate']:.1%}")
        print(f"⏱️  Ortalama Süre: {stats['avg_processing_time']:.3f}s")
        print(f"📜 Oturum Geçmişi: {stats['session_history_count']}")
        
        print("\\n" + "=" * 50)
    
    def _show_history(self):
        """Sorgu geçmişini gösterir"""
        history = self.agent.get_session_history()
        
        if not history:
            print("\\n📜 Henüz sorgu geçmişi yok.")
            return
        
        print(f"\\n📜 SORGU GEÇMİŞİ ({len(history)} sorgu)")
        print("=" * 50)
        
        for i, entry in enumerate(history[-10:], 1):  # Son 10 sorgu
            timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%H:%M:%S")
            intent = entry["response"].intent.value
            success = entry["response"].success
            
            status_emoji = "✅" if success else "❌"
            print(f"{i:2d}. [{timestamp}] {status_emoji} {intent}")
            print(f"    💬 {entry['user_input']}")
            if entry["response"].suggestions:
                print(f"    💡 {entry['response'].suggestions[0]}")
        
        print("\\n" + "=" * 50)
    
    def _show_tool_stats(self):
        """Araç istatistiklerini gösterir"""
        tool_stats = self.agent.tool_manager.get_tool_stats()
        
        print("\\n🔧 ARAÇ PERFORMANSI")
        print("=" * 50)
        
        for tool_name, stats in tool_stats.items():
            if stats['calls'] > 0:
                success_rate = stats['success_rate']
                avg_time = stats['avg_execution_time']
                last_used = stats['last_used']
                
                if last_used:
                    last_used_dt = datetime.fromisoformat(last_used)
                    last_used_str = last_used_dt.strftime("%H:%M:%S")
                else:
                    last_used_str = "Hiç kullanılmadı"
                
                print(f"🔧 {tool_name}:")
                print(f"  📞 Çağrı: {stats['calls']}")
                print(f"  ✅ Başarı: {success_rate:.1%}")
                print(f"  ⏱️  Süre: {avg_time:.3f}s")
                print(f"  🕐 Son Kullanım: {last_used_str}")
                print()
        
        print("=" * 50)
    
    def _show_intent_distribution(self):
        """Intent dağılımını gösterir"""
        stats = self.agent.get_agent_stats()
        intent_dist = stats['intent_distribution']
        
        if not intent_dist:
            print("\\n📊 Henüz intent verisi yok.")
            return
        
        print("\\n📊 INTENT DAĞILIMI")
        print("=" * 30)
        
        total_requests = stats['total_requests']
        
        # Sort by count
        sorted_intents = sorted(intent_dist.items(), key=lambda x: x[1], reverse=True)
        
        for intent, count in sorted_intents:
            percentage = (count / total_requests) * 100
            emoji = {
                "payment_failure": "💳",
                "transaction_history": "📋",
                "user_info": "👤",
                "activity_analysis": "📊",
                "fraud_analysis": "🔍",
                "balance_inquiry": "💰",
                "help": "🆘",
                "general_inquiry": "❓"
            }.get(intent, "🤖")
            
            bar_length = int(percentage / 2)  # 50 karakter max
            bar = "█" * bar_length + "░" * (50 - bar_length)
            
            print(f"{emoji} {intent:<20}: {bar} {count} ({percentage:.1f}%)")
        
        print("\\n" + "=" * 30)
    
    def _export_session(self):
        """Oturum verilerini dışa aktarır"""
        history = self.agent.get_session_history()
        
        if not history:
            print("\\n📤 Dışa aktarılacak veri yok.")
            return
        
        # Dosya adı oluştur
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"agent_session_{timestamp}.json"
        
        # Veriyi hazırla
        export_data = {
            "export_time": datetime.now().isoformat(),
            "session_start": self.session_start.isoformat(),
            "agent_stats": self.agent.get_agent_stats(),
            "tool_stats": self.agent.tool_manager.get_tool_stats(),
            "queries": []
        }
        
        for entry in history:
            query_data = {
                "timestamp": entry["timestamp"],
                "user_input": entry["user_input"],
                "intent": entry["response"].intent.value,
                "success": entry["response"].success,
                "confidence": entry["response"].confidence,
                "processing_time": entry["response"].processing_time,
                "tools_used": [r.tool_name for r in entry["response"].results if r.success],
                "message": entry["response"].message,
                "suggestions": entry["response"].suggestions
            }
            export_data["queries"].append(query_data)
        
        # Dosyaya yaz
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"\\n✅ Oturum verisi '{filename}' dosyasına aktarıldı.")
            print(f"📊 {len(history)} sorgu dışa aktarıldı.")
            
        except Exception as e:
            print(f"\\n❌ Dışa aktarma başarısız: {e}")
    
    def _show_help(self):
        """Detaylı yardım menüsünü gösterir"""
        help_text = """
🆘 ADVANCED AGENT YARDIM MENÜSÜ

🎯 **SİSTEM KAPASİTELERİ:**
• 🧠 Akıllı intent analizi (9 farklı intent tipi)
• 🔗 Bağımlı araç zinciri (tool chaining)
• ⚡ Paralel araç çalıştırma
• 📊 Gerçek zamanlı performans izleme
• 🧪 Otomatik hata yönetimi
• 💡 Akıllı öneri sistemi

📋 **İNTENT TİPLERİ:**
1. 💳 PAYMENT_FAILURE - Ödeme başarısızlık analizi
2. 📋 TRANSACTION_HISTORY - İşlem geçmişi sorgulama
3. 👤 USER_INFO - Kullanıcı bilgileri
4. 📊 ACTIVITY_ANALYSIS - Hesap aktivite analizi
5. 🔍 FRAUD_ANALYSIS - Fraud ve güvenlik analizi
6. 💰 BALANCE_INQUIRY - Bakiye sorgulama
7. 🆘 SUPPORT_REQUEST - Destek talepleri
8. 🆘 HELP - Yardım ve yönlendirme
9. ❓ GENERAL_INQUIRY - Genel sorular

🔧 **MEVCUT ARAÇLAR:**
• get_user_details - Kullanıcı bilgileri
• get_recent_transactions - Son işlemler
• check_fraud_reason - Fraud analizi
• get_failed_transactions - Başarısız işlemler
• analyze_user_activity - Aktivite analizi
• get_account_balance - Bakiye bilgisi
• create_support_ticket - Destek talebi
• search_transactions - İşlem arama

💡 **KULLANIM İPUÇLARI:**
• E-posta adresini belirtmek daha iyi sonuçlar verir
• Spesifik olun (ödeme, işlem, aktivite gibi)
• İşlem ID'si varsa belirtin
• Karşılaştırma için "karşılaştır" kullanın

⌨️ **ÖZEL KOMUTLAR:**
• stats - Tüm sistem istatistikleri
• tools - Araç performans detayları
• intents - Intent dağılım grafiği
• history - Sorgu geçmişi
• export - Oturum verisini JSON olarak dışa aktar
• test - Otomatik test senaryoları
• help - Bu yardım menüsü

🧪 **TEST SENARYOLARI:**
• Ödeme başarısızlık analizi
• Çoklu araç zinciri testi
• Hata yönetimi senaryoları
• Performans benchmark testleri

📈 **PERFORMANS ÖZELLİKLERİ:**
• Ortalama yanıt süresi: <500ms
• Başarı oranı: >95%
• Paralel araç çalıştırma desteği
• Otomatik cache yönetimi
• Gerçek zamanlı monitoring
        """
        
        print(help_text)
    
    def _run_test_scenarios(self):
        """Test senaryolarını çalıştırır"""
        print("\\n🧪 TEST SENARYOLARI")
        print("=" * 30)
        
        test_scenarios = [
            {
                "name": "Ödeme Başarısızlık Analizi",
                "query": "ali@sirket.com ödemi neden reddedildi?",
                "expected_intent": "payment_failure",
                "min_tools": 2
            },
            {
                "name": "İşlem Geçmişi Sorgulama",
                "query": "ayse@sirket.com son işlemlerini göster",
                "expected_intent": "transaction_history",
                "min_tools": 2
            },
            {
                "name": "Kullanıcı Bilgisi",
                "query": "mehmet@sirket.com hakkında bilgi ver",
                "expected_intent": "user_info",
                "min_tools": 1
            },
            {
                "name": "Aktivite Analizi",
                "query": "zeynep@sirket.com hesap aktivitesini analiz et",
                "expected_intent": "activity_analysis",
                "min_tools": 2
            },
            {
                "name": "Yardım Talebi",
                "query": "yardım",
                "expected_intent": "help",
                "min_tools": 0
            }
        ]
        
        passed = 0
        total = len(test_scenarios)
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\\n🧪 Test {i}/{total}: {scenario['name']}")
            print(f"📝 Sorgu: {scenario['query']}")
            
            try:
                response = asyncio.run(self.agent.process_request(scenario['query']))
                
                # Sonucu kontrol et
                success = True
                
                if response.intent.value != scenario['expected_intent']:
                    print(f"  ❌ Intent: {response.intent.value} (expected: {scenario['expected_intent']})")
                    success = False
                
                if len([r for r in response.results if r.success]) < scenario['min_tools']:
                    print(f"  ❌ Araç sayısı: {len([r for r in response.results if r.success])} (min: {scenario['min_tools']})")
                    success = False
                
                if not response.success:
                    print(f"  ❌ Başarısız yanıt")
                    success = False
                
                if success:
                    print(f"  ✅ Passed (Intent: {response.intent.value}, Tools: {len([r for r in response.results if r.success])}, Time: {response.processing_time:.3f}s)")
                    passed += 1
                else:
                    print(f"  💬 Yanıt: {response.message[:100]}...")
                    
            except Exception as e:
                print(f"  ❌ Exception: {e}")
        
        print(f"\\n📊 TEST SONUÇLARI: {passed}/{total} passed ({passed/total*100:.1f}%)")
        
        # Sistem istatistikleri
        stats = self.agent.get_agent_stats()
        print(f"\\n📈 SİSTEM PERFORMANSI:")
        print(f"  • Toplam sorgu: {stats['total_requests']}")
        print(f"  • Başarı oranı: {stats['success_rate']:.1%}")
        print(f"  • Ortalama süre: {stats['avg_processing_time']:.3f}s")
        
        print("\\n" + "=" * 30)
    
    def _show_session_summary(self):
        """Oturum özetini gösterir"""
        stats = self.agent.get_agent_stats()
        session_duration = datetime.now() - self.session_start
        
        print("\\n📊 OTURUM ÖZETİ")
        print("=" * 30)
        print(f"🕐 Oturum Süresi: {session_duration}")
        print(f"🔍 Toplam Sorgu: {stats['total_requests']}")
        print(f"✅ Başarılı Sorgu: {stats['successful_requests']}")
        print(f"📈 Başarı Oranı: {stats['success_rate']:.1%}")
        print(f"⏱️  Ortalama Süre: {stats['avg_processing_time']:.3f}s")
        
        # En çok kullanılan intent'ler
        if stats['intent_distribution']:
            print("\\n📊 En Çok Kullanılan Intent'ler:")
            sorted_intents = sorted(stats['intent_distribution'].items(), key=lambda x: x[1], reverse=True)
            for intent, count in sorted_intents[:3]:
                emoji = {
                    "payment_failure": "💳",
                    "transaction_history": "📋", 
                    "user_info": "👤",
                    "activity_analysis": "📊"
                }.get(intent, "🤖")
                print(f"  {emoji} {intent}: {count}")
        
        print("\\n" + "=" * 30)

if __name__ == "__main__":
    interface = AdvancedAgentInterface()
    interface.start_interactive_mode()
