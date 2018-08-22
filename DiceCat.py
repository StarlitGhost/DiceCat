from ananas import PineappleBot, reply, html_strip_tags
from pyhedrals import (
    DiceParser,
    UnknownCharacterException,
    SyntaxErrorException,
    InvalidOperandsException,
)
from bs4 import BeautifulSoup
import re

class DiceCat(PineappleBot):
    @reply
    def respond_roll(self, status, user):
        username = user["acct"]

        # strip out mentions
        soup = BeautifulSoup(status["content"], 'lxml')
        [s.extract() for s in soup.find_all(class_="h-card")]
        dice_expr = soup.text.strip()

        if dice_expr.startswith("help"):
            with open("help.txt", "r") as f:
                self._send_reply("@{}\n\n{}".format(username, f.read()), status)
                return

        if dice_expr.startswith("long"):
            dice_expr = dice_expr.lstrip("long")
            verbose = True
        else:
            verbose = False

        self.log("respond_roll", "Received roll {!r} from @{}".format(dice_expr, username))

        # actually do the thing
        roller = DiceParser()
        try:
            result = roller.parse(dice_expr)
        except OverflowError:
            self._send_reply("@{} Error: result too large to calculate :blob_cat_peek:".format(username), status)
            return
        except RecursionError:
            self._send_reply("@{} Error: I ran out of dice! Try something with less explosions or rerolls :blob_cat_melt:".format(username), status)
            return
        except (ZeroDivisionError,
                UnknownCharacterException,
                SyntaxErrorException,
                InvalidOperandsException,
                NotImplementedError) as e:
            self._send_reply("@{} Error: {} :blob_cat_peek:".format(username, e), status)
            return

        # add all the individual rolls to the output
        if verbose:
            roll_strings = roller.getRollStrings()
            roll_string = '\n'.join(roll_strings)
            if len(roll_string) > 400:
                roll_string = "LOTS OF DICE :blob_cat_fetch_ball:"
            result = "{}\n\n{}".format(result, roll_string)

        self._send_reply("@{} {}".format(username, result), status)

    def _send_reply(self, reply, original):
        self.mastodon.status_post(reply,
                in_reply_to_id = original["id"],
                visibility = original["visibility"])
