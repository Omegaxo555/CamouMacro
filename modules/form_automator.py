import random
import logging
from typing import Optional, Dict, Any
from playwright.sync_api import Page, ElementHandle, Error as PlaywrightError

class FormAutomator:

    def __init__(self, page: Page):
        self.page = page

    def human_type(
        self,
        selector: str,
        text: str,
        clear_first: bool = True,
        min_delay: int = 50,
        max_delay: int = 120
    ) -> bool:
        try:
            logging.info(f"Typing into element with selector: {selector}")

            element = self.page.query_selector(selector, state="visible", timeout=5000)
            if not element:
                logging.error(f"Element with selector '{selector}' not found or not visible.")
                return False

            element.scroll_into_view_if_needed()
            element.click()

            if clear_first:
                self.page.keyboard.press("Control+A")
                self.page.keyboard.press("Backspace")

            for char in text:
                element.type(char, delay=random.randint(min_delay, max_delay))

            logging.info(f"Successfully typed into element with selector: {selector}")
            return True

        except PlaywrightError as e:
            logging.error(f"Playwright error while typing into element with selector '{selector}': {e}")
            return False

    def safe_click(self, selector: str, timeout: int = 5000) -> bool:
        try:
            logging.info(f"Attempting to click element with selector: {selector}")

            element = self.page.query_selector(selector, state="visible", timeout=timeout)
            if not element:
                logging.error(f"Element with selector '{selector}' not found or not visible.")
                return False

            element.scroll_into_view_if_needed()
            element.hover()

            self.page.wait_for_timeout(random.randint(100, 300))  # Random delay before clicking
            element.click()

            logging.info(f"Successfully clicked element with selector: {selector}")
            return True

        except PlaywrightError as e:
            logging.error(f"Playwright error while clicking element with selector '{selector}': {e}")
            return False

    
    def select_dropdown_option(self, selector: str, value_or_label: str) -> bool:
        try:
            
            logging.info(f"Selecting option '{value_or_label}' from dropdown with selector: {selector}")
            self.page.wait_for_selector(selector, state="visible", timeout=5000)
            self.page.select_option(selector, value=value_or_label)
            return True
        except PlaywrightError as e:
            logging.error(f"Playwright error while selecting option '{value_or_label}' from dropdown with selector '{selector}': {e}")
            return False

    def fill_form_dict(self, form_data: Dict[str, str]) -> bool:
        logging.info(f"Filling form with provided data... ({len(form_data)} campos)")

        for selector, value in form_data.items():
            success = self.human_type(selector,value)
            if not success:
                logging.error(f"Failed to fill form field with selector '{selector}' and value '{value}'")
                return False

            self.page.wait_for_timeout(random.randint(100, 300))  # Random delay between filling fields

        logging.info("Form filled successfully.")
        return True

    def submit_form(self, 
        submit_selector: str,
        expected_url_part: Optional[str] = None,
        success_selector: Optional[str] = None,
        timeout: int = 10000
    ) -> bool:
        if not self.safe_click(submit_selector):
            logging.error(f"Failed to click submit button with selector '{submit_selector}'")
            return False

        try:
            logging.info("Waiting for form submission to complete...")
            if success_selector:
                self.page.wait_for_selector(success_selector, state="visible", timeout=timeout)
                logging.info(f"Form submission successful. Found success element with selector '{success_selector}'")
                return True
            elif expected_url_part:
                self.page.wait_for_url(lambda url: expected_url_part in url, timeout=timeout)
                logging.info(f"Form submission successful. URL contains '{expected_url_part}'")
                return True
            
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
            return True
        
        except PlaywrightError as e:
            logging.error(f"Playwright error while waiting for form submission to complete: {e}")
            return False

        




