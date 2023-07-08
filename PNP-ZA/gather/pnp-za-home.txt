import com.uk.ef.crawl.Action
import com.uk.ef.crawl.Browser
import com.uk.ef.model.GatherURL
import com.uk.ef.crawl.util.Scroll
import com.uk.ef.exceptions.CrawlException
import com.uk.ef.data.Code
import org.openqa.selenium.*
import org.openqa.selenium.By
import org.openqa.selenium.WebDriver
import org.openqa.selenium.WebDriverException
import org.openqa.selenium.interactions.Actions
import org.openqa.selenium.WebElement
import org.openqa.selenium.support.ui.FluentWait
import org.openqa.selenium.support.ui.Wait
import org.openqa.selenium.NoSuchElementException
import java.util.concurrent.TimeUnit
import java.util.concurrent.TimeoutException
import com.uk.ef.util.DriverUtils

import static org.openqa.selenium.support.ui.ExpectedConditions.*

WebDriver driver = getProperty(Browser.SCRIPT_PARAM_DRIVER) as WebDriver
Action a = getProperty(Browser.SCRIPT_PARAM_ACTION) as Action
GatherURL gurl = getProperty(Browser.SCRIPT_PARAM_GATHER_URL) as GatherURL
JavascriptExecutor js = driver as JavascriptExecutor

final String imageSelector = gurl.resourceSelectors.findAll { it.name == "bannerImage" }.collect { it.query }.join(",")
By byImageSelector = By.cssSelector(imageSelector)

Wait<WebDriver> wait = new FluentWait<>(driver)
        .pollingEvery(500, TimeUnit.MILLISECONDS)
        .withTimeout(15, TimeUnit.SECONDS)
        .ignoring(NoSuchElementException.class)

Wait<WebDriver> shortWait = new FluentWait<>(driver)
        .pollingEvery(200, TimeUnit.MILLISECONDS)
        .withTimeout(3, TimeUnit.SECONDS)
        .ignoring(NoSuchElementException.class)

a.step = "init"

def waitForHomepage = {
    a.step = "wait for homepage to load"
    try {
        By byHomepage = By.cssSelector("main[data-currency-iso-code='ZAR']")
        wait.until(visibilityOfElementLocated(byHomepage))
    } catch (WebDriverException ignored) {
        a.step = "Failed to wait for homepage to load"
    }
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

def waitForBanners = {
    a.step = "wait for banner to load"
    wait.until(presenceOfAllElementsLocatedBy(byImageSelector))
}

def rotateCarouselBanners = {
    a.step = 'capturing carousel banner'
    try {
        def dotButtons = wait.until(presenceOfAllElementsLocatedBy(By.cssSelector(".headercarousel .owl-dot")))
        a.step = "capturing ${dotButtons.size()} banners"
        sleep(1000)
        dotButtons.each { dotButton ->
            js.executeScript("arguments[0].click()", dotButton)
            sleep(1000)
            WebElement bannerCarousel = wait.until(visibilityOfElementLocated(By.cssSelector(".headercarousel .owl-item.active")))
            WebElement bannerImage = bannerCarousel.findElement(By.cssSelector("img"))
            String imageURI = DriverUtils.captureElement(driver, bannerCarousel)
            DriverUtils.embed(imageURI).attribute('x-data-src').on(bannerImage).execute(driver)
            
        }
    } catch (WebDriverException ignored) {
        a.log("No banner found $ignored")
    }
}



waitForHomepage()
rotateCarouselBanners()
a.step = "scrolling page"
Scroll.scroll(driver, 50)
waitForBanners()
closePopups()
a.step = "done"