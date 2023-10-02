# Appviewx-Project

Team members :
              - Vamsi Krishna . U (21pd38)
              - Vishwajeet Bharadwaj . S (21pt38)

We have developed a Flask-based local server that creates a dynamic auctioner and bidder system. It is a combination of frontend, backend and mysql database framework . Users can log in as either auctioneers or bidders, each with distinct functionalities. Auctioneers have the ability to to create new auctions, manage their own auctions, and monitor both their own auction listings and the successful bidders. Meanwhile, bidders can participate in auctions created by auctioneers. The project also offers user-friendly dashboards and interfaces to provide a comprehensive understanding of the auction process.


Frontend - Html, css, javascript;
Backend - python;
Database - Mysql;

Firstly, requirements -
                         visual studio code;
                         flask;
                         mysql workbench 8.0;
                         mysql-python-connector;

Secondly, make sure to create necessary tables (auctioners, bidders, auction_items, bid_transactions, successful_bids)
- Connect these tables to the python code using mysql-python-connector

- You can create tables by checking 'table_creation.txt' in the same repository

To run the code, run the main.py to access the login page, we can login as either auctioner or bidder

After logging, you can have the distinct privileges to manage or bid auctions. Thank you!

Note : The jpg images in the repository are just for testing purposes
       and successful_bids table gets updated only when end_time of an item is exceeded (it returns the maximum bid of that particular item)
