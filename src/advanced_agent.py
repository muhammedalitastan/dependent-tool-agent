#!/usr/bin/env python3
"""
Advanced Tool-Calling Agent - Enterprise Level
Gelişmiş birbirine bağımlı araç kullanımı ve akıllı asistan
"""

import os
import json
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import hashlib

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntentType(Enum):
    PAYMENT_FAILURE = "payment_failure"
    TRANSACTION_HISTORY = "transaction_history"
    USER_INFO = "user_info"
    ACTIVITY_ANALYSIS = "activity_analysis"
    FRAUD_ANALYSIS = "fraud_analysis"
    BALANCE_INQUIRY = "balance_inquiry"
    SUPPORT_REQUEST = "support_request"
    GENERAL_INQUIRY = "general_inquiry"
    HELP = "help"

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ToolResult:
    """Araç sonucu için veri sınıfı"""
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    tool_name: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ExecutionPlan:
    """İşlem planı için veri sınıfı"""
    id: str
    intent: IntentType
    entities: Dict[str, Any]
    tools: List[str]
    dependencies: Dict[str, List[str]] = None
    priority: Priority = Priority.MEDIUM
    estimated_time: float = 0.0
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.dependencies is None:
            self.dependencies = {}
        if self.id is None:
            self.id = hashlib.md5(f"{self.intent.value}{str(self.entities)}".encode()).hexdigest()[:12]

@dataclass
class AgentResponse:
    """Agent yanıtı için veri sınıfı"""
    success: bool
    message: str
    intent: IntentType
    entities: Dict[str, Any]
    execution_plan: ExecutionPlan
    results: List[ToolResult]
    processing_time: float
    confidence: float
    suggestions: List[str] = None
    related_actions: List[str] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
        if self.related_actions is None:
            self.related_actions = []

class AdvancedIntentAnalyzer:
    """Gelişmiş intent analizi sınıfı"""
    
    def __init__(self):
        self.intent_patterns = {
            IntentType.PAYMENT_FAILURE: [
                r"(?:ödeme|payment).*(?:neden|why|neden|red|reject|fail|başarısız)",
                r"(?:red|reject|fail|başarısız).*(?:ödeme|payment)",
                r"(?:iade|return).*(?:neden|why|neden|sorun|problem)",
                r"(?:sorun|problem).*(?:ödeme|payment|iade|return)"
            ],
            IntentType.TRANSACTION_HISTORY: [
                r"(?:işlem|transaction).*(?:geçmiş|history|son|recent|last)",
                r"(?:geçmiş|history|son|recent|last).*(?:işlem|transaction)",
                r"(?:hesabım|account).*(?:işlem|transaction)",
                r"(?:göster|show|listele|list).*(?:işlem|transaction)"
            ],
            IntentType.USER_INFO: [
                r"(?:kullanıcı|user).*(?:bilgi|info|detay|details)",
                r"(?:bilgi|info|detay|details).*(?:kullanıcı|user)",
                r"(?:hesap|account).*(?:bilgi|info|durum|status)",
                r"(?:kim|who).*(?:kullanıcı|user)"
            ],
            IntentType.ACTIVITY_ANALYSIS: [
                r"(?:aktivite|activity).*(?:analiz|analysis|durum|status)",
                r"(?:analiz|analysis).*(?:aktivite|activity)",
                r"(?:hesabım|account).*(?:durum|status|özet|summary)",
                r"(?:genel|general).*(():durum|status|bakış|overview)"
            ],
            IntentType.FRAUD_ANALYSIS: [
                r"(?:fraud|dolandırıcılık|şüpheli|suspicious).*(?:analiz|analysis|durum|status)",
                r"(?:güvenlik|security).*(?:analiz|analysis|kontrol|check)",
                r"(?:risk).*(?:değerlendirme|assessment|analiz|analysis)"
            ],
            IntentType.BALANCE_INQUIRY: [
                r"(?:bakiye|balance).*(?:nedir|what|kaç|how much)",
                r"(?:hesap|account).*(?:bakiye|balance)",
                r"(?:kalan|remaining).*(?:para|money|bakiye|balance)"
            ],
            IntentType.SUPPORT_REQUEST: [
                r"(?:yardım|help|destek|support).*(?:iste|request)",
                r"(?:sorun|problem).*(?:çözüm|solution)",
                r"(?:canlı|live).*(?:destek|support|yardım|help)"
            ],
            IntentType.HELP: [
                r"(?:yardım|help|nasıl|how)",
                r"(?:ne|what).*(?:yapabilirim|can i do)",
                r"(?:komut|command).*(?:listesi|list)"
            ]
        }
        
        self.entity_patterns = {
            "email": r"[\\w\\.-]+@[\\w\\.-]+\\.\\w+",
            "phone": r"(?:\\+90|0)?\\s*\\d{3}\\s*\\d{3}\\s*\\d{4}",
            "user_id": r"USR\\d{3}",
            "transaction_id": r"TRX\\d{3}",
            "date": r"\\d{4}-\\d{2}-\\d{2}|\\d{2}\\.\\d{2}\\.\\d{4}|\\d{2}/\\d{2}/\\d{4}",
            "amount": r"\\d+(?:\\.\\d+)?\\s*(?:TL|USD|EUR|\\$)",
            "time_period": r"(?:son|last|geçen|past)\\s+(\\d+)\\s+(?:gün|day|hafta|week|ay|month|yıl|year)",
            "limit": r"(?:limit|adet|count)\\s*[:\\s]*\\d+"
        }
    
    def analyze(self, user_input: str) -> Tuple[IntentType, Dict[str, Any], float]:
        """Kullanıcı girdisini analiz eder"""
        user_input_lower = user_input.lower()
        
        # Intent detection with confidence scoring
        intent_scores = {}
        
        for intent_type, patterns in self.intent_patterns.items():
            score = 0.0
            matched_patterns = []
            
            for pattern in patterns:
                matches = len(re.findall(pattern, user_input_lower))
                if matches > 0:
                    score += matches * 0.3
                    matched_patterns.append(pattern)
            
            # Keyword boosting
            intent_keywords = {
                IntentType.PAYMENT_FAILURE: ["ödeme", "payment", "red", "reject", "fail", "başarısız"],
                IntentType.TRANSACTION_HISTORY: ["işlem", "transaction", "geçmiş", "history", "son", "recent"],
                IntentType.USER_INFO: ["kullanıcı", "user", "bilgi", "info", "hesap", "account"],
                IntentType.ACTIVITY_ANALYSIS: ["aktivite", "activity", "analiz", "analysis", "durum", "status"],
                IntentType.FRAUD_ANALYSIS: ["fraud", "dolandırıcılık", "şüpheli", "suspicious", "güvenlik", "security"],
                IntentType.BALANCE_INQUIRY: ["bakiye", "balance", "para", "money"],
                IntentType.SUPPORT_REQUEST: ["yardım", "help", "destek", "support", "sorun", "problem"],
                IntentType.HELP: ["yardım", "help", "nasıl", "how", "ne", "what"]
            }
            
            if intent_type in intent_keywords:
                for keyword in intent_keywords[intent_type]:
                    if keyword in user_input_lower:
                        score += 0.2
            
            if score > 0:
                intent_scores[intent_type] = score
        
        # En yüksek skorlu intent'i seç
        if intent_scores:
            best_intent = max(intent_scores.keys(), key=lambda x: intent_scores[x])
            confidence = min(intent_scores[best_intent] / 2.0, 1.0)  # Normalize to 0-1
        else:
            best_intent = IntentType.GENERAL_INQUIRY
            confidence = 0.3
        
        # Entity extraction
        entities = {}
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, user_input_lower)
            if matches:
                entities[entity_type] = matches
        
        # Query complexity analysis
        word_count = len(user_input.split())
        complexity_score = min(word_count / 20.0, 1.0)
        
        # Add complexity to entities
        entities["complexity"] = {
            "word_count": word_count,
            "complexity_score": complexity_score,
            "has_negation": any(word in user_input_lower for word in ["değil", "yok", "not", "without", "hiç"]),
            "question_type": "wh_question" if any(word in user_input_lower for word in ["nedir", "neden", "nasıl", "ne", "kim", "kaç"]) else "yes_no"
        }
        
        return best_intent, entities, confidence

class AdvancedToolManager:
    """Gelişmiş araç yöneticisi"""
    
    def __init__(self):
        self.tools = {}
        self.tool_stats = {}
        self._register_tools()
    
    def _register_tools(self):
        """Araçları kaydeder"""
        self.tools = {
            "get_user_details": self._get_user_details,
            "get_recent_transactions": self._get_recent_transactions,
            "check_fraud_reason": self._check_fraud_reason,
            "get_failed_transactions": self._get_failed_transactions,
            "analyze_user_activity": self._analyze_user_activity,
            "get_account_balance": self._get_account_balance,
            "create_support_ticket": self._create_support_ticket,
            "search_transactions": self._search_transactions
        }
        
        # Initialize stats
        for tool_name in self.tools.keys():
            self.tool_stats[tool_name] = {
                "calls": 0,
                "success_rate": 0.0,
                "avg_execution_time": 0.0,
                "last_used": None
            }
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Araç çalıştırır"""
        if tool_name not in self.tools:
            return ToolResult(
                success=False,
                data=None,
                error=f"Tool not found: {tool_name}",
                tool_name=tool_name
            )
        
        start_time = datetime.now()
        
        try:
            # Mock database operations (gerçek implementasyonda burası API çağrıları olur)
            result = await self._execute_mock_tool(tool_name, **kwargs)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Update stats
            self._update_tool_stats(tool_name, True, execution_time)
            
            return ToolResult(
                success=True,
                data=result,
                execution_time=execution_time,
                tool_name=tool_name,
                metadata={"executed_at": datetime.now().isoformat()}
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Update stats
            self._update_tool_stats(tool_name, False, execution_time)
            
            return ToolResult(
                success=False,
                data=None,
                error=str(e),
                execution_time=execution_time,
                tool_name=tool_name
            )
    
    async def _execute_mock_tool(self, tool_name: str, **kwargs) -> Any:
        """Mock araç çalıştırma"""
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        if tool_name == "get_user_details":
            email = kwargs.get("email")
            if not email:
                raise ValueError("Email parameter required")
            
            # Mock user data
            users = {
                "ali@sirket.com": {
                    "user_id": "USR001",
                    "name": "Ali Yılmaz",
                    "email": "ali@sirket.com",
                    "status": "active",
                    "account_type": "Pro",
                    "created_date": "2023-01-15",
                    "last_login": "2024-03-01"
                },
                "ayse@sirket.com": {
                    "user_id": "USR002",
                    "name": "Ayşe Demir", 
                    "email": "ayse@sirket.com",
                    "status": "active",
                    "account_type": "Basic",
                    "created_date": "2023-02-20",
                    "last_login": "2024-02-28"
                }
            }
            
            if email not in users:
                raise ValueError(f"User not found: {email}")
            
            return users[email]
        
        elif tool_name == "get_recent_transactions":
            user_id = kwargs.get("user_id")
            limit = kwargs.get("limit", 5)
            
            if not user_id:
                raise ValueError("User ID parameter required")
            
            # Mock transaction data
            transactions = [
                {
                    "transaction_id": "TRX001",
                    "user_id": "USR001",
                    "amount": 1500.0,
                    "status": "failed",
                    "timestamp": "2024-03-01T14:30:00",
                    "description": "Pro paket ödemesi"
                },
                {
                    "transaction_id": "TRX002",
                    "user_id": "USR001", 
                    "amount": 1500.0,
                    "status": "success",
                    "timestamp": "2024-03-01T14:35:00",
                    "description": "Pro paket ödemesi"
                }
            ]
            
            user_transactions = [tx for tx in transactions if tx["user_id"] == user_id]
            return user_transactions[:limit]
        
        elif tool_name == "check_fraud_reason":
            transaction_id = kwargs.get("transaction_id")
            
            if not transaction_id:
                raise ValueError("Transaction ID parameter required")
            
            # Mock fraud data
            fraud_reasons = {
                "TRX001": {
                    "reason": "Yetersiz bakiye - Banka hesabında yeterli fon bulunamadı",
                    "detailed_code": "INSUFFICIENT_FUNDS",
                    "risk_score": 0.3
                },
                "TRX003": {
                    "reason": "Şüpheli aktivite - Hesap askıda olduğu için işlem reddedildi",
                    "detailed_code": "ACCOUNT_SUSPENDED", 
                    "risk_score": 0.8
                }
            }
            
            if transaction_id not in fraud_reasons:
                raise ValueError(f"Fraud record not found: {transaction_id}")
            
            return fraud_reasons[transaction_id]
        
        elif tool_name == "analyze_user_activity":
            user_id = kwargs.get("user_id")
            
            if not user_id:
                raise ValueError("User ID parameter required")
            
            # Mock activity analysis
            return {
                "user_id": user_id,
                "total_transactions": 25,
                "successful_transactions": 22,
                "failed_transactions": 3,
                "success_rate": 0.88,
                "total_amount": 15000.0,
                "avg_transaction_amount": 600.0,
                "risk_score": 0.2,
                "last_activity": "2024-03-01T14:35:00",
                "account_health": "Good"
            }
        
        elif tool_name == "get_account_balance":
            user_id = kwargs.get("user_id")
            
            if not user_id:
                raise ValueError("User ID parameter required")
            
            # Mock balance data
            balances = {
                "USR001": {"balance": 2500.0, "currency": "TL", "available": 2300.0},
                "USR002": {"balance": 750.0, "currency": "TL", "available": 750.0}
            }
            
            return balances.get(user_id, {"balance": 0.0, "currency": "TL", "available": 0.0})
        
        else:
            # Default mock response
            return {"status": "mock_response", "tool": tool_name, "params": kwargs}
    
    def _update_tool_stats(self, tool_name: str, success: bool, execution_time: float):
        """Araç istatistiklerini günceller"""
        stats = self.tool_stats[tool_name]
        stats["calls"] += 1
        stats["last_used"] = datetime.now().isoformat()
        
        # Update success rate
        current_success_rate = stats["success_rate"]
        total_calls = stats["calls"]
        if success:
            stats["success_rate"] = ((current_success_rate * (total_calls - 1)) + 1.0) / total_calls
        else:
            stats["success_rate"] = (current_success_rate * (total_calls - 1)) / total_calls
        
        # Update average execution time
        current_avg_time = stats["avg_execution_time"]
        stats["avg_execution_time"] = ((current_avg_time * (total_calls - 1)) + execution_time) / total_calls
    
    def get_tool_stats(self) -> Dict[str, Any]:
        """Tüm araç istatistiklerini döndürür"""
        return self.tool_stats.copy()

class AdvancedExecutionPlanner:
    """Gelişmiş işlem planlayıcısı"""
    
    def __init__(self, tool_manager: AdvancedToolManager):
        self.tool_manager = tool_manager
        self.intent_tool_mapping = {
            IntentType.PAYMENT_FAILURE: ["get_user_details", "get_failed_transactions", "check_fraud_reason"],
            IntentType.TRANSACTION_HISTORY: ["get_user_details", "get_recent_transactions"],
            IntentType.USER_INFO: ["get_user_details"],
            IntentType.ACTIVITY_ANALYSIS: ["get_user_details", "analyze_user_activity"],
            IntentType.FRAUD_ANALYSIS: ["get_user_details", "get_failed_transactions", "check_fraud_reason"],
            IntentType.BALANCE_INQUIRY: ["get_user_details", "get_account_balance"],
            IntentType.SUPPORT_REQUEST: ["get_user_details", "create_support_ticket"],
            IntentType.HELP: []
        }
    
    def create_execution_plan(self, intent: IntentType, entities: Dict[str, Any]) -> ExecutionPlan:
        """İşlem planı oluşturur"""
        tools = self.intent_tool_mapping.get(intent, [])
        
        # Dependencies based on entities
        dependencies = {}
        
        if "get_user_details" in tools:
            # User details is usually needed first
            dependencies["get_recent_transactions"] = ["get_user_details"]
            dependencies["analyze_user_activity"] = ["get_user_details"]
            dependencies["get_failed_transactions"] = ["get_user_details"]
            dependencies["check_fraud_reason"] = ["get_failed_transactions"]
            dependencies["get_account_balance"] = ["get_user_details"]
        
        # Priority based on intent
        priority_map = {
            IntentType.FRAUD_ANALYSIS: Priority.URGENT,
            IntentType.PAYMENT_FAILURE: Priority.HIGH,
            IntentType.SUPPORT_REQUEST: Priority.HIGH,
            IntentType.BALANCE_INQUIRY: Priority.MEDIUM,
            IntentType.TRANSACTION_HISTORY: Priority.MEDIUM,
            IntentType.USER_INFO: Priority.MEDIUM,
            IntentType.ACTIVITY_ANALYSIS: Priority.MEDIUM,
            IntentType.HELP: Priority.LOW
        }
        
        priority = priority_map.get(intent, Priority.MEDIUM)
        
        # Estimate execution time
        estimated_time = len(tools) * 0.15  # 150ms per tool average
        
        return ExecutionPlan(
            intent=intent,
            entities=entities,
            tools=tools,
            dependencies=dependencies,
            priority=priority,
            estimated_time=estimated_time
        )
    
    async def execute_plan(self, plan: ExecutionPlan) -> List[ToolResult]:
        """İşlem planını çalıştırır"""
        results = []
        executed_tools = {}
        
        # Execute tools in dependency order
        for tool_name in plan.tools:
            # Check dependencies
            if tool_name in plan.dependencies:
                deps = plan.dependencies[tool_name]
                for dep in deps:
                    if dep not in executed_tools or not executed_tools[dep].success:
                        # Skip tool if dependency failed
                        results.append(ToolResult(
                            success=False,
                            data=None,
                            error=f"Dependency {dep} failed or not executed",
                            tool_name=tool_name
                        ))
                        continue
            
            # Prepare tool parameters
            tool_params = self._prepare_tool_params(tool_name, plan.entities, executed_tools)
            
            # Execute tool
            result = await self.tool_manager.execute_tool(tool_name, **tool_params)
            results.append(result)
            executed_tools[tool_name] = result
        
        return results
    
    def _prepare_tool_params(self, tool_name: str, entities: Dict[str, Any], executed_tools: Dict[str, ToolResult]) -> Dict[str, Any]:
        """Araç parametrelerini hazırlar"""
        params = {}
        
        if tool_name == "get_user_details":
            if "email" in entities:
                params["email"] = entities["email"][0]
        
        elif tool_name == "get_recent_transactions":
            # Get user_id from previous tool result
            if "get_user_details" in executed_tools and executed_tools["get_user_details"].success:
                user_data = executed_tools["get_user_details"].data
                params["user_id"] = user_data["user_id"]
            
            # Set limit from entities
            if "limit" in entities:
                limit_match = re.search(r"\\d+", entities["limit"][0])
                if limit_match:
                    params["limit"] = int(limit_match.group())
            else:
                params["limit"] = 5
        
        elif tool_name == "check_fraud_reason":
            # Get transaction_id from failed transactions
            if "get_failed_transactions" in executed_tools and executed_tools["get_failed_transactions"].success:
                failed_txs = executed_tools["get_failed_transactions"].data
                if failed_txs:
                    params["transaction_id"] = failed_txs[0]["transaction_id"]
            elif "transaction_id" in entities:
                params["transaction_id"] = entities["transaction_id"][0]
        
        elif tool_name in ["analyze_user_activity", "get_account_balance", "get_failed_transactions"]:
            # Get user_id from user details
            if "get_user_details" in executed_tools and executed_tools["get_user_details"].success:
                user_data = executed_tools["get_user_details"].data
                params["user_id"] = user_data["user_id"]
        
        return params

class AdvancedToolCallingAgent:
    """Gelişmiş Tool-Calling Agent ana sınıfı"""
    
    def __init__(self):
        self.intent_analyzer = AdvancedIntentAnalyzer()
        self.tool_manager = AdvancedToolManager()
        self.execution_planner = AdvancedExecutionPlanner(self.tool_manager)
        self.session_history = []
        self.agent_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "avg_processing_time": 0.0,
            "intent_distribution": {},
            "session_start": datetime.now().isoformat()
        }
    
    async def process_request(self, user_input: str) -> AgentResponse:
        """Kullanıcı talebini işler"""
        start_time = datetime.now()
        
        try:
            # Analyze user input
            intent, entities, confidence = self.intent_analyzer.analyze(user_input)
            
            # Create execution plan
            plan = self.execution_planner.create_execution_plan(intent, entities)
            
            # Execute plan
            results = await self.execution_planner.execute_plan(plan)
            
            # Generate response
            response = self._generate_response(user_input, intent, entities, plan, results)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update stats
            self._update_agent_stats(intent, processing_time, len(results) > 0 and all(r.success for r in results))
            
            # Add to session history
            self.session_history.append({
                "user_input": user_input,
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Update response with timing
            response.processing_time = processing_time
            
            return response
            
        except Exception as e:
            logger.error(f"Request processing failed: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AgentResponse(
                success=False,
                message=f"İsteğiniz işlenirken bir hata oluştu: {str(e)}",
                intent=IntentType.GENERAL_INQUIRY,
                entities={},
                execution_plan=ExecutionPlan(
                    id="error",
                    intent=IntentType.GENERAL_INQUIRY,
                    entities={}
                ),
                results=[],
                processing_time=processing_time,
                confidence=0.0
            )
    
    def _generate_response(self, user_input: str, intent: IntentType, entities: Dict[str, Any], 
                          plan: ExecutionPlan, results: List[ToolResult]) -> AgentResponse:
        """Agent yanıtı üretir"""
        
        # Check if any tool failed
        failed_tools = [r for r in results if not r.success]
        if failed_tools:
            return AgentResponse(
                success=False,
                message=f"Bazı işlemler başarısız oldu: {', '.join([f.error for f in failed_tools])}",
                intent=intent,
                entities=entities,
                execution_plan=plan,
                results=results,
                processing_time=0.0,
                confidence=0.3
            )
        
        # Generate intent-specific response
        if intent == IntentType.PAYMENT_FAILURE:
            message, suggestions, related_actions = self._handle_payment_failure_response(results)
        elif intent == IntentType.TRANSACTION_HISTORY:
            message, suggestions, related_actions = self._handle_transaction_history_response(results)
        elif intent == IntentType.USER_INFO:
            message, suggestions, related_actions = self._handle_user_info_response(results)
        elif intent == IntentType.ACTIVITY_ANALYSIS:
            message, suggestions, related_actions = self._handle_activity_analysis_response(results)
        elif intent == IntentType.BALANCE_INQUIRY:
            message, suggestions, related_actions = self._handle_balance_inquiry_response(results)
        elif intent == IntentType.HELP:
            message, suggestions, related_actions = self._handle_help_response()
        else:
            message, suggestions, related_actions = self._handle_general_response(results)
        
        return AgentResponse(
            success=True,
            message=message,
            intent=intent,
            entities=entities,
            execution_plan=plan,
            results=results,
            processing_time=0.0,
            confidence=0.8,
            suggestions=suggestions,
            related_actions=related_actions
        )
    
    def _handle_payment_failure_response(self, results: List[ToolResult]) -> Tuple[str, List[str], List[str]]:
        """Ödeme başarısızlık yanıtı"""
        user_data = None
        fraud_data = None
        
        for result in results:
            if result.tool_name == "get_user_details" and result.success:
                user_data = result.data
            elif result.tool_name == "check_fraud_reason" and result.success:
                fraud_data = result.data
        
        if user_data and fraud_data:
            message = f"🔍 **Ödeme Analizi Sonuçları**\\n\\n"
            message += f"👤 **Kullanıcı:** {user_data['name']} ({user_data['email']})\\n"
            message += f"📊 **Hesap Durumu:** {user_data['status'].title()}\\n\\n"
            message += f"❌ **Red Sebebi:** {fraud_data['reason']}\\n"
            message += f"🔧 **Kod:** {fraud_data['detailed_code']}\\n"
            if 'risk_score' in fraud_data:
                message += f"⚠️ **Risk Skoru:** {fraud_data['risk_score']}/1.0"
            
            suggestions = [
                "Hesap bakiyenizi kontrol edin",
                "Banka kartı bilgilerinizi güncelleyin",
                "Farklı bir ödeme yöntemi deneyin"
            ]
            
            related_actions = [
                "Hesap detaylarını göster",
                "Son işlemleri listele",
                "Destek talebi oluştur"
            ]
        else:
            message = "Ödeme analizi için yeterli bilgi bulunamadı."
            suggestions = ["E-posta adresinizi belirtin"]
            related_actions = []
        
        return message, suggestions, related_actions
    
    def _handle_transaction_history_response(self, results: List[ToolResult]) -> Tuple[str, List[str], List[str]]:
        """İşlem geçmişi yanıtı"""
        user_data = None
        transactions = None
        
        for result in results:
            if result.tool_name == "get_user_details" and result.success:
                user_data = result.data
            elif result.tool_name == "get_recent_transactions" and result.success:
                transactions = result.data
        
        if user_data and transactions:
            message = f"📋 **İşlem Geçmişi**\\n\\n"
            message += f"👤 **Kullanıcı:** {user_data['name']}\\n"
            message += f"📊 **Toplam İşlem:** {len(transactions)}\\n\\n"
            
            for i, tx in enumerate(transactions[:5], 1):
                status_emoji = "✅" if tx['status'] == 'success' else "❌"
                message += f"{i}. {status_emoji} **{tx['transaction_id']}** - {tx['amount']} TL - {tx['status'].title()}\\n"
                message += f"   📅 {tx['timestamp']} - {tx['description']}\\n"
            
            suggestions = [
                "Daha fazla işlem göster",
                "Başarısız işlemleri filtrele",
                "İşlem detaylarını indir"
            ]
            
            related_actions = [
                "Hesap aktivitesini analiz et",
                "Bakiye sorgula",
                "Başarısız işlemleri incele"
            ]
        else:
            message = "İşlem geçmişi bulunamadı."
            suggestions = ["E-posta adresinizi belirtin"]
            related_actions = []
        
        return message, suggestions, related_actions
    
    def _handle_user_info_response(self, results: List[ToolResult]) -> Tuple[str, List[str], List[str]]:
        """Kullanıcı bilgisi yanıtı"""
        user_data = None
        
        for result in results:
            if result.tool_name == "get_user_details" and result.success:
                user_data = result.data
                break
        
        if user_data:
            message = f"👤 **Kullanıcı Bilgileri**\\n\\n"
            message += f"🆔 **Kullanıcı ID:** {user_data['user_id']}\\n"
            message += f"👨‍💼 **Ad Soyad:** {user_data['name']}\\n"
            message += f"📧 **E-posta:** {user_data['email']}\\n"
            message += f"📊 **Durum:** {user_data['status'].title()}\\n"
            message += f"💎 **Hesap Tipi:** {user_data.get('account_type', 'N/A')}\\n"
            message += f"📅 **Kayıt Tarihi:** {user_data['created_date']}\\n"
            message += f"🕐 **Son Giriş:** {user_data['last_login']}"
            
            suggestions = [
                "Hesap aktivitesini göster",
                "İşlem geçmişini listele",
                "Bakiye bilgisini al"
            ]
            
            related_actions = [
                "Son işlemleri göster",
                "Hesap özetini al",
                "Destek talebi oluştur"
            ]
        else:
            message = "Kullanıcı bilgileri bulunamadı."
            suggestions = ["Geçerli bir e-posta adresi belirtin"]
            related_actions = []
        
        return message, suggestions, related_actions
    
    def _handle_activity_analysis_response(self, results: List[ToolResult]) -> Tuple[str, List[str], List[str]]:
        """Aktivite analizi yanıtı"""
        user_data = None
        activity_data = None
        
        for result in results:
            if result.tool_name == "get_user_details" and result.success:
                user_data = result.data
            elif result.tool_name == "analyze_user_activity" and result.success:
                activity_data = result.data
        
        if user_data and activity_data:
            message = f"📊 **Hesap Aktivite Analizi**\\n\\n"
            message += f"👤 **Kullanıcı:** {user_data['name']}\\n\\n"
            message += f"📈 **İşlem İstatistikleri:**\\n"
            message += f"• Toplam İşlem: {activity_data['total_transactions']}\\n"
            message += f"• Başarılı: {activity_data['successful_transactions']} ({activity_data['success_rate']:.1%})\\n"
            message += f"• Başarısız: {activity_data['failed_transactions']}\\n\\n"
            message += f"💰 **Finansal Bilgiler:**\\n"
            message += f"• Toplam Hacim: {activity_data['total_amount']:.2f} TL\\n"
            message += f"• Ortalama İşlem: {activity_data['avg_transaction_amount']:.2f} TL\\n\\n"
            message += f"🔒 **Güvenlik:**\\n"
            message += f"• Risk Skoru: {activity_data['risk_score']}/1.0\\n"
            message += f"• Hesap Sağlığı: {activity_data['account_health']}"
            
            suggestions = [
                "Risk faktörlerini detaylandır",
                "Başarısız işlemleri incele",
                "İşlem grafiği oluştur"
            ]
            
            related_actions = [
                "Son işlemleri göster",
                "Fraud analizi yap",
                "Bakiye sorgula"
            ]
        else:
            message = "Aktivite analizi için yeterli bilgi bulunamadı."
            suggestions = ["E-posta adresinizi belirtin"]
            related_actions = []
        
        return message, suggestions, related_actions
    
    def _handle_balance_inquiry_response(self, results: List[ToolResult]) -> Tuple[str, List[str], List[str]]:
        """Bakiye sorgulama yanıtı"""
        user_data = None
        balance_data = None
        
        for result in results:
            if result.tool_name == "get_user_details" and result.success:
                user_data = result.data
            elif result.tool_name == "get_account_balance" and result.success:
                balance_data = result.data
        
        if user_data and balance_data:
            message = f"💰 **Hesap Bakiyesi**\\n\\n"
            message += f"👤 **Kullanıcı:** {user_data['name']}\\n"
            message += f"💳 **Bakiye:** {balance_data['balance']:.2f} {balance_data['currency']}\\n"
            message += f"✅ **Kullanılabilir:** {balance_data['available']:.2f} {balance_data['currency']}\\n"
            
            if balance_data['balance'] != balance_data['available']:
                blocked_amount = balance_data['balance'] - balance_data['available']
                message += f"🔒 **Bloke:** {blocked_amount:.2f} {balance_data['currency']}"
            
            suggestions = [
                "İşlem geçmişini göster",
                "Para yatır",
                "Para çek"
            ]
            
            related_actions = [
                "Son işlemleri listele",
                "Hesap hareketlerini detaylandır",
                "Para transferi yap"
            ]
        else:
            message = "Bakiye bilgisi bulunamadı."
            suggestions = ["E-posta adresinizi belirtin"]
            related_actions = []
        
        return message, suggestions, related_actions
    
    def _handle_help_response(self) -> Tuple[str, List[str], List[str]]:
        """Yardım yanıtı"""
        message = """
🆘 **YARDIM MENÜSÜ**

📋 **Kullanılabilir Komutlar:**

💳 **Ödeme İşlemleri:**
• "ali@sirket.com ödemi neden reddedildi?"
• "Vadeli işlemleri göster"

📊 **Hesap Bilgileri:**
• "ayse@sirket.com hakkında bilgi ver"
• "Hesap aktivitesini analiz et"

💰 **Finansal İşlemler:**
• "Bakiyemi öğrenmek istiyorum"
• "Son işlemlerimi göster"

🔍 **Diğer İşlemler:**
• "Fraud analizi yap"
• "Destek talebi oluştur"

💡 **İpuçları:**
• E-posta adresini belirtmek daha iyi sonuçlar verir
• Spesifik sorular sorun
• İşlem ID'si varsa belirtin
        """
        
        suggestions = [
            "Ödeme sorununu sorgula",
            "Hesap bilgilerini al",
            "İşlem geçmişini göster"
        ]
        
        related_actions = [
            "Ödeme analizi yap",
            "Hesap özeti al",
            "Aktivite analizi"
        ]
        
        return message, suggestions, related_actions
    
    def _handle_general_response(self, results: List[ToolResult]) -> Tuple[str, List[str], List[str]]:
        """Genel yanıt"""
        message = "Sorunuzu anlayamadım. 'yardım' yazarak kullanılabilir komutları görebilirsiniz."
        suggestions = [
            "Yardım menüsünü göster",
            "Ödeme sorununu sorgula",
            "Hesap bilgilerini al"
        ]
        related_actions = []
        
        return message, suggestions, related_actions
    
    def _update_agent_stats(self, intent: IntentType, processing_time: float, success: bool):
        """Agent istatistiklerini günceller"""
        self.agent_stats["total_requests"] += 1
        
        if success:
            self.agent_stats["successful_requests"] += 1
        
        # Update average processing time
        current_avg = self.agent_stats["avg_processing_time"]
        total_requests = self.agent_stats["total_requests"]
        self.agent_stats["avg_processing_time"] = ((current_avg * (total_requests - 1)) + processing_time) / total_requests
        
        # Update intent distribution
        intent_name = intent.value
        if intent_name not in self.agent_stats["intent_distribution"]:
            self.agent_stats["intent_distribution"][intent_name] = 0
        self.agent_stats["intent_distribution"][intent_name] += 1
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Agent istatistiklerini döndürür"""
        return {
            **self.agent_stats,
            "success_rate": self.agent_stats["successful_requests"] / max(self.agent_stats["total_requests"], 1),
            "session_history_count": len(self.session_history),
            "tool_stats": self.tool_manager.get_tool_stats()
        }
    
    def get_session_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Oturum geçmişini döndürür"""
        return self.session_history[-limit:]

if __name__ == "__main__":
    # Test
    async def test_agent():
        agent = AdvancedToolCallingAgent()
        
        test_queries = [
            "ali@sirket.com ödemi neden reddedildi?",
            "ayse@sirket.com hakkında bilgi ver",
            "hesap aktivitesini analiz et",
            "yardım"
        ]
        
        for query in test_queries:
            print(f"\\n🤖 Sorgu: {query}")
            response = await agent.process_request(query)
            print(f"💬 Yanıt: {response.message[:200]}...")
            print(f"✅ Başarılı: {response.success}")
            print(f"🎯 Intent: {response.intent.value}")
            print(f"⏱️ Süre: {response.processing_time:.3f}s")
            print("-" * 50)
    
    # Run test
    import asyncio
    asyncio.run(test_agent())
