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
GrabberDelegate grabber = getProperty(Browser.SCRIPT_PARAM_GRABBER) as GrabberDelegate

final String imageSelector = gatherURL.resourceSelectors.findAll { it.name == "productImage" }.collect { it.query }.join(",")
By byImageSelector = By.cssSelector(imageSelector)

Wait<WebDriver> wait = new FluentWait<>(driver)
        .pollingEvery(500, TimeUnit.MILLISECONDS)
        .withTimeout(15, TimeUnit.SECONDS)
        .ignoring(NoSuchElementException.class)

Wait<WebDriver> shortWait = new FluentWait<>(driver)
        .pollingEvery(100, TimeUnit.MILLISECONDS)
        .withTimeout(1, TimeUnit.SECONDS)
        .ignoring(NoSuchElementException.class)

a.step = "init"

final def storeNo = gatherURL.metadata['storeNo'] ?: 'HC06'

def isSearchPage = gatherURL.metadata['pageType'].equals 'search'
def isStorePage = gatherURL.metadata['pageType'].equals 'store'

def waitForProductImages = {
    a.step = "Wait for product Images to load"
    wait.until(visibilityOfAllElementsLocatedBy(byImageSelector))
}
def waitForMainContent = {
    a.step = "Wait for main Layout to load"
    By mainContent = By.cssSelector("main[data-currency-iso-code='ZAR']")
    wait.until(visibilityOfElementLocated(mainContent))
}

def noResult = {
    a.step = "Checking for no results"
    try {
        By noResultsLocator = By.cssSelector("div h1 span")
        wait.until(visibilityOfElementLocated(noResultsLocator))
        Boolean isNoResult = driver.findElement(noResultsLocator).getText().contains('Sorry, no products were found')
        return isNoResult
    } catch (WebDriverException ignored){
        a.step = "result found"
        return false
    }
}

def closePopups = { css ->
    a.step = "Close Popups"
    try {
        a.step = "Trying to close popup"
        By popupButton = By.cssSelector(css)
        shortWait.until(visibilityOfElementLocated(popupButton)).click()
        shortWait.until(invisibilityOfElementLocated(popupButton))
        a.log("closed popups")
    } catch (WebDriverException ignored) {
        a.log("failed to close popups"+ ignored)
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
if(isSearchPage && noResult()) {
    a.log("NO_RESULTS - No results found")
} else {
    if(!isStoreSelected() && isStorePage){
        selectStore(storeNo)
    }
    Scroll.scroll(driver,50)
    waitForProductImages()
}
closePopups(".close-button")
closePopups(".wp-optin-dialog-container .wp-optin-dialog-negativeButton")
a.log("done")