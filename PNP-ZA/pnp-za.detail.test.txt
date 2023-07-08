const { gatherClient, extractClient, helper } = require("../../lib");
const gatherConfigs = require("./gather");
const extractConfigs = require("./extract");
const path = require("path");
const { expect } = require("chai");
const { equal } = require("assert");
const { getGatherProductImages } = helper;

describe("PNP-ZA", () => {
  const pageType = "detail";

  describe("detail", () => {
    const baseDir = path.resolve(__dirname, "pages", "detail");
     const url = "https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/Cold-Drinks/Carbonated-Soft-Drinks/Coca-Cola-Soft-Drink-1-5l/p/000000000000490950_EA";
      
     it("gather detail @slow", async () => {
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

      expect(page.storage.resources, 'Incorrect number of resources').to.have.lengthOf(3);
      expect(page.storage.resources[0].url, 'Incorrect url of a single resource').to.equal("https://cdn-prd-02.pnp.co.za/sys-master/images/h83/h81/10772990787614/silo-product-image-v2-15Mar2022-180555-5449000000439-Straight_on-6954-22633_400Wx400H");
    });

    it("extract detail", async () => {
      const config = extractConfigs[pageType];
      const htmlPath = path.resolve(baseDir, "page.html");
      const gatherImages = getGatherProductImages(
        path.resolve(baseDir, "page.json")
      );

      const { skus } = await extractClient.extractPage(
        url,
        pageType,
        config,
        htmlPath
      );

      // verify
      expect(skus.length).to.be.at.least(1);

      const product = skus[0];

      // check the same image urls are extracted
       expect(product.extract.imageURL).to.deep.equal(gatherImages);

      expect(product.gather.url, 'url mismatch').to.equal("https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/Cold-Drinks/Carbonated-Soft-Drinks/Coca-Cola-Soft-Drink-1-5l/p/000000000000490950_EA");
      
      expect(product.extract.name, 'name mismatch').to.equal("Coca-Cola Soft Drink 1.5l");
      expect(product.extract.netQuantity, 'netQuantity mismatch').to.equal("1.5 l");
      expect(product.extract.price, 'price mismatch').to.equal("R17.99");
      expect(product.extract.productNo, 'productNo mismatch').to.equal("000000000000490950_EA");
      expect(product.extract.gtin, 'gtin mismatch').to.equal("5449000000439");
      expect(product.extract.description, 'description mismatch').to.equal("This lower-kilojoule soft drink is the same Coca-Cola with the original taste, just with less sugar. Beyond just the flavour, Coke No Sugar is an attitude. It’s about setting your own rules, standing your ground and challenging the status quo.");
      expect(product.extract.ingredients, 'ingredients mismatch').to.equal("Carbonated Water, Sugar, Caramel, Phosphoric Acid, Flavouring and Caffeine");
      expect(product.extract.imageURL, 'imageURL mismatch').to.deep.equal([
        "https://cdn-prd-02.pnp.co.za/sys-master/images/h83/h81/10772990787614/silo-product-image-v2-15Mar2022-180555-5449000000439-Straight_on-6954-22633_400Wx400H",
        "https://cdn-prd-02.pnp.co.za/sys-master/images/h44/hd4/10772994916382/silo-product-image-v2-15Mar2022-180556-5449000000439-Angle_D-6956-22644_400Wx400H",
        "https://cdn-prd-02.pnp.co.za/sys-master/images/heb/hd2/10772998914078/silo-product-image-v2-15Mar2022-180556-5449000000439-Angle_A-6955-22637_400Wx400H",
      ]);

      expect(product.parsed.price, 'parsed price mismatch').to.equal(17.99);
      expect(product.parsed.currency, 'parsed currency mismatch').to.equal("ZAR");
      expect(product.parsed.netQuantityUnit, 'parsed netQuantityUnit mismatch').to.equal("L");
      expect(product.parsed.netQuantity, 'parsed netQuantity mismatch').to.equal(1.5);

      expect(product.parsed.pricePerUnit, 'parsed pricePerUnit mismatch').to.equal(11.993);
      expect(product.parsed.perUnit, 'parsed perUnit mismatch').to.equal("L");

      });
  });

  describe("detail-2", () => {
    const baseDir = path.resolve(__dirname, "pages", "detail-2");
     const url = "https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/Cold-Drinks/Carbonated-Soft-Drinks/Coca-Cola-Plastic-2L/p/000000000000312875_EA";
      
    it("gather detail @slow", async () => {
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

      expect(page.storage.resources, 'Incorrect number of resources').to.have.lengthOf(3);
      expect(page.storage.resources[0].url, 'Incorrect url of a single resource').to.equal("https://cdn-prd-02.pnp.co.za/sys-master/images/hac/h0b/10771938902046/silo-product-image-v2-15Mar2022-180405-5449000009067-Straight_on-12454-20337_400Wx400H");
    });

    it("extract detail", async () => {
      const config = extractConfigs[pageType];
      const htmlPath = path.resolve(baseDir, "page.html");
      const gatherImages = getGatherProductImages(
        path.resolve(baseDir, "page.json")
      );

      const { skus } = await extractClient.extractPage(
        url,
        pageType,
        config,
        htmlPath
      );

      // verify
      expect(skus.length).to.be.at.least(1);

      const product = skus[0];

      // check the same image urls are extracted
      expect(product.extract.imageURL).to.deep.equal(gatherImages);

      expect(product.gather.url, 'url mismatch').to.equal("https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/Cold-Drinks/Carbonated-Soft-Drinks/Coca-Cola-Plastic-2L/p/000000000000312875_EA");
      
      expect(product.extract.name, 'name mismatch').to.equal("Coca-Cola Plastic 2L");
      expect(product.extract.price, 'price mismatch').to.equal("R23.99");
      expect(product.extract.features, 'features mismatch').to.deep.equal([
          "Less sugar",
          "New sweetener blend",
      ]);
      expect(product.extract.bulletPoints, 'bulletPoints mismatch').to.deep.equal([
        "Less sugar",
        "New sweetener blend",
      ]);

      expect(product.parsed.price, 'parsed price mismatch').to.equal(23.99);
      expect(product.parsed.currency, 'parsed currency mismatch').to.equal("ZAR");
      expect(product.parsed.netQuantityUnit, 'parsed netQuantityUnit mismatch').to.equal("L");
      expect(product.parsed.netQuantity, 'parsed netQuantity mismatch').to.equal(2);

      expect(product.parsed.pricePerUnit, 'parsed pricePerUnit mismatch').to.equal(11.995);
      expect(product.parsed.perUnit, 'parsed perUnit mismatch').to.equal("L");

      });
  });

  describe("detail-extrafree", () => {
    const baseDir = path.resolve(__dirname, "pages", "detail-extrafree");
     const url = "https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/Cold-Drinks/Carbonated-Soft-Drinks/Schweppes-Ginger-Ale-Plastic-Bottle-1l/p/000000000000211650_EA";
     const metadata = {
      "storeNo": "GC64" 
    };
    it("gather detail @slow", async () => {
      // gather page
      const config = gatherConfigs[pageType];
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

      expect(page.storage.resources, 'Incorrect number of resources').to.have.lengthOf(2);
      expect(page.storage.resources[0].url, 'Incorrect url of a single resource').to.equal("https://cdn-prd-02.pnp.co.za/sys-master/images/h7e/h77/10791323369502/silo-product-image-v2-02Apr2022-180120-5449000045515-Straight_on-17588-2611_400Wx400H");
    });

    it("extract detail", async () => {
      const config = extractConfigs[pageType];
      const htmlPath = path.resolve(baseDir, "page.html");
      const gatherImages = getGatherProductImages(
        path.resolve(baseDir, "page.json")
      );

      const { skus } = await extractClient.extractPage(
        url,
        pageType,
        config,
        htmlPath
      );

      // verify
      expect(skus.length).to.be.at.least(1);

      const product = skus[0];
      // check the same image urls are extracted
      expect(product.extract.imageURL).to.deep.equal(gatherImages);

      expect(product.extract.name, 'name mismatch').to.equal("Schweppes Ginger Ale Plastic Bottle 1l");
      expect(product.extract.price, 'price mismatch').to.equal("R16.99");  

      expect(product.parsed.price, 'parsed price mismatch').to.equal(16.99);
      expect(product.parsed.currency, 'parsed currency mismatch').to.equal("ZAR");
      expect(product.parsed.netQuantityUnit, 'parsed netQuantityUnit mismatch').to.equal("L");
      expect(product.parsed.netQuantity, 'parsed netQuantity mismatch').to.equal(1);

      expect(product.parsed.pricePerUnit, 'parsed pricePerUnit mismatch').to.equal(16.99);
      expect(product.parsed.perUnit, 'parsed perUnit mismatch').to.equal("L");
      });
  });

  describe("detail nutrition", () => {
    const baseDir = path.resolve(__dirname, "pages", "detail-nutrition");
    const url =
      "https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/Water/Flavoured-Water/Bonaqua-Pump-Still-Lemon-Flavoured-Drink-750ml-x-6/p/000000000000783004_CK";

    it("gather detail @slow", async () => {
      // gather page
      const config = gatherConfigs[pageType];
      const { status, pages } = await gatherClient.gatherPage(
        url,
        config,
        baseDir
      );

      // verify
      expect(status.success, "Gather should not fail").to.equal(true);
      expect(pages, "Amount of pages mismatch").to.have.lengthOf(1);
      const page = pages[0];

      expect(page.storage.resources, "Incorrect number of resources").to.have.lengthOf(3);
      expect(page.storage.resources[0].url, "Incorrect url of a single resource").to.equal(
        "https://cdn-prd-02.pnp.co.za/sys-master/images/h61/hfd/11120512368670/silo-product-image-v2-16Mar2023-180919-5449000265616-Straight_on-113666-1724_400Wx400H"
      );
    });

    it("extract detail nutrition", async () => {
      const config = extractConfigs[pageType];
      const htmlPath = path.resolve(baseDir, "page.html");
      const gatherImages = getGatherProductImages(
        path.resolve(baseDir, "page.json")
      );

      const { skus } = await extractClient.extractPage(
        url,
        pageType,
        config,
        htmlPath
      );

      // verify
      expect(skus.length).to.be.at.least(1);

      const product = skus[0];

      // check the same image urls are extracted
      expect(product.extract.imageURL).to.deep.equal(gatherImages);

      expect(product.extract.name, "name mismatch").to.equal(
        "Bonaqua Pump Still Lemon Flavoured Drink 750ml x 6"
      );
      expect(product.extract.price, "price mismatch").to.equal("R78.99");
      expect(product.extract.netQuantity, "netQuantity mismatch").to.equal("750ml x 6");
      expect(product.extract.productNo, "productNo mismatch").to.equal("000000000000783004_CK");
      expect(product.extract.gtin, "gtin mismatch").to.equal("5449000265616");
      expect(product.extract.imageURL, "imageURL mismatch").to.deep.equal([
        "https://cdn-prd-02.pnp.co.za/sys-master/images/h61/hfd/11120512368670/silo-product-image-v2-16Mar2023-180919-5449000265616-Straight_on-113666-1724_400Wx400H",
        "https://cdn-prd-02.pnp.co.za/sys-master/images/h82/hbe/11120516988958/silo-product-image-v2-16Mar2023-180920-5449000265616-Angle_A-113668-1725_400Wx400H",
        "https://cdn-prd-02.pnp.co.za/sys-master/images/h44/hf3/11120520790046/silo-product-image-v2-16Mar2023-180921-5449000265616-Angle_D-113670-1732_400Wx400H",
      ]);
      expect(product.extract.nutrition, "nutrition mismatch").to.equal(
        "Per 100 g/ml Per Serving (100ml) Energy 59 kJ 59 kJ Carbohydrate 4 g 4 g of which total sugar 3.5 g 3.6 g Total Sodium 27 mg 27 mg"
      );
    });
  });
});