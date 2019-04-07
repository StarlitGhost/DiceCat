# DiceCat [![Build Status](https://travis-ci.org/StarlitGhost/DiceCat.svg?branch=master)](https://travis-ci.org/StarlitGhost/DiceCat) [![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/starlitghost/dicecat.svg)](https://hub.docker.com/r/starlitghost/dicecat) [![Updates](https://pyup.io/repos/github/StarlitGhost/DiceCat/shield.svg)](https://pyup.io/repos/github/StarlitGhost/DiceCat/)
A dice rolling Mastodon bot, using my dice roll library [pyhedrals](https://github.com/StarlitGhost/pyhedrals).

To use, create a config file like this:

```
[dicecat]
class = DiceCat.DiceCat
domain = mastodon.instance
```

And then run it with `ananas --interactive config.cfg` to set up client secrets and so forth.

See [ananas](https://github.com/chr-1x/ananas) for more details on the bot framework.
