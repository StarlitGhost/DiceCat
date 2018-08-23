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
        [mention.extract() for mention in soup.find_all(class_="h-card")]
        
        # put all the lines in a list
        lines = [line.text.strip() for line in soup.find_all('p')]
        
        # help command (only valid on first line)
        if lines[0].startswith("help"):
            with open("help.txt", "r") as f:
                self._send_reply("@{}\n\n{}".format(username, f.read()), status)
                return

        # loop over the lines looking for roll commands to run
        results = []
        for dice_expr in lines:
            # verbose mode
            if dice_expr.startswith("long"):
                dice_expr = dice_expr.lstrip("long")
                dice_expr = dice_expr.lstrip()
                verbose = True
            else:
                verbose = False

            # check for roll command, skip if not present
            if dice_expr.startswith("roll "):
                dice_expr = dice_expr.lstrip("roll ")
                dice_expr = dice_expr.lstrip()
            else:
                continue

            self.log("respond_roll", "Received roll {!r} from @{}".format(dice_expr, username))

            # actually do the thing
            result = self._roll(dice_expr, verbose)
            if result:
                results.append(result)

        if results:
            result = '\n'.join(results)

        self._send_reply("@{user} {result}".format(user=username, result=result), status)

    def _roll(self, dice_expr, verbose):
        roller = DiceParser()
        try:
            result = roller.parse(dice_expr)
        except OverflowError:
            return "Error: result too large to calculate :blob_cat_peek:"
        except RecursionError:
            return "Error: I ran out of dice! Try something with less explosions or rerolls :blob_cat_melt:"
        except (ZeroDivisionError,
                UnknownCharacterException,
                SyntaxErrorException,
                InvalidOperandsException,
                NotImplementedError) as e:
            return "Error: {} :blob_cat_peek:".format(e)

        # append comment text after the result
        if roller.description:
            result = "{} {}".format(result, roller.description)

        # add all the individual rolls to the output
        if verbose:
            roll_strings = roller.getRollStrings()
            roll_string = '\n'.join(roll_strings)
            if len(roll_string) > 400:
                roll_string = "LOTS OF DICE :blob_cat_fetch_ball:"
            result = "{}\n\n{}".format(result, roll_string)

        return result

    def _send_reply(self, reply, original):
        self.mastodon.status_post(reply,
                in_reply_to_id = original["id"],
                visibility = original["visibility"])
