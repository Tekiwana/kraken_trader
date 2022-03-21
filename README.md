# kraken_trader
Trader bot for Kraken_api. *unfinished

Requires a Kraken.com account with permissons.
Key should be saved in kraken.key file in root directory.

This program will check the 4 month price average and 3 days price average for every crypto pair in the list.
If the current price is belowe the 4 month price average, by 25% and if the 3 days price average is above -0.8%.
The bot will buy. (Not implemented. For now only record the details in a log file)
And send an email to notify you. (disabled for now)

End of the cycle it wait 1 hour and start it again.
Selling also not implemented.

This was just a practice project.

Please do not use this bot for real trading.
