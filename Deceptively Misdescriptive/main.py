from models.application import TrademarkApplication
from engine.logic_examiner import ExaminerLogicEngine

def main():
    engine = ExaminerLogicEngine()

    real_app = TrademarkApplication(
        mark_name="Cold Drink", 
        goods_services="Retail store services featuring Air fresheners, baby food, biscuits, breakfast cereal, drinks, energy drinks, food, hand gel, hand sanitizer, handwash and creams, health care products, home care products, honey and spreads, hams, juices, ketchup, lentils and beans, malt, milk powder, non-achoholic beverages, oils and vinegars, peraonal care products, pulses, salad dressing, seafood, sparkling beverages, spices and salt, sunflower oil, table sauces, tinned and packaged foods, water; Wholesale store services featuring...", 
        specimen_ingredients=[], 
        design_elements="none"
    )

    print(engine.examine(real_app))

if __name__ == "__main__":
    main()