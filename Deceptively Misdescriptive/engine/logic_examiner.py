from services.dictionary_client import DictionaryClient
from services.web_search_client import WebSearchClient
from services.nlp_client import NLPClient

class ExaminerLogicEngine:
    def __init__(self):
        self.dictionary = DictionaryClient()
        self.web_search = WebSearchClient()
        self.nlp = NLPClient()

    def examine(self, app):
        print(f"\n--- Examining Mark: '{app.mark_name}' ---")
        
        # Use NLP to break down the mark and the goods
        words_in_mark = self.nlp.split_mark_name(app.mark_name)
        core_goods = self.nlp.extract_core_goods(app.goods_services)
        
        highest_refusal = "Result: Approved. No descriptive/misdescriptive terms found."
        severity = 0 
        
        for word in words_in_mark:
            definition = self.dictionary.get_definition(word)
            if not definition:
                continue 

            metrics = self.web_search.check_industry_prevalence(word, core_goods)

            # Check against the raw text for accuracy
            in_goods = word.lower() in app.goods_services.lower()
            in_specimen = any(word.lower() in item.lower() for item in app.specimen_ingredients)
            is_misdescriptive = not (in_goods or in_specimen)
            
            if not is_misdescriptive:
                if severity < 1:
                    highest_refusal = f"Result: Merely Descriptive. '{word}' describes the goods."
                    severity = 1
                continue

            is_believable = metrics["common_in_industry"]
            if not is_believable:
                continue 

            is_material = metrics["drives_sales"]
            if is_material:
                if severity < 3:
                    highest_refusal = f"FATAL REFUSAL: Section 2(a) Deceptive. Consumers believe it contains '{word}', materially affecting sales."
                    severity = 3
            else:
                if severity < 2:
                    highest_refusal = f"REFUSAL: Section 2(e)(1) Deceptively Misdescriptive regarding '{word}'."
                    severity = 2
                
        return highest_refusal
# from services.dictionary_client import DictionaryClient
# from services.web_search_client import WebSearchClient
# from services.nlp_client import NLPClient

# class ExaminerLogicEngine:
#     def __init__(self):
#         self.dictionary = DictionaryClient()
#         self.web_search = WebSearchClient()
#         self.nlp = NLPClient()

#     def examine(self, app):
#         print(f"\n--- Examining Mark: '{app.mark_name}' ---")
        
#         # Use NLP to break down the mark and the goods
#         words_in_mark = self.nlp.split_mark_name(app.mark_name)
#         core_goods = self.nlp.extract_core_goods(app.goods_services)
        
#         highest_refusal = "Result: Approved. No descriptive/misdescriptive terms found."
#         severity = 0 
        
#         for word in words_in_mark:
#             definition = self.dictionary.get_definition(word)
#             if not definition:
#                 continue 

#             metrics = self.web_search.check_industry_prevalence(word, core_goods)

#             # Check against the raw text for accuracy
#             in_goods = word.lower() in app.goods_services.lower()
#             in_specimen = any(word.lower() in item.lower() for item in app.specimen_ingredients)
#             is_misdescriptive = not (in_goods or in_specimen)
            
#             if not is_misdescriptive:
#                 if severity < 1:
#                     highest_refusal = f"Result: Merely Descriptive. '{word}' describes the goods."
#                     severity = 1
#                 continue

#             is_believable = metrics["common_in_industry"]
#             if not is_believable:
#                 continue 

#             is_material = metrics["drives_sales"]
#             if is_material:
#                 if severity < 3:
#                     highest_refusal = f"FATAL REFUSAL: Section 2(a) Deceptive. Consumers believe it contains '{word}', materially affecting sales."
#                     severity = 3
#             else:
#                 if severity < 2:
#                     highest_refusal = f"REFUSAL: Section 2(e)(1) Deceptively Misdescriptive regarding '{word}'."
#                     severity = 2
                
#         return highest_refusal