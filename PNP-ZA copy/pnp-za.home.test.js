const { gatherClient, extractClient, helper } = require("../../lib");
const gatherConfigs = require("./gather");
const extractConfigs = require("./extract");
const path = require("path");
const { expect } = require("chai");
const {hashDataUri } = helper;

describe("PNP-ZA", () => {

  describe("home", () => {

    const baseDir = path.resolve(__dirname, "pages", "home");
    const pageType = "home";
    const url = "https://www.pnp.co.za/";

    it("gather home @slow", async () => {
      // gather page
      const config = gatherConfigs[pageType];
      const { status, pages } = await gatherClient.gatherPage(url, config, baseDir);

      // verify
      expect(status.success, "Gather should not fail").to.equal(true);
      expect(pages, "Amount of pages mismatch").to.have.lengthOf(1);
      const page = pages[0];

      expect(page.storage.resources, "Incorrect number of resources").to.have.lengthOf(5);
      expect(page.storage.resources[0].url, "Incorrect url of a single resource").to.equal("3819678625");
    });

    it("extract home", async () => {
      const config = extractConfigs[pageType];
      const htmlPath = path.resolve(baseDir, "page.html");
      const metadata = { journey: "Home" };
      const { banners } = await extractClient.extractPage(url, pageType, config, htmlPath, metadata);

      // verify
      expect(banners.length, "Incorrect number of banners").to.equal(5);

      const carouselBanners = banners.map(banner => {
        return {
          ...banner,
          imageURL: hashDataUri(banner.imageURL)
        };
      });
      
      // generic banner test
      banners.forEach((banner, i) => {
        expect(banner.url, "Banner URL mismatch").to.equal("https://www.pnp.co.za/");
        expect(banner.pageType, "Banner pageType mismatch").to.equal("home");
        expect(banner.retailer, "Banner retailer mismatch").to.equal("PNP-ZA");
        expect(banner.journey, "Banner journey mismatch").to.equal("Home");
        expect(banner.channel, "Banner channel mismatch").to.equal("desktop");
        expect(banner, "Banner is missing gatherTimestamp").to.have.property("gatherTimestamp");
        expect(banner, "Banner is missing imageURL").to.have.property("imageURL");
        expect(banner, "Banner is missing href").to.have.property("href");
      });

      // carousel banner test
      expect(carouselBanners[0], "Carousel banner mismatch").to.deep.include({
        imageURL: "3819678625",
        href: "https://www.pnp.co.za/easter-2023",
        rank: 1,
        position: "top"
      });
      expect(carouselBanners[1], "Carousel banner mismatch").to.deep.include({
        imageURL: "288884764",
        href: "https://www.pnp.co.za/ramadan-2023",
        rank: 2,
        position: "top"
      });
      expect(carouselBanners[2], "Carousel banner mismatch").to.deep.include({
        imageURL: "2627324994",
        href: "https://www.pnp.co.za/c/weekly-savings032023",
        rank: 3,
        position: "top"
      });
      expect(carouselBanners[3], "Carousel banner mismatch").to.deep.include({
        imageURL: "3487418929",
        href: "https://www.pnphome.co.za/win-with-lift",
        rank: 4,
        position: "top"
      });
      expect(carouselBanners[4], "Carousel banner mismatch").to.deep.include({
        imageURL: "918341128",
        href: "https://www.pnp.co.za/money/financial-services/store-account",
        rank: 5,
        position: "top"
      });
      
    });
  });
});