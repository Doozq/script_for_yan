import time
import random
import threading
import logging
import os.path

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, timedelta

import logger_setup
import dolphin
from config import token, temp_urls, t_size, download_path
from coordinate import colibrate_systems
from paint import start_paint
from claim import claim, get_balance
from upgrade import check_upgrade
from templates import tournament_templates


MAX_THREADS = 4
semaphore = threading.Semaphore(MAX_THREADS)


def click_close_btn(driver):
    try:
        close_btn = driver.find_element(By.XPATH, "//div[contains(@class, 'close_container')]/div")
        time.sleep(2)
        close_btn.click()
        print("Нажата кнопка закртыия")
        time.sleep(1)
    except Exception as e:
        print(e)

def pick_tempalte(driver, profile_id, profiles):
    try:
        select_btn = driver.find_element(By.XPATH, "//span[text() = 'Starts ']")
        time.sleep(1)
        select_btn.click()
        time.sleep(7)
        temp = driver.find_elements(By.XPATH, "//div[contains(@class, 'template_item')]")[random.randint(3, 8)]
        temp.click()
        time.sleep(4)
        input_btn = driver.find_element(By.XPATH, "//button[text() = 'Select Template']")
        input_btn.click()
        time.sleep(5)
        close_btn = driver.find_element(By.XPATH, "//div[@class='_close_button_17ca7_20']")
        close_btn.click()
        time.sleep(2)
        img = driver.find_element(By.XPATH, "//div[contains(@class, 'template_item')]//img")
        url = img.get_attribute("src")
        path = url.split("app/")[1].split("?")[0].replace("/", "\\")
        profiles[profile_id]["temp"] = path
        time.sleep(4)

    except Exception:
        raise

def get_tempalte_info(driver, profile_id, profiles):
    try:
        img = driver.find_element(By.XPATH, "//img[contains(@src, 'tournament')]")
        url = img.get_attribute("src")
        path = url.split("tournament/")[1].split("?")[0]
        # img.click()
        # time.sleep(2)

        # canvas = driver.find_element(By.XPATH, "//canvas[@id='canvasHolder']")
        # time.sleep(1)
        # canvas.click()
        # time.sleep(2)
        # element = driver.find_element(
        #     By.XPATH, "//div[contains(@class, 'pixel_info_text')]"
        # )
        # text = element.get_attribute("innerHTML")
        # coords = text[:text.find("&")]
        # x_pixel, y_pixel = map(int, coords.split(", "))

        # select_btn = driver.find_element(By.XPATH, "//span[text() = 'Round 2']")
        # time.sleep(1)
        # select_btn.click()
        # time.sleep(5)
        # results = driver.find_element(By.XPATH, "//div[text() = 'My results']")
        # results.click()
        # time.sleep(4)
        # t_btn = driver.find_element(By.XPATH, "//div[contains(@class, 'round_main_info')]")
        # t_btn.click()
        # time.sleep(2)
        # coords = driver.find_elements(By.XPATH, "//div [@class = '_info_row_17ca7_66']/span")[1].text.split(", ")
        # size = (64, 64)
        # start = (int(coords[0]), int(coords[1]))
        # time.sleep(2)
        # if profiles[profile_id]["temp"] != path:
        #     profiles[profile_id]["temp"] = path
        #     driver.get(url)

        profiles[profile_id]["temp"] = path
        switched = False
        if not os.path.exists(download_path + path):
            driver.get(url)
            switched = True
        tournament_templates[path] = {}
        tournament_templates[path]["size"] = (t_size, t_size)
        time.sleep(2)
        return switched

    except Exception as e:
        logging.error(f"Errorin get_template_info: {e}")
        raise


def work_profile(profile_id, profiles):
    with semaphore:
        try:
            profile_name = profiles[profile_id]["name"]
            # Авторизация и создание драйвера
            dolphin.auth(token=token)
            driver = dolphin.get_driver(profile_id=profile_id)
            driver.implicitly_wait(50)

            logging.info(f"Profile {profile_name}. Driver for initialized and authenticated.")

            # Открытие Telegram и переход в нужный чат
            driver.get("https://web.telegram.org")
            logging.info(f"Profile {profile_name}. Opened Telegram Web.")

            chat = driver.find_element(By.XPATH, "//a[@href='#7249432100']")
            chat.click()
            logging.info(f"Profile {profile_name}. Navigated to the chat.")

            # Начало взаимодействия с ботом
            start = driver.find_element(By.XPATH, "//*[text() = 'start']")
            start.click()
            logging.info(f"Profile {profile_name}. Started interaction with the bot.")

            # Переход в iframe с канвасом
            iframe = driver.find_element(By.XPATH, "//iframe")
            driver.switch_to.frame(iframe)
            logging.info(f"Profile {profile_name}. Switched to canvas iframe.")

            time.sleep(random.uniform(5.0, 7.0))

            now = datetime.now()
            if now - profiles[profile_id]["last_claim"] >= timedelta(
                hours=random.uniform(5, 8)
            ):
                claim(driver, profile_id, profiles)
            
            if profiles[profile_id].get("skip", False):
                return
            
            if "temp" not in profiles[profile_id]:
                switched = get_tempalte_info(driver, profile_id, profiles)
                if switched:
                    driver.switch_to.frame(iframe)
            

            # Открытие шаблона
            template = driver.find_element(
                By.XPATH, "//div[contains(@class, 'container')]/button/img"
            )

            time.sleep(3)
            template.click()
            time.sleep(2)
            template.click()
            time.sleep(random.uniform(1.0, 2.0))
            logging.info(f"Profile {profile_name}. Template selected.")


            # zoom = driver.find_element(
            #     By.XPATH, "//div[contains(@class, 'buttons')]/button[contains(@class, 'button')]/span[contains(@class, 'icons')]"
            # )
            # zoom.click()
            # time.sleep(2)
            # zoom.click()
            # time.sleep(2)

            # Поиск элемента канваса
            canvas = driver.find_element(By.XPATH, "//canvas[@id='canvasHolder']")


            if profiles[profile_id]["temp"] not in tournament_templates or "start" not in tournament_templates[profiles[profile_id]["temp"]]:
                canvas.click()
                time.sleep(2)
                tournament_templates[profiles[profile_id]["temp"]] = {}
                element = driver.find_element(
                    By.XPATH, "//div[contains(@class, 'pixel_info_text')]"
                )
                text = element.get_attribute("innerHTML")
                coords = text[: text.find("&")]
                x_pixel, y_pixel = map(int, coords.split(", "))
                start_x = x_pixel - x_pixel % t_size
                start_y = y_pixel - y_pixel % t_size
                tournament_templates[profiles[profile_id]["temp"]]["start"] = (start_x, start_y)


            # Калибровка системы координат
            (
                x_canvas_zero,
                y_canvas_zero,
                x_pixel_zero,
                y_pixel_zero,
                x_pixel_end,
                y_pixel_end,
                ratio_x,
                ratio_y,
            ) = colibrate_systems(driver, canvas)
            logging.info(f"Profile {profile_name}. System calibrated.")

            check_for_load = driver.find_element(By.XPATH, "//body/div[contains(@class, 'layout')]")
            style_load = check_for_load.get_attribute('style')
            if 'width: 0px' not in style_load:
                logging.error(f"Profile {profile_name}. Ошибка загрузки")
                return

            # Запуск покраски
            start_paint(
                x_canvas_zero,
                y_canvas_zero,
                x_pixel_zero,
                y_pixel_zero,
                x_pixel_end,
                y_pixel_end,
                ratio_x,
                ratio_y,
                driver,
                canvas,
                profile_id,
                profiles,
            )
            # end_time = datetime.now()
            # if end_time - start_time >= timedelta(minutes=25):
            #     profiles[profile_id]["skip"] = True
            # if profiles[profile_id]["is_max"] == False:
            #     check_upgrade(driver, profile_id, profiles)

            # current_hour = datetime.now().hour
            # if current_hour > 8:
            time.sleep(random.randint(7, 15))
            round_btn = driver.find_element(By.XPATH, "//span[text()='Starts ' or text()='Round ']")
            round_btn.click()
            time.sleep(random.uniform(3.0, 5.0))
            results_btn = driver.find_element(By.XPATH, "//div[text()='My results']")
            results_btn.click()
            time.sleep(random.uniform(4.0, 5.0))
            template_place = driver.find_elements(By.XPATH, "//div[contains(@class, 'round_line_')]/div")[1].text.split(" ")[1]
            my_place = driver.find_elements(By.XPATH, "//div[contains(@class, 'round_line_')]/div")[5].text
            pixels_to_win = driver.find_elements(By.XPATH, "//div[contains(@class, 'pixels_number')]//div")[1].text
            profiles[profile_id]["template_place"] = template_place
            profiles[profile_id]["my_place"] = my_place
            profiles[profile_id]["pixels_to_win"] = pixels_to_win
            # if int(template_place) >= 75 and profiles[profile_id]["balance"] > 100000:
            #     profiles[profile_id]["skip"] = True
            


            logging.info(f"Profile {profile_name}. Work with profile {profile_id} is completed.")

            return

        except Exception as e:
            logging.error(f"Profile {profile_name}. An error occurred in work: {e}")
            raise

        finally:
            # Закрытие драйвера при завершении работы
            try:
                driver.quit()
                logging.info(f"Profile {profile_name}. Driver closed successfully.")
                dolphin.close_profile(profile_id)
                return

            except Exception as e:
                logging.error(f"Profile {profile_name}. Error closing the driver: {e}")
                raise
