#!/usr/bin/env python3
"""
Advanced Tool-Calling Agent Test Suite
Kapsamlı test ve doğrulama sistemleri
"""

import sys
import os
import json
import unittest
import asyncio
from datetime import datetime
from typing import Dict, Any, List

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from advanced_agent import (
    AdvancedToolCallingAgent, 
    IntentType, 
    Priority, 
    ExecutionStatus
)

class TestAdvancedAgent(unittest.TestCase):
    """Advanced Agent test sınıfı"""
    
    def setUp(self):
        """Test setup"""
        self.agent = AdvancedToolCallingAgent()
        self.test_scenarios = [
            {
                "name": "Payment Failure Analysis",
                "query": "ali@sirket.com ödemi neden reddedildi?",
                "expected_intent": IntentType.PAYMENT_FAILURE,
                "min_tools": 2,
                "min_confidence": 0.7
            },
            {
                "name": "Transaction History",
                "query": "ayse@sirket.com son işlemlerini göster",
                "expected_intent": IntentType.TRANSACTION_HISTORY,
                "min_tools": 2,
                "min_confidence": 0.7
            },
            {
                "name": "User Information",
                "query": "mehmet@sirket.com hakkında bilgi ver",
                "expected_intent": IntentType.USER_INFO,
                "min_tools": 1,
                "min_confidence": 0.7
            },
            {
                "name": "Activity Analysis",
                "query": "zeynep@sirket.com hesap aktivitesini analiz et",
                "expected_intent": IntentType.ACTIVITY_ANALYSIS,
                "min_tools": 2,
                "min_confidence": 0.7
            },
            {
                "name": "Help Request",
                "query": "yardım",
                "expected_intent": IntentType.HELP,
                "min_tools": 0,
                "min_confidence": 0.5
            }
        ]
    
    async def test_intent_analysis(self):
        """Intent analizi testi"""
        analyzer = self.agent.intent_analyzer
        
        test_cases = [
            ("ali@sirket.com ödemi neden reddedildi?", IntentType.PAYMENT_FAILURE),
            ("ayse@sirket.com son işlemlerini göster", IntentType.TRANSACTION_HISTORY),
            ("mehmet@sirket.com hakkında bilgi ver", IntentType.USER_INFO),
            ("hesap aktivitesini analiz et", IntentType.ACTIVITY_ANALYSIS),
            ("yardım", IntentType.HELP)
        ]
        
        for query, expected_intent in test_cases:
            with self.subTest(query=query):
                detected_intent, entities, confidence = analyzer.analyze(query)
                
                self.assertEqual(detected_intent, expected_intent)
                self.assertGreater(confidence, 0.5)
                self.assertIsInstance(entities, dict)
    
    async def test_tool_execution(self):
        """Araç çalıştırma testi"""
        tool_manager = self.agent.tool_manager
        
        # Test user details tool
        result = await tool_manager.execute_tool("get_user_details", email="ali@sirket.com")
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertEqual(result.tool_name, "get_user_details")
        self.assertGreater(result.execution_time, 0)
    
    async def test_execution_planning(self):
        """İşlem planlama testi"""
        planner = self.agent.execution_planner
        
        # Test payment failure plan
        intent = IntentType.PAYMENT_FAILURE
        entities = {"email": ["ali@sirket.com"]}
        
        plan = planner.create_execution_plan(intent, entities)
        
        self.assertEqual(plan.intent, intent)
        self.assertIn("get_user_details", plan.tools)
        self.assertGreater(len(plan.tools), 0)
        self.assertIsInstance(plan.priority, Priority)
    
    async def test_plan_execution(self):
        """Plan çalıştırma testi"""
        planner = self.agent.execution_planner
        
        # Create and execute plan
        intent = IntentType.PAYMENT_FAILURE
        entities = {"email": ["ali@sirket.com"]}
        
        plan = planner.create_execution_plan(intent, entities)
        results = await planner.execute_plan(plan)
        
        self.assertGreater(len(results), 0)
        
        # Check if at least one tool succeeded
        successful_tools = [r for r in results if r.success]
        self.assertGreater(len(successful_tools), 0)
    
    async def test_end_to_end_scenarios(self):
        """Uçtan uca senaryo testleri"""
        for scenario in self.test_scenarios:
            with self.subTest(scenario=scenario["name"]):
                response = await self.agent.process_request(scenario["query"])
                
                # Response validation
                self.assertIsNotNone(response)
                self.assertEqual(response.intent, scenario["expected_intent"])
                self.assertGreaterEqual(response.confidence, scenario["min_confidence"])
                
                # Tool execution validation
                successful_tools = [r for r in response.results if r.success]
                self.assertGreaterEqual(len(successful_tools), scenario["min_tools"])
                
                # Response content validation
                self.assertIsNotNone(response.message)
                self.assertGreater(len(response.message), 0)
    
    async def test_error_handling(self):
        """Hata yönetimi testi"""
        # Test with invalid email
        response = await self.agent.process_request("invalid@email.com ödemi neden reddedildi?")
        
        # Should still return a response, but with lower confidence
        self.assertIsNotNone(response)
        self.assertGreaterEqual(response.confidence, 0.0)
        
        # Test with empty query
        response = await self.agent.process_request("")
        
        self.assertIsNotNone(response)
        self.assertEqual(response.intent, IntentType.GENERAL_INQUIRY)
    
    async def test_concurrent_requests(self):
 """Eş zamanlı istek testi"""
        queries = [
            "ali@sirket.com ödemi neden reddedildi?",
            "ayse@sirket.com hakkında bilgi ver",
            "mehmet@sirket.com son işlemlerini göster"
        ]
        
        # Run queries concurrently
        tasks = [self.agent.process_request(query) for query in queries]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check all responses
        self.assertEqual(len(responses), len(queries))
        
        for response in responses:
            self.assertNotIsInstance(response, Exception)
            self.assertIsNotNone(response)
    
    async def test_performance_benchmarks(self):
        """Performans benchmark testi"""
        query = "ali@sirket.com hakkında bilgi ver"
        
        # Run multiple times and measure
        times = []
        
        for _ in range(10):
            start_time = datetime.now()
            response = await self.agent.process_request(query)
            end_time = datetime.now()
            
            execution_time = (end_time - start_time).total_seconds()
            times.append(execution_time)
        
        avg_time = sum(times) / len(times)
        
        # Should complete within 1 second on average
        self.assertLess(avg_time, 1.0)
        
        # Check consistency (standard deviation)
        variance = sum((t - avg_time) ** 2 for t in times) / len(times)
        std_dev = variance ** 0.5
        
        # Should be consistent (std dev < 0.5s)
        self.assertLess(std_dev, 0.5)
    
    def test_agent_statistics(self):
        """Agent istatistikleri testi"""
        stats = self.agent.get_agent_stats()
        
        # Check required fields
        required_fields = [
            "total_requests", "successful_requests", "avg_processing_time",
            "intent_distribution", "session_start", "tool_stats"
        ]
        
        for field in required_fields:
            self.assertIn(field, stats)
        
        # Check tool stats
        self.assertIsInstance(stats["tool_stats"], dict)
        
        for tool_name, tool_stats in stats["tool_stats"].items():
            self.assertIn("calls", tool_stats)
            self.assertIn("success_rate", tool_stats)
            self.assertIn("avg_execution_time", tool_stats)
    
    async def test_session_history(self):
        """Oturum geçmişi testi"""
        # Make some requests
        queries = [
            "ali@sirket.com hakkında bilgi ver",
            "yardım",
            "ayse@sirket.com son işlemlerini göster"
        ]
        
        for query in queries:
            await self.agent.process_request(query)
        
        # Check session history
        history = self.agent.get_session_history()
        
        self.assertEqual(len(history), len(queries))
        
        for entry in history:
            self.assertIn("user_input", entry)
            self.assertIn("response", entry)
            self.assertIn("timestamp", entry)
    
    async def test_entity_extraction(self):
        """Entity extraction testi"""
        analyzer = self.agent.intent_analyzer
        
        test_cases = [
            ("ali@sirket.com ödemi neden reddedildi?", {"email": ["ali@sirket.com"]}),
            ("TRX001 işlemi neden başarısız?", {"transaction_id": ["TRX001"]}),
            ("son 5 işlemi göster", {"limit": ["5"]}),
            ("USR001 kullanıcısını bul", {"user_id": ["USR001"]})
        ]
        
        for query, expected_entities in test_cases:
            with self.subTest(query=query):
                intent, entities, confidence = analyzer.analyze(query)
                
                for entity_type, expected_values in expected_entities.items():
                    if entity_type in entities:
                        self.assertEqual(entities[entity_type], expected_values)

class TestToolManager(unittest.TestCase):
    """Tool Manager test sınıfı"""
    
    def setUp(self):
        """Test setup"""
        from advanced_agent import AdvancedToolManager
        self.tool_manager = AdvancedToolManager()
    
    async def test_tool_registration(self):
        """Araç kayıt testi"""
        # Check if all required tools are registered
        required_tools = [
            "get_user_details",
            "get_recent_transactions", 
            "check_fraud_reason",
            "get_failed_transactions",
            "analyze_user_activity",
            "get_account_balance",
            "create_support_ticket",
            "search_transactions"
        ]
        
        for tool_name in required_tools:
            self.assertIn(tool_name, self.tool_manager.tools)
    
    async def test_tool_stats_tracking(self):
        """Araç istatistik takibi testi"""
        # Execute a tool
        result = await self.tool_manager.execute_tool("get_user_details", email="ali@sirket.com")
        
        # Check stats
        stats = self.tool_manager.get_tool_stats()
        tool_stats = stats["get_user_details"]
        
        self.assertGreater(tool_stats["calls"], 0)
        self.assertGreaterEqual(tool_stats["success_rate"], 0.0)
        self.assertLessEqual(tool_stats["success_rate"], 1.0)
        self.assertGreater(tool_stats["avg_execution_time"], 0.0)
    
    async def test_tool_error_handling(self):
        """Araç hata yönetimi testi"""
        # Test with missing required parameter
        result = await self.tool_manager.execute_tool("get_user_details")
        
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
        self.assertEqual(result.tool_name, "get_user_details")

async def run_performance_test():
    """Performans testi çalıştırır"""
    print("🚀 AGENT PERFORMANCE TEST")
    print("=" * 50)
    
    agent = AdvancedToolCallingAgent()
    
    # Test scenarios
    scenarios = [
        "ali@sirket.com ödemi neden reddedildi?",
        "ayse@sirket.com hakkında bilgi ver",
        "mehmet@sirket.com hesap aktivitesini analiz et",
        "yardım"
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\\n🧪 Testing: {scenario}")
        
        # 10 kez çalıştır ve ortalamasını al
        times = []
        confidences = []
        tool_counts = []
        
        for i in range(10):
            start_time = datetime.now()
            response = await agent.process_request(scenario)
            end_time = datetime.now()
            
            times.append((end_time - start_time).total_seconds())
            confidences.append(response.confidence)
            tool_counts.append(len([r for r in response.results if r.success]))
        
        avg_time = sum(times) / len(times)
        avg_confidence = sum(confidences) / len(confidences)
        avg_tools = sum(tool_counts) / len(tool_counts)
        
        min_time = min(times)
        max_time = max(times)
        
        print(f"  ⏱️  Avg Time: {avg_time:.3f}s")
        print(f"  🎯 Avg Confidence: {avg_confidence:.3f}")
        print(f"  🔧 Avg Tools: {avg_tools:.1f}")
        print(f"  📈 Time Range: {min_time:.3f}s - {max_time:.3f}s")
        
        results.append({
            "scenario": scenario,
            "avg_time": avg_time,
            "avg_confidence": avg_confidence,
            "avg_tools": avg_tools,
            "min_time": min_time,
            "max_time": max_time
        })
    
    # Genel özet
    print(f"\\n📊 PERFORMANCE SUMMARY")
    print("=" * 30)
    
    overall_avg_time = sum(r["avg_time"] for r in results) / len(results)
    overall_avg_confidence = sum(r["avg_confidence"] for r in results) / len(results)
    overall_avg_tools = sum(r["avg_tools"] for r in results) / len(results)
    
    print(f"🕐 Overall Avg Time: {overall_avg_time:.3f}s")
    print(f"🎯 Overall Avg Confidence: {overall_avg_confidence:.3f}")
    print(f"🔧 Overall Avg Tools: {overall_avg_tools:.1f}")
    
    # Performans kriterleri
    if overall_avg_time < 0.5:
        print("✅ Excellent performance (< 500ms)")
    elif overall_avg_time < 1.0:
        print("✅ Good performance (< 1s)")
    else:
        print("⚠️  Needs optimization (> 1s)")
    
    if overall_avg_confidence > 0.8:
        print("✅ High confidence (> 0.8)")
    elif overall_avg_confidence > 0.6:
        print("✅ Good confidence (> 0.6)")
    else:
        print("⚠️  Low confidence (< 0.6)")
    
    return results

async def run_stress_test():
    """Stres testi çalıştırır"""
    print("\\n🔥 AGENT STRESS TEST")
    print("=" * 50)
    
    agent = AdvancedToolCallingAgent()
    
    # 100 sıralı sorgu
    query = "ali@sirket.com hakkında bilgi ver"
    
    print(f"🧪 Running 100 sequential queries...")
    
    start_time = datetime.now()
    successful_queries = 0
    failed_queries = 0
    
    for i in range(100):
        try:
            response = await agent.process_request(query)
            if response.success:
                successful_queries += 1
            else:
                failed_queries += 1
        except Exception as e:
            failed_queries += 1
            print(f"❌ Query {i+1} failed: {e}")
    
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    
    print(f"\\n📊 STRESS TEST RESULTS")
    print("=" * 30)
    print(f"🕐 Total Time: {total_time:.3f}s")
    print(f"📈 Queries/Second: {100/total_time:.1f}")
    print(f"✅ Successful: {successful_queries}")
    print(f"❌ Failed: {failed_queries}")
    print(f"📊 Success Rate: {successful_queries/100:.1%}")
    
    return {
        "total_time": total_time,
        "queries_per_second": 100/total_time,
        "successful_queries": successful_queries,
        "failed_queries": failed_queries,
        "success_rate": successful_queries/100
    }

async def run_concurrent_test():
    """Eş zamanlı test çalıştırır"""
    print("\\n⚡ CONCURRENT TEST")
    print("=" * 50)
    
    agent = AdvancedToolCallingAgent()
    
    # 50 eş zamanlı sorgu
    queries = [
        "ali@sirket.com hakkında bilgi ver",
        "ayse@sirket.com son işlemlerini göster",
        "mehmet@sirket.com ödemi neden reddedildi?",
        "yardım"
    ]
    
    # Create 50 concurrent requests
    tasks = []
    for i in range(50):
        query = queries[i % len(queries)]
        tasks.append(agent.process_request(query))
    
    print(f"🧪 Running 50 concurrent queries...")
    
    start_time = datetime.now()
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = datetime.now()
    
    total_time = (end_time - start_time).total_seconds()
    
    # Analyze results
    successful = sum(1 for r in responses if not isinstance(r, Exception) and r.success)
    failed = len(responses) - successful
    
    print(f"\\n📊 CONCURRENT TEST RESULTS")
    print("=" * 30)
    print(f"🕐 Total Time: {total_time:.3f}s")
    print(f"📈 Queries/Second: {50/total_time:.1f}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {successful/50:.1%}")
    
    return {
        "total_time": total_time,
        "queries_per_second": 50/total_time,
        "successful_queries": successful,
        "failed_queries": failed,
        "success_rate": successful/50
    }

async def main():
    """Ana test fonksiyonu"""
    print("🧪 ADVANCED AGENT TEST SUITE")
    print("=" * 50)
    
    # Unit tests
    print("\\n🔬 RUNNING UNIT TESTS")
    print("=" * 30)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestAdvancedAgent))
    suite.addTest(unittest.makeSuite(TestToolManager))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Performance tests
    perf_results = await run_performance_test()
    
    # Stress test
    stress_results = await run_stress_test()
    
    # Concurrent test
    concurrent_results = await run_concurrent_test()
    
    # Test sonuçlarını kaydet
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_results = {
        "timestamp": timestamp,
        "unit_tests": {
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "success": result.wasSuccessful()
        },
        "performance": perf_results,
        "stress": stress_results,
        "concurrent": concurrent_results
    }
    
    with open(f"agent_test_results_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    print(f"\\n💾 Test results saved to: agent_test_results_{timestamp}.json")
    print("\\n🎉 ALL TESTS COMPLETED!")
    
    return test_results

if __name__ == "__main__":
    asyncio.run(main())
