#!/usr/bin/env python3
"""
Tool-Calling Agent Ana Uygulaması
Birbirine bağımlı araç kullanımı ile kullanıcı taleplerini işleyen agent
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent import ToolCallingAgent

def main():
    """Ana uygulama fonksiyonu"""
    print("=== Tool-Calling Agent Sistemi ===")
    print("Kullanıcı taleplerini analiz eden ve gerekli araçları çağıran akıllı asistan.")
    print("Sistem başlatılıyor...\n")
    
    # Agent'ı başlat
    agent = ToolCallingAgent()
    
    print("Sistem hazır! Sorularınızı yazabilirsiniz.")
    print("Çıkmak için 'çıkış' yazın, yardım için 'yardım' yazın.\n")
    
    while True:
        try:
            user_input = input("Siz: ").strip()
            
            if user_input.lower() in ['çıkış', 'exit', 'quit']:
                print("Güle güle!")
                break
            
            if not user_input:
                continue
            
            # Kullanıcı talebini işle
            result = agent.process_request(user_input)
            
            print(f"\nAsistan: {result['message']}")
            
            # Detayları göster
            if result.get('success') and 'details' in result:
                details = result['details']
                print("\nDetaylar:")
                
                if 'kullanici' in details:
                    print(f"  Kullanıcı: {details['kullanici']}")
                
                if 'islem_tutari' in details:
                    print(f"  İşlem Tutari: {details['islem_tutari']}")
                    print(f"  Red Sebebi: {details['red_sebebi']}")
                    print(f"  İşlem ID: {details['islem_id']}")
                
                if 'islem_sayisi' in details:
                    print(f"  İşlem Sayısı: {details['islem_sayisi']}")
                    if details.get('islemler'):
                        print("  Son İşlemler:")
                        for i, islem in enumerate(details['islemler'][:3], 1):
                            print(f"    {i}. {islem['id']} - {islem['tutar']} - {islem['durum']} - {islem['aciklama']}")
                
                if 'kullanici_adi' in details:
                    print(f"  Adı: {details['kullanici_adi']}")
                    print(f"  E-posta: {details['e_posta']}")
                    print(f"  Durum: {details['durum']}")
                    print(f"  Kayıt Tarihi: {details['kayit_tarihi']}")
                
                if 'toplam_islem' in details:
                    print(f"  Toplam İşlem: {details['toplam_islem']}")
                    print(f"  Başarılı İşlem: {details['basarili_islem']}")
                    print(f"  Başarısız İşlem: {details['basarisiz_islem']}")
                    print(f"  Başarı Oranı: {details['basari_orani']}")
                    print(f"  Toplam Tutar: {details['toplam_tutar']}")
                
                if 'yardim_metni' in details:
                    print(details['yardim_metni'])
            
            # Hata durumunda
            if not result.get('success'):
                print(f"Hata: {result.get('error', 'Bilinmeyen hata')}")
            
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\nGüle güle!")
            break
        except Exception as e:
            print(f"Sistem hatası: {e}")

def test_examples():
    """Örnek senaryolarla test fonksiyonu"""
    print("=== Test Modu ===\n")
    
    agent = ToolCallingAgent()
    
    test_scenarios = [
        "ali@sirket.com adresli hesabımla dün yapmaya çalıştığım ödeme neden reddedildi?",
        "ayse@sirket.com adresli hesabımın son 3 işlemini göster",
        "mehmet@sirket.com hakkında bilgi ver",
        "zeynep@sirket.com adresli hesabın aktivitesini analiz et",
        "yardım"
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"Test {i}: {scenario}")
        result = agent.process_request(scenario)
        
        print(f"Sonuç: {result['message']}")
        if result.get('details'):
            print("Detaylar mevcut")
        print(f"Başarılı: {result.get('success', False)}")
        print("-" * 50)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_examples()
    else:
        main()
