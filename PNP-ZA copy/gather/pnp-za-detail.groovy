import com.uk.ef.crawl.Action
import com.uk.ef.crawl.Browser
import com.uk.ef.crawl.GrabberDelegate
import com.uk.ef.model.GatherURL
import com.uk.ef.crawl.util.Scroll
import org.openqa.selenium.*
import org.openqa.selenium.support.ui.FluentWait
import org.openqa.selenium.support.ui.Wait
import java.util.concurrent.TimeUnit
import com.uk.ef.exceptions.*

import static org.openqa.selenium.support.ui.ExpectedConditions.*

WebDriver driver = getProperty(Browser.SCRIPT_PARAM_DRIVER) as WebDriver
JavascriptExecutor js = driver as JavascriptExecutor
Action a = getProperty(Browser.SCRIPT_PARAM_ACTION) as Action
GatherURL gurl = getProperty(Browser.SCRIPT_PARAM_GATHER_URL) as GatherURL

final String imageSelector = gurl.resourceSelectors.findAll { it.name == "productImage" }.collect { it.query }.join(",")
By byImageSelector = By.cssSelector(imageSelector)
By accordionButtonLocator = By.cssSelector('div.collapsed')

Wait<WebDriver> wait = new FluentWait<>(driver)
        .pollingEvery(500, TimeUnit.MILLISECONDS)
        .withTimeout(10, TimeUnit.SECONDS)
        .ignoring(NoSuchElementException.class)

Wait<WebDriver> shortWait = new FluentWait<>(driver)
        .pollingEvery(200, TimeUnit.MILLISECONDS)
        .withTimeout(3, TimeUnit.SECONDS)
        .ignoring(NoSuchElementException.class)

a.step = "init"
final def storeNo = gatherURL.metadata['storeNo'] ?: 'HC06'

def waitForMainContent = {
    a.step = "Wait for main Layout to load"
    By mainContent = By.cssSelector(".js-product-card-item")
    wait.until(visibilityOfElementLocated(mainContent))
}

def waitForProductImage = {
    a.step = "wait for image to load"
    wait.until(presenceOfElementLocated(byImageSelector))
}

def closePopups = {
    a.step = "Close Popups"
    try {
            By popupButton = By.cssSelector(".close-button")
            WebElement btn = shortWait.until(visibilityOfElementLocated(popupButton))
            js.executeScript("arguments[0].click()", btn)
            shortWait.until(invisibilityOfElementLocated(popupButton))
            a.log("closed popups")

    } catch (WebDriverException ignored) {
        a.log("failed to close popups"+ ignored)
    }
}

def openAccordionTabs = {
    try{
        a.step = "Open Accordions"
        js.executeScript("const allTabs = document.querySelectorAll('div.collapsed');\
                        allTabs.forEach(ele=>ele.click());")

    }catch(ignored) {
        a.log("Unable to open accordion "+ignored)
    }

}

def getBrand = {
    try{
        action.step = "Getting brand name"
        def brand = js.executeScript("return dataLayer[0].ecommerce.detail.products[0].brand")
        action.step = "Brand name: $brand"
        if(brand){
            action.step = "Attaching brand to dom"
            js.executeScript("const divBrand = document.createElement('div'); \
                    divBrand.style.display='none'; \
                    divBrand.setAttribute('class', 'ef-custom-brand'); \
                    divBrand.innerHTML = arguments[0]; \
                    document.querySelector('div.bottom-bar').appendChild(divBrand);", brand)
        }
        else{
            a.log("brand not found")
        }
    } catch (Exception ignored) {
        a.log("Brand not found")
    }
}

def isStoreSelected = {
    def selectedStoreNo = js.executeScript(""" 
        if(window.dataLayer[0].baseStoreCode == '$storeNo'){ return true}
        return false
    """);
    if(selectedStoreNo){
        a.step = "Store is already selected"
    }
    return selectedStoreNo
}

def selectStore = { storeNumber ->
    a.step = "set store using API"
    
    def storeUpdated = js.executeScript("""
                            const token = ACC.config.CSRFToken;
                            return await fetch("https://www.pnp.co.za/pnpstorefront/basestore/" + arguments[0], {
                              "headers": {
                                "accept": "*/*",
                                "accept-language": "en-US,en;q=0.9,fr;q=0.8",
                                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                "sec-fetch-dest": "empty",
                                "sec-fetch-mode": "cors",
                                "sec-fetch-site": "same-origin",
                                "x-requested-with": "XMLHttpRequest"
                              },
                              "referrerPolicy": "strict-origin-when-cross-origin",
                              "body": "CSRFToken=" + token,
                              "method": "POST",
                              "mode": "cors",
                              "credentials": "include"
                            }).then(res => res.ok)
                        """, storeNumber)
    if(!storeUpdated) throw new CrawlException("cannot select the store!")
    driver.navigate().refresh()
    
}

waitForMainContent()
if(!isStoreSelected()){
    selectStore(storeNo)
}
waitForProductImage()
openAccordionTabs()
getBrand()
a.step = "scrolling page"
Scroll.scroll(driver, 50)
closePopups()
a.log("done")