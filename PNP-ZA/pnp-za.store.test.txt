const { gatherClient, extractClient, helper } = require("../../lib");
const gatherConfigs = require("./gather");
const extractConfigs = require("./extract");
const path = require("path");
const { expect } = require("chai");
const { getGatherProductImages } = helper;

describe("PNP-ZA", () => {
  const pageType = "store";

  describe("store", () => {
    const baseDir = path.resolve(__dirname, "pages", "store");
    const url = "https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/c/beverages-423144840";

    it("gather store @slow", async () => {
      // gather page
      const config = gatherConfigs[pageType];

      const { status, pages } = await gatherClient.gatherPage(
        url,
        config,
        baseDir
      );

      // verify
      expect(status.success, 'Gather should not fail').to.equal(true);
      expect(pages, 'Amount of pages mismatch').to.have.lengthOf(1);

      const page = pages[0];

      const productLinks = page.links.filter(
        (link) => link.selector === "productLink"
      );
      expect(productLinks, 'Incorrect number of productLinks').to.have.lengthOf(18);
      expect(productLinks[0].url, 'Incorrect url for a productLink').to.equal("https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/Cold-Drinks/Carbonated-Soft-Drinks/Coca-Cola-Zero-2-25l/p/000000000000393280_EA"); 
    });

    describe("extract store", () => {
      before("extracting data...", async function () {
        const config = extractConfigs[pageType];
        const htmlPath = path.resolve(baseDir, "page.html");

        const { skus } = await extractClient.extractPage(
          url,
          pageType,
          config,
          htmlPath
        );
        this.skus = skus
      });

      it("specific test for one product", function () {
        // verify
        const selectedProduct = this.skus[1];
        expect(selectedProduct.extract.name, 'name mismatch').to.equal("Coca-Cola Soft Drink 1.5l");
        expect(selectedProduct.extract.rank, 'rank mismatch').to.equal(2);
        expect(selectedProduct.extract.price, 'price mismatch').to.equal("R17.99");
        expect(selectedProduct.extract.productNo, 'productNo mismatch').to.equal("000000000000490950_EA");

      });

      it("generic test for all products", function () {
        const gatherImages = getGatherProductImages(
          path.resolve(baseDir, "page.json")
        );
        expect(this.skus.length).to.be.at.least(2);
        this.skus.forEach((product) => {
          expect(product.extract.name, 'all products should have name').not.to.be.empty;
          expect(product.extract.productNo, 'all products should have productNo').not.to.be.empty;
          expect(product.extract.imageURL, 'all products should have imageURL').not.to.be.empty;

          if (product.extract.netQuantity) {
            expect(product.parsed.netQuantity, 'parsed netQuantities should not be undefined').not.to.be.undefined;
          }
          if (!product.extract.outOfStock) {
            expect(product.extract.price, 'parsed outOfStock should not be undefined').not.to.be.empty;
          }
          if (product.extract.pricePerUnit) {
            expect(product.parsed.pricePerUnit, 'parsed pricePerUnit should not be undefined').not.to.be.undefined;
          }
          if (product.extract.price) {
            expect(product.parsed.price, 'parsed price should not be undefined').not.to.be.undefined;
          }
          if (product.extract.subscription) {
            expect(product.extract.subscriptionPrice, 'parsed subscriptionPrice should not be undefined').not.to.be.empty;
          }
          if (product.extract.promotionText) {
            expect(product.parsed.promotionType, 'parsed promotionType should not be UNCLASSIFIED').not.to.be.equal(
              "UNCLASSIFIED"
            );
          }
          if (product.feedback) {
            expect(product.feedback.avgRating, 'feedback should have avgRating').to.be.finite;
          }
        });

        // check the same image urls are extracted
        const extractedImages = this.skus.map((sku) => sku.extract.imageURL);
        expect(extractedImages, 'gathered images are not the same than extracted').to.deep.equal(gatherImages);
      });
    });
  });

  describe("George", () => {
    const baseDir = path.resolve(__dirname, "pages", "George");
    const url = "https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/c/beverages-423144840";

    it("gather store @slow", async () => {
      // gather page
      const config = gatherConfigs[pageType];

      const metadata = {
        "storeNo": "GC64" 
      };
      const { status, pages } = await gatherClient.gatherPage(
        url,
        config,
        baseDir,
        metadata
      );

      // verify
      expect(status.success, 'Gather should not fail').to.equal(true);
      expect(pages, 'Amount of pages mismatch').to.have.lengthOf(1);

      const page = pages[0];

      const productLinks = page.links.filter(
        (link) => link.selector === "productLink"
      );
      expect(productLinks, 'Incorrect number of productLinks').to.have.lengthOf(18);
      expect(productLinks[0].url, 'Incorrect url for a productLink').to.equal("https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/Cold-Drinks/Carbonated-Soft-Drinks/Coca-Cola-Zero-2-25l/p/000000000000393280_EA"); 
    });

    describe("extract store", () => {
      before("extracting data...", async function () {
        const config = extractConfigs[pageType];
        const htmlPath = path.resolve(baseDir, "page.html");

        const { skus } = await extractClient.extractPage(
          url,
          pageType,
          config,
          htmlPath
        );
        this.skus = skus
      });

      it("specific test for one product", function () {
        // verify
        const selectedProduct = this.skus[1];
        expect(selectedProduct.extract.name, 'name mismatch').to.equal("Coca-Cola Soft Drink 1.5l");
        expect(selectedProduct.extract.price, 'price mismatch').to.equal("R17.99");
        expect(selectedProduct.extract.productNo, 'productNo mismatch').to.equal("000000000000490950_EA");

      });
    });
  })
});