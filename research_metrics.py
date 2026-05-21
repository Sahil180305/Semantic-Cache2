import httpx
import time
import statistics
import asyncio
import json
from typing import List, Dict

# Configuration
BASE_URL = "http://localhost:8001"
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzYWhpbCIsInRlbmFudF9pZCI6InJlc2VhcmNoX3RlbmFudCIsInJvbGUiOiJ1c2VyIiwic2NvcGVzIjpbImNhY2hlOnJlYWQiLCJjYWNoZTp3cml0ZSJdLCJleHAiOjE3Nzk0MTc5NzB9.UWxYv16M4yxmbEiUuzJtOBS6pRnNqIZ4TzA9Qpdetus" # Replace with actual token if auth is strict
HEADERS = {
    "Authorization": AUTH_TOKEN,
    "Content-Type": "application/json",
    "X-Tenant-ID": "research_tenant"
}



class SemanticCacheBenchmark:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = {
            "latencies_hit_l1_l2": [],
            "latencies_hit_l3": [],
            "latencies_miss": [],
            "hits_exact": 0,
            "hits_semantic": 0,
            "misses": 0,
            "normalization_hits": 0,
            "threshold_data": [],
            "domain_hits": {"tech": 0, "science": 0, "geo_history": 0, "lifestyle": 0, "control": 0},
            "total_queries": 0
        }

    async def setup_tenant(self):
        try:
            await self.client.post(f"{BASE_URL}/api/v1/tenant/create", headers=HEADERS, json={"tenant_id": "research_tenant"})
        except Exception:
            pass 

    async def store_seed_data(self):
        """Seed cache with 20 diverse Q&A pairs across 4 domains."""
        print("🌱 Storing 20 Seed Data Entries...")
        seed_data = [
            # Tech/AI
            {"query": "What is machine learning?", "response": "ML is a subset of AI...", "domain": "general"},
            {"query": "How do neural networks work?", "response": "Neural nets use layers of nodes...", "domain": "general"},
            {"query": "Explain quantum computing", "response": "Quantum computing uses qubits...", "domain": "general"},
            {"query": "What is blockchain technology?", "response": "A decentralized digital ledger system.", "domain": "general"},
            {"query": "How do solar panels generate electricity?", "response": "By converting sunlight using photovoltaic cells.", "domain": "general"},
            # Science
            {"query": "What is photosynthesis?", "response": "Process plants use to convert light to energy.", "domain": "general"},
            {"query": "Explain the theory of relativity", "response": "Einstein's theory linking space and time.", "domain": "general"},
            {"query": "What causes rain?", "response": "Condensation of water vapor in clouds.", "domain": "general"},
            {"query": "Explain DNA replication", "response": "Copying genetic material before cell division.", "domain": "general"},
            {"query": "What are black holes?", "response": "Regions where gravity prevents anything from escaping.", "domain": "general"},
            # Geo/History
            {"query": "What is the capital of France?", "response": "Paris is the capital.", "domain": "general"},
            {"query": "Who invented the telephone?", "response": "Alexander Graham Bell in 1876.", "domain": "general"},
            {"query": "What is the Great Wall of China?", "response": "Historic fortifications across northern China.", "domain": "general"},
            {"query": "What is the speed of light?", "response": "Approximately 299,792,458 m/s in vacuum.", "domain": "general"},
            {"query": "Explain the water cycle", "response": "Continuous movement of water on, above, and below Earth.", "domain": "general"},
            # Lifestyle/Other
            {"query": "How to make pasta carbonara?", "response": "Mix eggs, cheese, guanciale, and pasta.", "domain": "general"},
            {"query": "How does a refrigerator work?", "response": "Uses a refrigerant cycle to remove heat.", "domain": "general"},
            {"query": "How to bake a chocolate cake?", "response": "Mix flour, sugar, cocoa, eggs, bake at 350F.", "domain": "general"},
            {"query": "What is the function of the liver?", "response": "Detoxifies chemicals and metabolizes drugs.", "domain": "general"},
            {"query": "Explain inflation in economics", "response": "General increase in prices and fall in purchasing value.", "domain": "general"},
        ]
        
        success = 0
        for item in seed_data:
            try:
                await self.client.post(f"{BASE_URL}/api/v1/cache/semantic", headers=HEADERS, json=item)
                success += 1
            except Exception as e:
                print(f"⚠️ Warning: Could not store '{item['query'][:30]}...'")
        print(f"✅ {success}/{len(seed_data)} seed entries stored.")

    async def measure_latency_detailed(self, query: str, threshold: float = 0.75) -> Dict:
        start_time = time.perf_counter()
        payload = {"query": query, "threshold": threshold, "domain": "general"}
        
        try:
            response = await self.client.post(
                f"{BASE_URL}/api/v1/cache/semantic/search",
                headers=HEADERS,
                json=payload
            )
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            if response.status_code != 200:
                return {"latency_ms": latency_ms, "is_hit": False, "similarity": 0.0, "tier": "ERROR"}

            data = response.json()
            is_hit = data.get("hit", False)
            similarity = data.get("similarity", 0.0)
            
            tier = "MISS"
            if is_hit:
                if similarity >= 0.99 and latency_ms < 15:
                    tier = "L1/L2 (Exact)"
                else:
                    tier = "L3 (Semantic)"
            
            return {"latency_ms": latency_ms, "is_hit": is_hit, "similarity": similarity, "tier": tier}
        except Exception as e:
            return {"latency_ms": 0, "is_hit": False, "similarity": 0.0, "tier": "ERROR"}

    async def run_comprehensive_test(self):
        """Run 30 diverse test cases across multiple domains."""
        print("\n🧪 Running Comprehensive Hit Rate Test (30 Queries)...")
        test_cases = [
            # Tech/AI Variations
            ("Explain machine learning", "tech"),
            ("Tell me about ML", "tech"),
            ("How do neural nets function?", "tech"),
            ("Neural network mechanics", "tech"),
            ("Tell me about quantum computers", "tech"),
            ("What is quantum computation?", "tech"),
            ("Define blockchain", "tech"),
            # Science Variations
            ("How do plants make food?", "science"),
            ("Explain relativity theory", "science"),
            ("Why does it rain?", "science"),
            ("DNA copying process", "science"),
            ("Describe black holes", "science"),
            # Geo/History Variations
            ("Capital city of France", "geo_history"),
            ("Who created the telephone?", "geo_history"),
            ("Inventor of the phone", "geo_history"),
            ("Great Wall China history", "geo_history"),
            ("Speed of light value", "geo_history"),
            ("Explain hydrological cycle", "geo_history"),
            # Lifestyle Variations
            ("Recipe for carbonara", "lifestyle"),
            ("How do I prepare pasta carbonara?", "lifestyle"),
            ("How does a fridge cool things?", "lifestyle"),
            ("Chocolate cake baking instructions", "lifestyle"),
            ("Liver purpose in body", "lifestyle"),
            ("What does inflation mean in finance?", "lifestyle"),
            # Exact Matches (Should hit L1/L2)
            ("What is machine learning?", "tech"),
            ("What is photosynthesis?", "science"),
            ("How to make pasta carbonara?", "lifestyle"),
            # Control / Should Miss
            ("What is the weather today?", "control"),
            ("Who won the 2024 World Cup?", "control"),
            ("Translate hello to French", "control"),
        ]
        
        self.results["total_queries"] = len(test_cases)
        
        for i, (query, domain) in enumerate(test_cases):
            res = await self.measure_latency_detailed(query, threshold=0.75)
            self.results["domain_hits"][domain] += 1 if res["is_hit"] else 0
            
            status = "✅ HIT" if res["is_hit"] else "❌ MISS"
            print(f"  {status:4} | {domain:<10} | '{query}'")
            print(f"       -> Tier: {res['tier']} | Sim: {res['similarity']:.4f} | Lat: {res['latency_ms']:.2f}ms")
            
            if res["is_hit"]:
                if "L1/L2" in res["tier"]:
                    self.results["hits_exact"] += 1
                    self.results["latencies_hit_l1_l2"].append(res["latency_ms"])
                else:
                    self.results["hits_semantic"] += 1
                    self.results["latencies_hit_l3"].append(res["latency_ms"])
            else:
                self.results["misses"] += 1
                self.results["latencies_miss"].append(res["latency_ms"])

    async def run_normalization_test(self):
        """Test query normalization across 4 domains."""
        print("\n🧪 Running Normalization Impact Test...")
        variants = [
            "what is machine learning?", "What is ML", "Explain ML",
            "how does photosynthesis work", "Photosynthesis process?", "Explain plant food creation",
            "who invented the phone", "telephone creator", "Inventor of telephone",
            "how to make carbonara", "Carbonara recipe", "Pasta carbonara instructions"
        ]
        hits = 0
        for q in variants:
            res = await self.measure_latency_detailed(q, threshold=0.75)
            if res["is_hit"]:
                hits += 1
        self.results["normalization_hits"] = hits
        print(f"  📊 Normalization Success: {hits}/{len(variants)} variants captured")

    async def run_threshold_analysis(self):
        """Generate Threshold vs Hit Rate data."""
        print("\n📈 Generating Threshold Analysis Data...")
        thresholds = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
        # Use a representative subset to keep runtime low
        test_queries = [
            "Explain machine learning", "Tell me about ML", "Neural network mechanics",
            "How do plants make food?", "Why does it rain?", "DNA copying process",
            "Capital city of France", "Inventor of the phone", "Recipe for carbonara",
            "What is the weather today?", "Who won the 2024 World Cup?"
        ]
        
        print(f"{'Threshold':<10} | {'Hits':<6} | {'Total':<6} | {'Hit Rate %':<10}")
        print("-" * 45)
        
        for thresh in thresholds:
            hits = 0
            for query in test_queries:
                res = await self.measure_latency_detailed(query, threshold=thresh)
                if res["is_hit"]: hits += 1
            hit_rate = (hits / len(test_queries)) * 100
            self.results["threshold_data"].append({"threshold": thresh, "hit_rate": hit_rate})
            print(f"{thresh:<10.2f} | {hits:<6} | {len(test_queries):<6} | {hit_rate:<10.2f}%")

    async def run_concurrency_test(self, num_requests=50):
        """Test throughput with mixed queries (simulates real traffic)."""
        print(f"\n🧪 Running Concurrency Test ({num_requests} mixed requests)...")
        mixed_queries = [
            "Explain machine learning", "What is photosynthesis?", "Recipe for carbonara",
            "Who invented the telephone?", "What are black holes?", "What is the weather today?"
        ]
        tasks = [self.measure_latency_detailed(q, threshold=0.75) for q in mixed_queries * (num_requests // len(mixed_queries))]
        start = time.time()
        await asyncio.gather(*tasks)
        end = time.time()
        
        total_time = end - start
        throughput = num_requests / total_time
        print(f"  ⚡ Throughput: {throughput:.2f} req/sec")
        print(f"  ⏱️ Total Time: {total_time:.2f}s")

    def generate_report(self):
        """Final Paper-Ready Report."""
        print("\n" + "="*70)
        print("📊 FINAL RESEARCH PAPER METRICS (Expanded Dataset)")
        print("="*70)
        
        total_reqs = self.results["hits_exact"] + self.results["hits_semantic"] + self.results["misses"]
        total_hits = self.results["hits_exact"] + self.results["hits_semantic"]
        hit_rate = (total_hits / total_reqs * 100) if total_reqs > 0 else 0
        
        all_hit_lats = self.results["latencies_hit_l1_l2"] + self.results["latencies_hit_l3"]
        avg_hit_lat = statistics.mean(all_hit_lats) if all_hit_lats else 0
        avg_miss_lat = statistics.mean(self.results["latencies_miss"]) if self.results["latencies_miss"] else 0
        
        simulated_llm_lat = 2000.0 
        latency_reduction = ((simulated_llm_lat - avg_hit_lat) / simulated_llm_lat * 100) if avg_hit_lat > 0 else 0

        print(f"📦 Total Queries Tested:        {self.results['total_queries']}")
        print(f"🎯 Overall Cache Hit Rate:      {hit_rate:.2f}%")
        print(f"   - Exact Matches (L1/L2):     {self.results['hits_exact']}")
        print(f"   - Semantic Matches (L3):     {self.results['hits_semantic']}")
        print(f"   - Misses:                    {self.results['misses']}")
        print(f"📊 Domain Hit Distribution:")
        for domain, count in self.results["domain_hits"].items():
            print(f"   - {domain:<12}: {count} hits")
        print(f"⏱️ Average Cache Hit Latency:   {avg_hit_lat:.2f} ms")
        print(f"⏱️ Average Cache Miss Latency:  {avg_miss_lat:.2f} ms")
        print(f"📉 Est. Latency Reduction:      {latency_reduction:.2f}% (vs {simulated_llm_lat}ms LLM)")
        print(f"🔄 Query Normalization Success: {self.results['normalization_hits']}/12 variants")
        print(f"⚡ System Throughput:           See Concurrency Test above")
        print("="*70)
        print("\n💡 Paper Integration Tips:")
        print("1. Use 'Threshold Analysis' table for Figure 1: Hit Rate vs Similarity Threshold")
        print("2. Use Latency metrics for Figure 2: Bar Chart (L1/L2 vs L3 vs Miss vs Baseline LLM)")
        print("3. Cite 'Domain Hit Distribution' to prove cross-domain semantic robustness")
        print("4. Highlight 'Normalization Success' as a preprocessing optimization metric")

    async def run_all(self):
        await self.setup_tenant()
        await self.store_seed_data()
        await self.run_comprehensive_test()
        await self.run_normalization_test()
        await self.run_threshold_analysis()
        await self.run_concurrency_test()
        self.generate_report()
        await self.client.aclose()

if __name__ == "__main__":
    benchmark = SemanticCacheBenchmark()
    asyncio.run(benchmark.run_all())

# class SemanticCacheBenchmark:
#     def __init__(self):
#         self.client = httpx.AsyncClient(timeout=30.0)
#         self.results = {
#             "latencies_hit_l1_l2": [],
#             "latencies_hit_l3": [],
#             "latencies_miss": [],
#             "hits_exact": 0,
#             "hits_semantic": 0,
#             "misses": 0,
#             "normalization_hits": 0,
#             "threshold_data": []
#         }

#     async def setup_tenant(self):
#         """Ensure tenant exists."""
#         try:
#             await self.client.post(f"{BASE_URL}/api/v1/tenant/create", headers=HEADERS, json={"tenant_id": "research_tenant"})
#         except Exception:
#             pass 

#     async def store_seed_data(self):
#         """Seed the cache with known Q&A pairs."""
#         print("🌱 Storing Seed Data...")
#         seed_data = [
#             {"query": "What is machine learning?", "response": "ML is a subset of AI...", "domain": "general"},
#             {"query": "How do neural networks work?", "response": "Neural nets use layers of nodes...", "domain": "general"},
#             {"query": "What is the capital of France?", "response": "Paris is the capital.", "domain": "general"},
#             {"query": "Explain quantum computing", "response": "Quantum computing uses qubits...", "domain": "general"},
#             {"query": "How to make pasta carbonara?", "response": "Mix eggs, cheese, and guanciale...", "domain": "general"},
#             {"query": "What is AI?", "response": "Artificial Intelligence is...", "domain": "general"}
#         ]
#         for item in seed_data:
#             try:
#                 await self.client.post(f"{BASE_URL}/api/v1/cache/semantic", headers=HEADERS, json=item)
#             except Exception as e:
#                 print(f"⚠️ Warning: Could not store '{item['query']}': {e}")
#         print("✅ Seed data stored.")

#     async def measure_latency_detailed(self, query: str, threshold: float = 0.75) -> Dict:
#         """Measure latency and infer cache tier."""
#         start_time = time.perf_counter()
        
#         payload = {
#             "query": query, 
#             "threshold": threshold, 
#             "domain": "general" 
#         }
        
#         try:
#             response = await self.client.post(
#                 f"{BASE_URL}/api/v1/cache/semantic/search",
#                 headers=HEADERS,
#                 json=payload
#             )
#             end_time = time.perf_counter()
#             latency_ms = (end_time - start_time) * 1000
            
#             if response.status_code != 200:
#                 return {"latency_ms": latency_ms, "is_hit": False, "similarity": 0.0, "tier": "ERROR"}

#             data = response.json()
#             is_hit = data.get("hit", False)
#             similarity = data.get("similarity", 0.0)
            
#             tier = "MISS"
#             if is_hit:
#                 # Heuristic: Exact matches (L1/L2) are fast and have sim ~1.0
#                 # Semantic matches (L3) are slightly slower and have sim < 1.0
#                 if similarity >= 0.99 and latency_ms < 15:
#                     tier = "L1/L2 (Exact)"
#                 else:
#                     tier = "L3 (Semantic)"
            
#             return {
#                 "latency_ms": latency_ms,
#                 "is_hit": is_hit,
#                 "similarity": similarity,
#                 "tier": tier
#             }
#         except Exception as e:
#             return {"latency_ms": 0, "is_hit": False, "similarity": 0.0, "tier": "ERROR"}

#     async def run_semantic_hit_rate_test(self):
#         """Test semantic matching capabilities."""
#         print("\n🧪 Running Semantic Hit Rate Test...")
#         # Pairs: (Query, Expected Original Seed)
#         test_cases = [
#             ("Explain machine learning", "What is machine learning?"),
#             ("How do neural nets function?", "How do neural networks work?"),
#             ("Capital city of France", "What is the capital of France?"),
#             ("Tell me about quantum computers", "Explain quantum computing"),
#             ("Recipe for carbonara", "How to make pasta carbonara?"),
#             ("What is the weather today?", None) # Should Miss
#         ]
        
#         for query, _ in test_cases:
#             res = await self.measure_latency_detailed(query, threshold=0.75)
            
#             status = "✅ HIT" if res["is_hit"] else "❌ MISS"
#             print(f"  {status}: '{query}'")
#             print(f"       -> Tier: {res['tier']} | Sim: {res['similarity']:.4f} | Lat: {res['latency_ms']:.2f}ms")
            
#             if res["is_hit"]:
#                 if "L1/L2" in res["tier"]:
#                     self.results["hits_exact"] += 1
#                     self.results["latencies_hit_l1_l2"].append(res["latency_ms"])
#                 else:
#                     self.results["hits_semantic"] += 1
#                     self.results["latencies_hit_l3"].append(res["latency_ms"])
#             else:
#                 self.results["misses"] += 1
#                 self.results["latencies_miss"].append(res["latency_ms"])

#     async def run_normalization_test(self):
#         """Test query normalization."""
#         print("\n🧪 Running Normalization Impact Test...")
#         variants = ["what is ai?", "What is AI", "Explain AI"]
#         hits = 0
#         for q in variants:
#             res = await self.measure_latency_detailed(q, threshold=0.75)
#             if res["is_hit"]:
#                 hits += 1
#                 print(f"  ✅ Normalized Hit: '{q}'")
        
#         self.results["normalization_hits"] = hits
#         print(f"  📊 Normalization Success: {hits}/{len(variants)}")

#     async def run_threshold_analysis(self):
#         """Generate data for Threshold vs Hit Rate Graph."""
#         print("\n📈 Generating Threshold Analysis Data...")
#         thresholds = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
#         test_queries = [
#             "Explain machine learning", 
#             "How do neural nets function?", 
#             "Capital city of France", 
#             "Tell me about quantum computers", 
#             "Recipe for carbonara", 
#             "What is the weather today?" 
#         ]
        
#         print(f"{'Threshold':<10} | {'Hits':<6} | {'Total':<6} | {'Hit Rate %':<10}")
#         print("-" * 45)
        
#         for thresh in thresholds:
#             hits = 0
#             for query in test_queries:
#                 res = await self.measure_latency_detailed(query, threshold=thresh)
#                 if res["is_hit"]:
#                     hits += 1
            
#             hit_rate = (hits / len(test_queries)) * 100
#             self.results["threshold_data"].append({"threshold": thresh, "hit_rate": hit_rate})
#             print(f"{thresh:<10.2f} | {hits:<6} | {len(test_queries):<6} | {hit_rate:<10.2f}%")

#     async def run_concurrency_test(self, num_requests=50):
#         """Test throughput."""
#         print(f"\n🧪 Running Concurrency Test ({num_requests} requests)...")
#         tasks = [self.measure_latency_detailed("What is machine learning?", threshold=0.75) for _ in range(num_requests)]
#         start = time.time()
#         await asyncio.gather(*tasks)
#         end = time.time()
        
#         total_time = end - start
#         throughput = num_requests / total_time
#         print(f"  ⚡ Throughput: {throughput:.2f} req/sec")
#         print(f"  ⏱️ Total Time: {total_time:.2f}s")

#     def generate_report(self):
#         """Final Report for Paper."""
#         print("\n" + "="*60)
#         print("📊 FINAL RESEARCH PAPER METRICS")
#         print("="*60)
        
#         total_reqs = self.results["hits_exact"] + self.results["hits_semantic"] + self.results["misses"]
#         total_hits = self.results["hits_exact"] + self.results["hits_semantic"]
#         hit_rate = (total_hits / total_reqs * 100) if total_reqs > 0 else 0
        
#         # Latency Calcs
#         all_hit_lats = self.results["latencies_hit_l1_l2"] + self.results["latencies_hit_l3"]
#         avg_hit_lat = statistics.mean(all_hit_lats) if all_hit_lats else 0
#         avg_miss_lat = statistics.mean(self.results["latencies_miss"]) if self.results["latencies_miss"] else 0
        
#         simulated_llm_lat = 2000.0 
#         latency_reduction = ((simulated_llm_lat - avg_hit_lat) / simulated_llm_lat * 100) if avg_hit_lat > 0 else 0

#         print(f"1. Overall Cache Hit Rate:      {hit_rate:.2f}%")
#         print(f"   - Exact Matches (L1/L2):     {self.results['hits_exact']}")
#         print(f"   - Semantic Matches (L3):     {self.results['hits_semantic']}")
#         print(f"2. Average Cache Hit Latency:   {avg_hit_lat:.2f} ms")
#         print(f"3. Average Cache Miss Latency:  {avg_miss_lat:.2f} ms")
#         print(f"4. Est. Latency Reduction:      {latency_reduction:.2f}% (vs {simulated_llm_lat}ms LLM)")
#         print(f"5. Query Normalization Success: {self.results['normalization_hits']}/3 variants captured")
#         print(f"6. System Throughput:           See Concurrency Test above")
#         print("="*60)
        
#         print("\n💡 Tip for Paper:")
#         print("Use the 'Threshold Analysis' table above to plot Figure 1 (Hit Rate vs Threshold).")
#         print("Use the Latency metrics to plot Figure 2 (Latency Comparison Bar Chart).")

#     async def run_all(self):
#         await self.setup_tenant()
#         await self.store_seed_data()
#         await self.run_semantic_hit_rate_test()
#         await self.run_normalization_test()
#         await self.run_threshold_analysis()
#         await self.run_concurrency_test()
#         self.generate_report()
#         await self.client.aclose()

# if __name__ == "__main__":
#     benchmark = SemanticCacheBenchmark()
#     asyncio.run(benchmark.run_all())