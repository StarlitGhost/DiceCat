from ananas import PineappleBot, reply
from pyhedrals import (
    DiceParser,
    UnknownCharacterException,
    SyntaxErrorException,
    InvalidOperandsException,
)
from bs4 import BeautifulSoup


class DiceCat(PineappleBot):
    @reply
    def respond_roll(self, status, user):
        username = user["acct"]

        # decode the toot into raw text
        soup = BeautifulSoup(status["content"], "lxml")
        #  strip out mentions
        for mention in status["mentions"]:
            for a in soup.find_all(href=mention["url"]):
                a.extract()
        #  put all the lines in a list
        #   replace <br /> tags with a newline
        for br in soup.find_all("br"):
            br.replace_with('\n')
        #   then replace consecutive p tags with a double newline
        lines = [line.text for line in soup.find_all('p')]
        lines = '\n\n'.join(lines)
        #   finally split all the lines up at the newlines we just added
        lines = [line.strip() for line in lines.splitlines() if line.strip()]
        
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

        # if we have results, join them all up, otherwise abort
        if results:
            result = '\n'.join(results)
        else:
            return

        self._send_reply("@{user} {result}".format(user=username, result=result), status)

    def _roll(self, dice_expr, verbose):
        roller = DiceParser()
        try:
            result = "{}".format(roller.parse(dice_expr))
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
            roll_string = '\n '.join(roll_strings)
            # the roll string is too long, cut it
            if len(roll_string) > 400:
                roll_string = "LOTS OF DICE :blob_cat_fetch_ball:"
            result = "{}\n {}".format(result, roll_string)

        return result

    def _send_reply(self, reply, original):
        self.mastodon.status_post(reply,
                in_reply_to_id = original["id"],
                visibility = original["visibility"])
