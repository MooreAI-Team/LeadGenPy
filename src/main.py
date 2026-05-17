from WebScrapper.scrapper import Scrappers
from Configs.selenium_config import driver
from Configs import config


def main():
    scrapper = Scrappers()

    while True:
        print("\n[MENU]\n  1 - Single business category extract\n  2 - MooreAI mode\n  0 - Exit\n")
        try:
            mode = int(input())
        except ValueError:
            print("[LOG] Invalid option")
            continue

        try:
            if mode == 0:
                print("[LOG] Terminated")
                driver.quit()
                break
            elif mode == 1:
                business_category = input("Enter the Business Category: ")
                location = input("Enter the Location: ")
                scrapper.scrape(business_category, location)
            elif mode == 2:
                location = input("Enter the Location: ")
                print(f"[LOG] MooreAI mode -- {len(config.all_business_categories)} categories\n")
                for business_category in config.all_business_categories:
                    scrapper.scrape(business_category, location)
                print("[LOG] MooreAI mode complete")
            else:
                print("[LOG] Invalid option")
        except Exception as error:
            print(error)


if __name__ == "__main__":
    main()
