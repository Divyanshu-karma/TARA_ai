# from app.models.search_input import SearchInput
# from app.services.trademark_search_service import TrademarkSearchService

# def handle_search(keyword, intl_class, filing_status):
#     search_input = SearchInput(keyword, intl_class, filing_status)
#     service = TrademarkSearchService()
    # return service.search(search_input)
# app/controllers/search_controller.py
# app/controllers/search_controller.py
from app.services.trademark_search_service import TrademarkSearchService

def handle_search(keyword, intl_class=None, filing_status=None):
    svc = TrademarkSearchService()
    return svc.search(keyword, intl_class=intl_class, filing_status=filing_status)
