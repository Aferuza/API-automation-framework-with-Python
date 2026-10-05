from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class GitHubRepositoryPage:
    """UI assertion surface for a public repository created by the API suite."""

    REPOSITORY_HEADING = (By.CSS_SELECTOR, "h1")

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url):
        self.driver.get(url)
        self.wait.until(EC.visibility_of_element_located(self.REPOSITORY_HEADING))
        return self

    @property
    def heading(self):
        return self.driver.find_element(*self.REPOSITORY_HEADING).text
