from selenium import webdriver
from selenium.webdriver.common.by import By
import os
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class GarticGuess:
    def __init__(self):
        self.lines = None
        self.load_lines()
        self.options = webdriver.ChromeOptions()
        self.options.page_load_strategy = 'none'
        self.options.add_argument("user-data-dir={}\driver_data".format(os.getcwd()))
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get("https://gartic.io/")
        self.is_game = False
        self.wait = WebDriverWait(self.driver, 10)

    def load_lines(self):
        self.lines = open("words.txt", "r", encoding="utf8").readlines()
        self.lines = [line.strip() for line in self.lines]
        self.lines.sort()
        
        with open("words.txt", "w", encoding="utf8") as f:
            for line in self.lines:
                f.write(line + "\n")

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
            try:
                self.driver.find_element(By.ID, 'possible_words')
            except NoSuchElementException:
                self.create_possible_words_div()

            try:
                answer_input = self.driver.find_element(By.XPATH, "//input[@name='answer']")
                if not self.is_game:
                    if answer_input:
                        print("Jogo encontrado, carregando componentes de palavras...")
                        self.is_game = True

                if self.is_game:
                    hint = self.driver.find_element(By.ID, 'hint')
                    if hint:
                        #print("Dica encontrada, extraindo palavras...")
                        words_divs = self.driver.find_elements(By.CLASS_NAME, 'word')
                        #print(f"{len(words_divs)} sílabas encontradas")
                        
                        separated_letters_without_hyphen = [span.text.lower() for word_div in words_divs for span in word_div.find_elements(By.TAG_NAME, 'span')]
                        complete_word = ''.join(separated_letters_without_hyphen).replace('-', '')

                        possible_words = self.extract_words(len(separated_letters_without_hyphen), complete_word)
                        #print(f"Palavras possíveis sem filtro ({len(possible_words)}): {possible_words}")

                        filtered_words = []
                        for word in possible_words:
                            matching_indices = [i for i, letter in enumerate(word) if letter == separated_letters_without_hyphen[i]]
                            if matching_indices == list(range(len(matching_indices))):
                                filtered_words.append(word)

                        #print(f"Palavras possíveis após filtragem ({len(filtered_words)}): {filtered_words}")

                        best_words = [word for word in possible_words if word not in filtered_words] if len(filtered_words) < len(possible_words) else filtered_words

                        self.update_possible_words_div(best_words)

            except (NoSuchElementException, ElementNotInteractableException):
                pass

    def create_possible_words_div(self):
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
        self.wait.until(EC.presence_of_element_located((By.ID, 'possible_words')))

    def update_possible_words_div(self, words):
        possible_words_list_html = "<ul>" + "".join(f"<li>{word}</li>" for word in words) + "</ul>"
        possible_words_div = self.driver.find_element(By.ID, 'possible_words')
        self.driver.execute_script("arguments[0].innerHTML = arguments[1];", possible_words_div, possible_words_list_html)

if __name__ == "__main__":
    solver = GarticGuess()
    solver.run()
