const { gatherClient, extractClient, helper } = require("../../lib");
const gatherConfigs = require("./gather");
const extractConfigs = require("./extract");
const path = require("path");
const { expect } = require("chai");
const exp = require("constants");
const { getGatherProductImages } = helper;

describe("PNP-ZA", () => {
  const pageType = "category";

  describe("category", () => {
    const baseDir = path.resolve(__dirname, "pages", "category");
    const url = "https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/c/beverages-423144840";

    it("gather category @slow", async () => {
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

      const nextPageLinks = page.links.filter(
        (link) => link.selector === "nextPageLink"
      );
      expect(nextPageLinks, 'Incorrect number of nextPageLinks').to.have.lengthOf(1);
      expect(nextPageLinks[0].url, 'Incorrect url for a nextPageLink').to.equal("https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/c/beverages-423144840?q=%3Arelevance&page=1");

      expect(page.storage.resources, 'Incorrect number of resources').to.have.lengthOf(18);
      expect(page.storage.resources[0].url, 'Incorrect url of a single resource').to.equal("https://cdn-prd-02.pnp.co.za/sys-master/images/h4a/h89/10675823018014/silo-product-image-v2-08Feb2022-181059-5449000061768-Straight_on-231-10528_140Wx140H");
    });

    describe("extract category", () => {
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
        
        expect(selectedProduct.extract.name, 'name mismatch').to.equal("Coca-Cola Zero 2.25l");
        expect(selectedProduct.extract.rank, 'rank mismatch').to.equal(1);
        expect(selectedProduct.extract.breadcrumbText, 'breadcrumbText mismatch').to.equal("Beverages");
        expect(selectedProduct.extract.badge, 'badge mismatch').to.equal("MAX 30 PER ORDER");
        expect(selectedProduct.extract.price, 'price mismatch').to.equal("R20.99");
        expect(selectedProduct.extract.netQuantity, 'netQuantity mismatch').to.equal("2.25 l");
        expect(selectedProduct.extract.productNo, 'productNo mismatch').to.equal("000000000000393280_EA");
        expect(selectedProduct.extract.url, 'url mismatch').to.equal("https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/Cold-Drinks/Carbonated-Soft-Drinks/Coca-Cola-Zero-2-25l/p/000000000000393280_EA");
        expect(selectedProduct.extract.imageURL, 'imageURL mismatch').to.equal("https://cdn-prd-02.pnp.co.za/sys-master/images/h4a/h89/10675823018014/silo-product-image-v2-08Feb2022-181059-5449000061768-Straight_on-231-10528_140Wx140H");

        expect(selectedProduct.parsed.price, 'parsed price mismatch').to.equal(20.99);
        expect(selectedProduct.parsed.currency, 'parsed currency mismatch').to.equal("ZAR");
        expect(selectedProduct.parsed.netQuantityUnit, 'parsed netQuantityUnit mismatch').to.equal("L");
        expect(selectedProduct.parsed.netQuantity, 'parsed netQuantity mismatch').to.equal(2.25);

        expect(selectedProduct.parsed.perUnit, 'parsed perUnit mismatch').to.equal("L");
        expect(selectedProduct.parsed.pricePerUnit, 'parsed pricePerUnit mismatch').to.equal(9.329);

        expect(selectedProduct.parsed.promotionType, 'parsed promotionType mismatch').to.equal("MULTI_BUY");
        expect(selectedProduct.extract.promotionText, 'promotionText mismatch').to.equal("Buy Any 2 For R34.00 (Smart Price)");
        expect(selectedProduct.parsed.discount, 'parsed discount mismatch').to.equal(19.01);
        expect(selectedProduct.parsed.originalPrice, 'parsed originalPrice mismatch').to.equal(20.99);
        expect(selectedProduct.parsed.promotionPrice, 'parsed promotionPrice mismatch').to.equal(17);
        expect(selectedProduct.parsed.promotionPricePerUnit, 'parsed promotionPricePerUnit mismatch').to.equal(7.556);
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

  describe("category-bevrages", () => {
    const baseDir = path.resolve(__dirname, "pages", "category-bevrages");
    const url = "https://www.pnp.co.za/pnpstorefront/pnp/en/Weekly-Savings/c/weekly-savings522023?q=%3Arelevance%3AisOnPromotion%3AOn%2BPromotion&text=&pageSize=18";

    it("gather category @slow", async () => {
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
      expect(productLinks[13].url, 'Incorrect url for a productLink').to.equal("https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Food-Cupboard/Baking-Ingredients/Jelly-%26-Custards/Long-Life-Custard/Danone-Ultra-Mel-Vanilla-Flavoured-Custard-1L/p/000000000000148952_EA");

      const nextPageLinks = page.links.filter(
        (link) => link.selector === "nextPageLink"
      );
      expect(nextPageLinks, 'Incorrect number of nextPageLinks').to.have.lengthOf(1);
      expect(nextPageLinks[0].url, 'Incorrect url for a nextPageLink').to.equal("https://www.pnp.co.za/pnpstorefront/pnp/en/Weekly-Savings/c/weekly-savings522023?q=%3Arelevance%3AisOnPromotion%3AOn%2BPromotion&page=1");

      expect(page.storage.resources, 'Incorrect number of resources').to.have.lengthOf(18);
      expect(page.storage.resources[13].url, 'Incorrect url of a single resource').to.equal("https://cdn-prd-02.pnp.co.za/sys-master/images/h8a/hb1/11009425375262/silo-product-image-v2-09Nov2022-180128-6009708460257-Straight_on-71253-5700_140Wx140H");
    });

    describe("extract category", () => {
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

        const selectedProduct = this.skus[6];
        expect(selectedProduct.extract.name, 'name mismatch').to.equal("Bakers Red Label Lemon Creams 200g");
        expect(selectedProduct.extract.price, 'price mismatch').to.equal("R23.99");
        expect(selectedProduct.extract.url, 'url mismatch').to.equal("https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Food-Cupboard/Biscuits-%26-Crackers/Biscuits/Everyday-Biscuits/Bakers-Red-Label-Lemon-Creams-200g/p/000000000000137350_EA");
        expect(selectedProduct.extract.imageURL, 'imageURL mismatch').to.equal("https://cdn-prd-02.pnp.co.za/sys-master/images/h6e/h56/11100663513118/silo-product-image-v2-02Mar2023-235253-6001056411004-Straight_on-113116-8894_140Wx140H");
        expect(selectedProduct.extract.promotionText, 'striked price mismatch').to.equal("Smart Price: R17.99");
        
        expect(selectedProduct.parsed.price, 'parsed price mismatch').to.equal(23.99);
        expect(selectedProduct.parsed.currency, 'parsed currency mismatch').to.equal("ZAR");
        expect(selectedProduct.parsed.netQuantityUnit, 'parsed netQuantityUnit mismatch').to.equal("KG");
        expect(selectedProduct.parsed.netQuantity, 'parsed netQuantity mismatch').to.equal(0.2);

        expect(selectedProduct.parsed.perUnit, 'parsed perUnit mismatch').to.equal("KG");
        expect(selectedProduct.parsed.pricePerUnit, 'parsed pricePerUnit mismatch').to.equal(119.95);

        expect(selectedProduct.parsed.promotionType, 'parsed promotionType mismatch').to.equal("PRICE_CUT");
        expect(selectedProduct.parsed.discount, 'parsed discount mismatch').to.equal(25.01);
        expect(selectedProduct.parsed.originalPrice, 'parsed originalPrice mismatch').to.equal(23.99);
        expect(selectedProduct.parsed.promotionPrice, 'parsed promotionPrice mismatch').to.equal(17.99);
        expect(selectedProduct.parsed.promotionPricePerUnit, 'parsed promotionPricePerUnit mismatch').to.equal(89.95);
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

  describe("category-bevrages-2", () => {
    const baseDir = path.resolve(__dirname, "pages", "category-bevrages-2");
    const url = "https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/c/beverages-423144840?sort=price-asc&q=%3Arelevance%3Abrand%3ALIQUI-FRUIT&show=Page#";

    it("gather category @slow", async () => {
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
      expect(productLinks[0].url, 'Incorrect url for a productLink').to.equal("https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/Cold-Drinks/Carbonated-Soft-Drinks/Liqui-fruit-Spark-Cranberry-Cooler-250-Ml/p/000000000000715442_EA");

      const nextPageLinks = page.links.filter(
        (link) => link.selector === "nextPageLink"
      );
      expect(nextPageLinks, 'Incorrect number of nextPageLinks').to.have.lengthOf(1);
      expect(nextPageLinks[0].url, 'Incorrect url for a nextPageLink').to.equal("https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/c/beverages-423144840?q=%3Aprice-asc%3Abrand%3ALIQUI-FRUIT&page=1");

      expect(page.storage.resources, 'Incorrect number of resources').to.have.lengthOf(14);
      expect(page.storage.resources[0].url, 'Incorrect url of a single resource').to.equal("https://cdn-prd-02.pnp.co.za/sys-master/images/hc2/ha5/9228241535006/silo-6001240235096-front-296093_140Wx140H");
    });

    describe("extract category", () => {
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
        expect(selectedProduct.extract.name, 'name mismatch').to.equal("Liqui-fruit Spark Cranberry Cooler 250 Ml");
        expect(selectedProduct.extract.price, 'price mismatch').to.equal("R9.49");
        expect(selectedProduct.extract.url, 'url mismatch').to.equal("https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/Cold-Drinks/Carbonated-Soft-Drinks/Liqui-fruit-Spark-Cranberry-Cooler-250-Ml/p/000000000000715442_EA");
        expect(selectedProduct.extract.imageURL, 'imageURL mismatch').to.equal("https://cdn-prd-02.pnp.co.za/sys-master/images/hc2/ha5/9228241535006/silo-6001240235096-front-296093_140Wx140H");
       
      });
    });
  });

});