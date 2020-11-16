from typing import Dict, List
import random


class TextLoader:
    def __init__(self, character_set: List):
        self.character_set = character_set

    def load_data(self, dataset_name=None) -> Dict:
        """
        Returns a dictionary of dictionaries of all cleaned text data.
        :return: {
            "text_id": string
        }
        """
        # raise NotImplementedError()

    def generate_random_text(self, length=None) -> str:
        """
        Returns a string that contains all characters randomly. Used to create a warm-up
        dataset to train the model on rare characters.

        :param length: Length of string. If specified, pick characters randomly. If None,
        generate a string that contains all characters once.
        :return:
        """
        # str = ["a", "b", "c", "d", "e", "f"]
        string = ""

        max_word_length = 5  # if max sequence length without space
        for i in range(length):
            word_length = random.randint(1, max_word_length)
            for j in range(word_length):
                string += random.choice(self.character_set)
            string += " "
        return string.strip()

    def clean_string(self, original) -> str:
        """
        Removes all invalid characters from a string.

        Implementation notes: be wary of how to deal with spaces.

        :param original:
        :return:
        """
        string = ""
        for c in original:
            if c in self.character_set:
                string += c

        # Remove repetitive spaces
        new_string = ""
        for k in string.split():
            new_string += k + " "

        return new_string.strip()


if __name__ == "__main__":
    loader = TextLoader(["가", "나", "다", "라", "마"])
    text = loader.generate_random_text(length=10)
    print("Generated random text", text)

    clean_str = loader.clean_string("선(禪)의 시작은 부처님으로부터이다. 그런데 禪이란 쟈나의 음(音)을 그대로 <선나(禪那)>라고 쓰고 이를 한역하여 정려(瀞")
    print("clean text", clean_str)
