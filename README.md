# Chainmail Pricing

## Overview

The purpose of this project is to scrape chainmail ring data from various chainmail supply vendors and store the data in a normalized fashion to allow for comparisons between vendors.


## Responsibility

For each of the vendors whose websites I will scrape in this project I have checked their website for a robots.txt file and will comply with the restrictions set out in it.


## Vendors

Using the [vendor page](https://chainmaillers.com/reviews/categories/suppliers.4/) on [chainmaillers.com](https://chainmaillers.com/) I created the following list of potential vendors for scraping. In the chart I will include the name of the vendor as a link to their website, whether or not scraping the vendor's product pages is allowed or not, whether or not I plan to scrape the vendor, whether or not I have scrapped the vendor as well as notes on the vendor.

| **Vendor**                                                                    | **Scraping Allowed** | **Will Scrape** | **Has Been Scraped** | **Notes**                                                                                  |
|-------------------------------------------------------------------------------|----------------------|-----------------|----------------------|--------------------------------------------------------------------------------------------|
| [Aussie Maille](https://www.aussiemaille.com/)                                | Yes                  | Yes             |                      |                                                                                            |
| [Bracken Maille](https://brackenmaille.com/)                                  | Yes                  | Yes             |                      |                                                                                            |
| [Chainmaille Joe](https://www.chainmailjoe.com/)                              | Yes                  | Yes             |                      |                                                                                            |
| [Dragon Chains](https://www.dragonchains.com/)                                | Yes                  | Yes             |                      | The layout makes it appear that this will not be easy to scrape                            |
| [Joshua Dilberto](https://www.joshuadiliberto.com/JD_newWebPages/index.php)   | Yes                  | Yes             |                      | Their robots.txt file only contains a link to the sitemap, so I assume it is ok to scrape. |
| [Metal Designz](https://www.metaldesignz.com/)                                | Yes                  | Yes             |                      | They seem to have a large number and variety of products                                   |
| [The Ring Lord](https://theringlord.com/)                                     | Yes                  | Yes             |  Yes                 |                                                                                            |
| [Weave Got Maille](https://weavegotmaille.com/)                               | Yes                  | Yes             |                      | They have a very wide variety of materials available.                                      |
| [West Coast Chainmail](https://www.westcoastchainmail.com/index.html)         | Yes                  | Yes             |                      | Their robots.txt file only contains a link to the sitemap, so I assume it is ok to scrape. |
| [Whitney Maille](https://whitneymaille.square.site/)                          | Yes                  | Yes             |                      |                                                                                            |
| [WraithMaille](https://www.wraithmaille.co.uk/)                               | Yes                  | Future          |                      |                                                                                            |
| [HyperLynks](https://hyperlynks.ca/index.html)                                | Yes                  | No              |                      | They don't sell anything directly                                                          |
| [Bead Me a Story](https://www.beadmeastory.com/)                              | No                   | No              |                      | It appears this may be due to using shopify and not customizing product page urls          |
| [Blue Buddha Boutique](http://www.bluebuddhaboutique.com/)                    | No                   | No              |                      | All sales are through etsy(no scraping allowed)                                            |
| [Chain Reaction](https://www.chain-reaction.ca/)                              | No                   | No              |                      | It appears this may be due to using shopify and not customizing product page urls          |
| [Creating Unkamen](https://www.wraithmaille.co.uk/)                           | No                   | No              |                      | It appears this may be due to using shopify and not customizing product page urls          |
| [Maille Order Rings Australia](https://www.mailleorderringsaustralia.com.au/) | No                   | No              |                      | It appears this may be due to using shopify and not customizing product page urls          |
| [Steampunk Garage](https://www.etsy.com/shop/spgsupplies/?etsrc=sdt)          | No                   | No              |                      | This is an etsy shop(etsy does not allow scraping).                                        |
| [Toms Ringshop](https://toms-ringshop.at/)                                    | No                   | No              |                      | It appears this may be due to using shopify and not customizing product page urls          |
| [C & T Designs](http://www.candtdesigns.com/)                                 | N/A                  | No              |                      | They appear to have gone out of business                                                   |
| [Chainweavers](https://chainweavers.com/)                                     | N/A                  | No              |                      | They appear to have gone out of business                                                   |

## Steps

1. Determine list of vendors of interest.
2. Determine which vendors of interest are scrapable/should be scraped.
3. For each vendor to be scraped figure out the following:
    * List of products that need to be scraped.
    * For each product that needs scraped how to get the following data:
        * Wire Gauge
        * Internal Diameter
        * Quantity
        * Material
        * Color
        * Price
        * Currency
4. Find a way to compare the scraped data across vendors.
5. Find a way to scrape the data periodically and store it.
