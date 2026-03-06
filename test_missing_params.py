#!/usr/bin/env python3
"""
Eksik parametre ve hata senaryolarını test etmek için
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent import ToolCallingAgent

def test_error_scenarios():
    """Hata senaryolarını test eder"""
    agent = ToolCallingAgent()
    
    print("=== Hata Senaryoları Testi ===\n")
    
    # Test 1: E-posta olmadan ödeme sorugu
    print("Test 1: E-posta olmadan ödeme sorugu")
    result = agent.process_request("dün yaptığım ödeme neden reddedildi?")
    print(f"Sonuç: {result['message']}")
    print(f"Başarılı: {result.get('success', False)}")
    print()
    
    # Test 2: Geçersiz e-posta formatı
    print("Test 2: Geçersiz e-posta formatı")
    result = agent.process_request("invalid-email adresli hesabın ödemesi neden reddedildi?")
    print(f"Sonuç: {result['message']}")
    print(f"Başarılı: {result.get('success', False)}")
    print()
    
    # Test 3: Var olmayan kullanıcı
    print("Test 3: Var olmayan kullanıcı")
    result = agent.process_request("nonexistent@company.com adresli hesabın bilgilerini göster")
    print(f"Sonuç: {result['message']}")
    print(f"Başarılı: {result.get('success', False)}")
    print()
    
    # Test 4: Anlaşılamayan sorgu
    print("Test 4: Anlaşılamayan sorgu")
    result = agent.process_request("random text that makes no sense")
    print(f"Sonuç: {result['message']}")
    print(f"Başarılı: {result.get('success', False)}")
    print()

if __name__ == "__main__":
    test_error_scenarios()
