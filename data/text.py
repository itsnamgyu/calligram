from typing import Dict, List


class TextLoader:
    def __init__(self, character_set: List):
        self.character_set = character_set

    def load_data(self, dataset_name=None) -> Dict[Dict]:
        """
        Returns a dictionary of dictionaries of all cleaned text data.
        :return: {
            "text_id": string
        }
        """
        raise NotImplementedError()

    def generate_random_text(self, length=None) -> str:
        """
        Returns a string that contains all characters randomly. Used to create a warm-up
        dataset to train the model on rare characters.

        :param length: Length of string. If specified, pick characters randomly. If None,
        generate a string that contains all characters once.
        :return:
        """
        raise NotImplementedError()

    def clean_string(self, original) -> str:
        """
        Removes all invalid characters from a string.

        Implementation notes: be wary of how to deal with spaces.

        :param original:
        :return:
        """
        raise NotImplementedError()
