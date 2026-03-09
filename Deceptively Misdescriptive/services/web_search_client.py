from ddgs import DDGS

class WebSearchClient:
    def check_industry_prevalence(self, term, core_goods_list):
        # Create a shorter, effective query: "Topple" AND ("air fresheners" OR "baby food")
        goods_query = " OR ".join([f'"{g}"' for g in core_goods_list])
        query = f'"{term}" ({goods_query})'
        
        try:
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=5)
            
            if not results:
                return {"common_in_industry": False, "drives_sales": False}

            relevant_hits = sum(1 for res in results if term.lower() in res.get('body', '').lower())
            
            return {
                "common_in_industry": relevant_hits >= 1, 
                "drives_sales": relevant_hits >= 3
            }
        except Exception as e:
            return {"common_in_industry": False, "drives_sales": False}

# from ddgs import DDGS  # Changed import

# class WebSearchClient:
#     def check_industry_prevalence(self, term, goods_services):
#         query = f'"{term}" AND "{goods_services}"'
#         try:
#             with DDGS() as ddgs:
#                 results = list(ddgs.text(query, max_results=5))
                
#             is_common = len(results) >= 3
#             drives_sales = len(results) == 5 
#             return {"common_in_industry": is_common, "drives_sales": drives_sales}
#         except Exception:
#             return {"common_in_industry": False, "drives_sales": False}
# from duckduckgo_search import DDGS

# class WebSearchClient:
#     def check_industry_prevalence(self, term, goods_services):
#         """
#         Simulates LexisNexis/Google search.
#         Checks if the term and the goods frequently appear together online,
#         indicating consumers EXPECT this feature (Believability/Materiality).
#         """
#         query = f'"{term}" AND "{goods_services}"'
#         try:
#             with DDGS() as ddgs:
#                 results = list(ddgs.text(query, max_results=5))
                
#             # If we find multiple search results talking about this term 
#             # in relation to these goods, it's common in the industry.
#             is_common = len(results) >= 3
            
#             # Simplified materiality check: If it's highly searched, it drives sales.
#             drives_sales = len(results) == 5 
            
#             return {"common_in_industry": is_common, "drives_sales": drives_sales}
#         except Exception:
#             return {"common_in_industry": False, "drives_sales": False}