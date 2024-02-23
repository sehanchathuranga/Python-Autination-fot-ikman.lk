from selenium import webdriver
from selenium.webdriver.common.by import By  # Import By module for locating elements
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

# URL of the website
url = "https://ikman.lk/en/ads/sri-lanka/vehicles?sort=relevance&buy_now=0&urgent=0&query=ct100&page=1"


def scrape_data(url, max_items=50):
    driver = webdriver.Chrome()
    driver.get(url)

    # Frist page

    all_data = []
    current_page = 1

    r = requests.get(driver.current_url)
    c = r.content
    soup = BeautifulSoup(c, "html.parser")

    item_list_names = [item.text.strip() for item in soup.find_all("h2", {"class": "heading--2eONR heading-2--1OnX8 title--3yncE block--3v-Ow"})]
    item_list_images = [item['src'] for item in soup.find_all("img", {"class": "normal-ad--1TyjD"})]
    item_list_price = [item.text.strip() for item in soup.find_all("div", {"class": "price--3SnqI color--t0tGX"})]
    item_list_description = [item.text.strip() for item in soup.find_all("div", {"class": "description--2-ez3"})]
    list_updated_time = [item.text.strip() for item in soup.find_all("div", {"class": "updated-time--1DbCk"})]
    list_links_to_items = [item['href'] for item in soup.find_all("a", {"class": "card-link--3ssYv gtm-ad-item"})]

    page_data = list(zip(item_list_names, item_list_images, item_list_price, item_list_description, list_updated_time, list_links_to_items))
    all_data.extend(page_data)

    while len(all_data) < 50:    #Secound page
        try:
            next_page_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a.wrapper--trS9a[aria-label="Next"]'))
            )
            current_page += 1
            next_page_button.click()

            r = requests.get(driver.current_url)
            c = r.content
            soup = BeautifulSoup(c, "html.parser")

            item_list_names = [item.text.strip() for item in soup.find_all("h2", {"class": "heading--2eONR heading-2--1OnX8 title--3yncE block--3v-Ow"})]
            item_list_images = [item['src'] for item in soup.find_all("img", {"class": "normal-ad--1TyjD"})]
            item_list_price = [item.text.strip() for item in soup.find_all("div", {"class": "price--3SnqI color--t0tGX"})]
            item_list_description = [item.text.strip() for item in soup.find_all("div", {"class": "description--2-ez3"})]
            list_updated_time = [item.text.strip() for item in soup.find_all("div", {"class": "updated-time--1DbCk"})]
            list_links_to_items = [item['href'] for item in soup.find_all("a", {"class": "card-link--3ssYv gtm-ad-item"})]

            page_data = list(zip(item_list_names, item_list_images, item_list_price, item_list_description, list_updated_time, list_links_to_items))
            all_data.extend(page_data)

        except Exception as e:
            print("No more pages or element not found:", e)
            break

    driver.quit()

    return all_data[:max_items]


# save to csv
def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Image', 'Price', 'Description', 'Updated Time', 'Link'])
        writer.writerows(data)


def send_email(subject, body, to_email, attachment_filename):
    from_email = 'sehanchathuweerasinghe@gmail.com'               # your email
    password = 'jzww yppn jzft umzu'                              # your email password

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    with open(attachment_filename, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        part.add_header('Content-Disposition', f'attachment; filename= {attachment_filename}')
        msg.attach(part)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_bytes())


data = scrape_data(url)

csv_filename = "scraped_data.csv"    #rechange filename here
save_to_csv(data, csv_filename)

# Send email with the CSV
email_subject = "Auto-Generated Ikman.lk Vehicle Listings - Data Scraped"
email_body = "Dear [Recipient's Name],\n\n I hope this email finds you well. \n Attached, please find the auto-generated report containing the latest vehicle listings from Ikman.lk. The data was scraped from Ikman.lk and includes details such as vehicle names, images, prices, descriptions, updated times, and links.\n This report is provided for your reference and analysis. If you have any questions or require further information, feel free to reach out.\n\nBest regards,\n[Your Name]"
to_email = "sehanchathurangaascg@gmail.com"                # the recipient's email
send_email(email_subject, email_body, to_email, csv_filename)

