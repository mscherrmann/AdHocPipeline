from adhocpipeline.crawler import Crawler
from utils.time import get_time_periods


def test_crawler(language="de",
                 start_date="01.03.2021",
                 end_date="01.04.2021"):

    time_periods = get_time_periods(start_date, end_date, 30)
    crawler = Crawler(language=language, is_test_mode=True)

    # Crawl
    for time_period in time_periods:
        crawler.crawl(time_period[0], time_period[1])


if __name__ == '__main__':
    test_crawler()
