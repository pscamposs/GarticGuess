from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unicodedata


class GarticGuess:
    def __init__(self):
        print("Gartic.io Bot iniciando...")
        self.lines = None
        self.load_lines()
        self.options = webdriver.ChromeOptions()
        self.options.page_load_strategy = 'none'
        self.options.add_argument(
            "user-data-dir={}\driver_data".format(os.getcwd()))
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get("https://gartic.io/")
        self.is_game = False
        self.wait = WebDriverWait(self.driver, 10)
        print("Aguardando carregamento da página...")

    def load_lines(self):
        self.lines = open("words.txt", "r", encoding="utf8").readlines()
        self.lines = [self.normalize_string(line) for line in self.lines]
        self.lines.sort()

        with open("words.txt", "w", encoding="utf8") as f:
            for line in self.lines:
                f.write(line + "\n")

        print(f"{len(self.lines)} palavras carregadas com sucesso!")
        
    def normalize_string(self, text):
        utf_string = ''.join(
            (c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
        )
        return utf_string.strip()

    def create_possible_words_div(self):
        if self.driver.find_elements(By.ID, 'possible_words'):
            return
        possible_words_div = self.driver.execute_script(
            "var div = document.createElement('div');"
            "div.id = 'possible_words';"
            "div.style.position = 'fixed';"
            "div.style.width = '200px';"
            "div.style.top = '0';"
            "div.style.left = '0';"
            "div.style.backgroundColor = 'white';"
            "div.style.padding = '10px';"
            "div.style.zIndex = '9999';"
            "div.style.border = '1px solid black';"
            "div.style.borderRadius = '5px';"
            "div.style.color = 'black';"
            "div.overflow = 'auto';"
            "document.body.appendChild(div);"
            "return div;"
        )
        self.wait.until(EC.presence_of_element_located(
            (By.ID, 'possible_words')))

    def extract_words(self, length, letters):
        word_list = []
        for line in self.lines:
            if len(line) == length and all(letter in line for letter in letters) and len(letters) > 0 and line[0] == letters[0]:
                word_list.append(line)

        word_list = list(set(word_list))
        word_list.sort()

        return word_list

    def run(self):
        while True:
            self.create_possible_words_div()

            if not self.is_game:
                if self.driver.find_elements(
                        By.XPATH, "//input[@name='answer']"):
                    print("Jogo encontrado, carregando componentes de palavras...")
                    self.is_game = True

            if self.is_game:
                if self.driver.find_elements(By.ID, 'hint') and self.driver.find_elements(
                        By.CLASS_NAME, 'word'):
                    time.sleep(1)
                    separated_letters = [span.text.lower(
                    ) for word_div in self.driver.find_elements(
                        By.CLASS_NAME, 'word') for span in word_div.find_elements(By.TAG_NAME, 'span')]
                    complete_word = self.normalize_string(''.join(separated_letters))
    
            
                    possible_words = self.extract_words(
                        len(separated_letters), complete_word)

                    filtered_words = []

                    for word in possible_words:
                        lower_word = word.lower()
                        if all(lower_word[i] == separated_letters[i] or separated_letters[i] == '' for i in range(len(lower_word))):
                            filtered_words.append(word)
                    self.update_possible_words_div(filtered_words)

    def update_possible_words_div(self, words):
        possible_words_list_html = "<ul>" + \
            "".join(f"<li>{word}</li>" for word in words) + "</ul>"
        possible_words_div = self.driver.find_element(By.ID, 'possible_words')
        self.driver.execute_script(
            "arguments[0].innerHTML = arguments[1];", possible_words_div, possible_words_list_html)


if __name__ == "__main__":
    solver = GarticGuess()
    solver.run()
