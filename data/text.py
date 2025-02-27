from typing import Dict, List
import random
import tqdm
import os


class TextLoader:
    def __init__(self, character_list: List):
        self.character_list = character_list
        self.character_set = set(character_list)

    def load_data(self, dataset_name=None, verbose=False) -> Dict:
        """
        Returns a dictionary of dictionaries of all cleaned text data.
        :return: {
            "text_id": string
        }
        """
        count = 0
        newdict = {}

        for root, dirs, files in os.walk(dataset_name):
            for name in tqdm.tqdm(files) if verbose else files:
                if name.endswith(".txt"):
                    string = ""
                    fullpath = os.path.join(root, name)
                    # open the file in read mode and save all the contents to a string
                    with open(fullpath, "r") as file:
                        for line in file:
                            string += line

                    cleaned_text = self.clean_string(string)

                    key = os.path.splitext(name)[0]
                    newdict[key] = cleaned_text

        return newdict
        # raise NotImplementedError()

    def generate_random_text(self, max_length=None) -> str:
        """
        Returns a string that contains all characters randomly. Used to create a warm-up
        dataset to train the model on rare characters.

        :param max_length: Length of string. If specified, pick characters randomly. If None,
        generate a string that contains all characters once.
        :return:
        """
        string = ""

        max_word_length = 5  # if max sequence length without space
        while True:
            word_length = int(random.uniform(1, max_word_length + 1))
            for j in range(word_length):
                string += random.choice(self.character_list)
            if len(string) >= max_length:
                string = string[:max_length]
                break
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
        new_string = " ".join(string.split())
        return new_string.strip()


if __name__ == "__main__":
    loader = TextLoader(["가", "나", "다", "라", "마", ".", " "])
    text = loader.generate_random_text(max_length=10)
    print("Generated random text", text)

    clean_str = loader.clean_string("선(禪)의 시작은 부처님으로부터이다. 그런데 禪이란 쟈나의 음(音)을 그대로 <선나(禪那)>라고 쓰고 이를 한역하여 정려(瀞")
    print("clean text", clean_str)

    loaded_data = loader.load_data('/Users/mac/calligram/input/text/kaist_corpus')
    print("Load data", loaded_data)
