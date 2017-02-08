class Card:
    """
    A wrapper around a Scryfall json card object.
    """

    def __init__(self, cardData):
        self._data = cardData

    def __getattr__(self, attr):
        """
        A hack that makes all attributes inaccessible,
        and instead returns the stored json values as class fields.
        """
        if attr in self._data and (isinstance(self._data[attr], str) or
                                   isinstance(self._data[attr], bool)):
            return str(self._data[attr]).capitalize()

        elif (isinstance(self._data[attr], dict)):
            return self.format_dict(self._data[attr])

        else:
            return "Attribute not found."

    def __contains__(self, arg):
        return arg in self._data

    def __str__(self):
        """
        Returns the string representation of a magic card.
        The ** is the Discord way to bolden the text
        """
        # Power/toughness, seen only if it's a creature
        pt = ""
        if "power" in self._data:
            pt = "{0}/{1}".format(self.power, self.toughness)

        return "**{0}** {1}\n{2} {3}\n{4}\n\n".format(self.name,
                                                      self.mana_cost,
                                                      self.type_line,
                                                      pt,
                                                      self.oracle_text)

    def format_dict(self, dict):
        """
        Converts a dict into a readble, discord compatible string.
        """

        result = ""
        for k, v in dict.items():
            result += "\n{0}: {1}".format(k.capitalize(), v)

        return "```\n{0}\n```".format(result.replace("_", " "))
