const { gatherClient, extractClient, helper } = require("../../lib");
const gatherConfigs = require("./gather");
const extractConfigs = require("./extract");
const path = require("path");
const { expect } = require("chai");
const { getGatherProductImages } = helper;

describe("PNP-ZA", () => {
  const pageType = "search";

  describe("search", () => {
    const baseDir = path.resolve(__dirname, "pages", "search");
    const url = "https://www.pnp.co.za/pnpstorefront/pnp/en/search/?text=coca+cola";

    it("gather search @slow", async () => {
      // gather page
      const config = gatherConfigs[pageType];
      const { status, pages } = await gatherClient.gatherPage(
        url,
        config,
        baseDir
      );

      // verify
      expect(status.success).to.equal(true);
      expect(pages).to.have.lengthOf(1);

      const page = pages[0];

      const productLinks = page.links.filter(
        (link) => link.selector === "productLink"
      );
      expect(productLinks, 'Incorrect number of productLinks').to.have.lengthOf(18);
      expect(productLinks[0].url, 'Incorrect url for a productLink').to.equal("https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/Cold-Drinks/Carbonated-Soft-Drinks/Coca-Cola-Soft-Drink-1-5l/p/000000000000490950_EA");

      expect(page.storage.resources, 'Incorrect number of resources').to.have.lengthOf(18);
      expect(page.storage.resources[0].url, 'Incorrect url of a single resource').to.equal("https://cdn-prd-02.pnp.co.za/sys-master/images/h39/h29/10772991246366/silo-product-image-v2-15Mar2022-180555-5449000000439-Straight_on-6954-22633_140Wx140H");
    });

    describe("extract search", () => {
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

        const selectedProduct = this.skus[0];
        expect(selectedProduct.extract.name, 'name mismatch').to.equal("Coca-Cola Soft Drink 1.5l");
        expect(selectedProduct.extract.price, 'price mismatch').to.equal("R17.99");
        expect(selectedProduct.extract.netQuantity, 'netQuantity mismatch').to.equal("1.5 l");
        expect(selectedProduct.extract.productNo, 'productNo mismatch').to.equal("000000000000490950_EA");
        expect(selectedProduct.extract.url, 'url mismatch').to.equal("https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/Cold-Drinks/Carbonated-Soft-Drinks/Coca-Cola-Soft-Drink-1-5l/p/000000000000490950_EA");
        expect(selectedProduct.extract.imageURL, 'imageURL mismatch').to.equal("https://cdn-prd-02.pnp.co.za/sys-master/images/h39/h29/10772991246366/silo-product-image-v2-15Mar2022-180555-5449000000439-Straight_on-6954-22633_140Wx140H");

        expect(selectedProduct.parsed.price, 'parsed price mismatch').to.equal(17.99);
        expect(selectedProduct.parsed.currency, 'parsed currency mismatch').to.equal("ZAR");
        expect(selectedProduct.parsed.netQuantityUnit, 'parsed netQuantityUnit mismatch').to.equal("L");
        expect(selectedProduct.parsed.netQuantity, 'parsed netQuantity mismatch').to.equal(1.5);

        expect(selectedProduct.parsed.perUnit, 'parsed perUnit mismatch').to.equal("L");
        expect(selectedProduct.parsed.pricePerUnit, 'parsed pricePerUnit mismatch').to.equal(11.993);

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
            expect(product.feedback.commentCount, 'feedback should have commentCount').to.be.finite;
          }
        });

        // check the same image urls are extracted
        const extractedImages = this.skus.map((sku) => sku.extract.imageURL);
        expect(extractedImages, 'gathered images are not the same than extracted').to.deep.equal(gatherImages);
      });
    });
  });

  describe("search no result", () => {
    const baseDir = path.resolve(__dirname, "pages", "search_no_result");
    const url = "https://www.pnp.co.za/pnpstorefront/pnp/en/search/?text=*";

    it("gather search @slow", async () => {
      // gather page
      const config = gatherConfigs[pageType];
      const { status, pages } = await gatherClient.gatherPage(
        url,
        config,
        baseDir
      );

      // verify
      expect(status.success).to.equal(true);
      expect(pages).to.have.lengthOf(1);

    });

    
  });

});