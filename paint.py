import logging
import time
import random

from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import logger_setup

from coordinate import convert_coords_from_pixel_to_canvas
from colors import color_from_template, color_from_screen
from claim import get_balance
from templates import templates, tournament_templates
from config import real_colors, pupmkin_colors, t_size

from test import get_top_colors

def get_energy(driver):
    energy_element = driver.find_element(
        By.XPATH, "//div[contains(@class, 'placeholder')]"
    )
    energy = int(
        energy_element.get_attribute("innerHTML")
        .split("<span")[2][1:]
        .replace("</span>", "")
    )
    return energy


def get_template(driver):
    try:
        template_element = driver.find_element(
            By.XPATH, "//img[contains(@src, 'template')]"
        )
        template_key = (
            template_element.get_attribute("src").split("templates/")[1].split(".png")[0]
        )
        template = templates[template_key]
        return template
    except Exception as e:
        logging.error(f"Error in get_template: {e}")
        raise

def change_color(color, canvas, driver):
    try:
        active_color_element = driver.find_element(
            By.XPATH, "//div[contains(@class, 'active_color')]"
        )
        active_color = tuple(
            map(
                int,
                active_color_element.get_attribute("style")
                .replace("background-color: rgb(", "")[:-2]
                .split(", "),
            )
        )

        if active_color == color:
            return True
        else:
            active_color_element.click()
            opacity = "0"
            while opacity != "1":
                panel = driver.find_element(
                    By.XPATH, "//div[contains(@class, 'expandable_panel_layout')]"
                )
                opacity = panel.get_attribute("style").split(" ")[-1][:-1]
            need_color = driver.find_element(
                By.XPATH, f"//div[contains(@style, '{color}')]"
            )
            need_color.click()
            time.sleep(1)
            active_color_element.click()
            time.sleep(2)

        # Проверка
        active_color_element = driver.find_element(
            By.XPATH, "//div[contains(@class, 'active_color')]"
        )
        active_color = tuple(
            map(
                int,
                active_color_element.get_attribute("style")
                .replace("background-color: rgb(", "")[:-2]
                .split(", "),
            )
        )

        if active_color == color:
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Error in change_color: {e}")
        raise

def check_tanos(driver):
    try:
        driver.implicitly_wait(0)
        whoosh_btn = driver.find_element(By.XPATH, "//button[text()='Whoosh!']")
        driver.implicitly_wait(15)
        time.sleep(1.5)
        whoosh_btn.click()
        time.sleep(random.uniform(7.0, 10.0))

        template_btn = driver.find_element(
            By.XPATH, "//div[contains(@class, 'container')]/button/img"
        )
        time.sleep(0.5)
        template_btn.click()
        time.sleep(2)
        template_btn.click()
        time.sleep(1)

        logging.info("TANOS was dodged")
    
    except NoSuchElementException:
        driver.implicitly_wait(15)
        return

    except Exception as e:
        driver.implicitly_wait(15)
        logging.error(f"Error in check_tanos: {e}")
        raise


# def start_paint(
#     x_canvas_zero,
#     y_canvas_zero,
#     x_pixel_zero,
#     y_pixel_zero,
#     x_pixel_end,
#     y_pixel_end,
#     ratio_x,
#     ratio_y,
#     driver,
#     canvas,
#     profile_id,
#     profiles,
# ):
#     profile_name = profiles[profile_id]["name"]
#     try:
#         start_balance = get_balance(driver)
#         # template = get_template(driver)
#         template_path = profiles[profile_id]["temp"]
#         template = tournament_templates[template_path]
#         energy = get_energy(driver)
#         colored = 0
#         temp_start = template["start"]
#         pixel_coords = [[(x, y) for x in range(temp_start[0], temp_start[0] + t_size)] for y in range(temp_start[1], temp_start[1] + t_size)]
#         template_colors, opacity = color_from_template(template_path)
#         canvas_coords = [
#             [
#                 convert_coords_from_pixel_to_canvas(
#                     j[0],
#                     j[1],
#                     x_canvas_zero,
#                     y_canvas_zero,
#                     x_pixel_zero,
#                     y_pixel_zero,
#                     ratio_x,
#                     ratio_y,
#                 ) for j in i
#             ] for i in pixel_coords
#         ]
        
        
#         if "top_colors" not in template:
#             get_top_colors(template_path)

#         top_color = random.choice(template["top_colors"])
#         if not change_color(top_color, canvas, driver):
#             return
#         time.sleep(1)

#         while energy != 0:
#             screen_colors = color_from_screen(canvas_coords, canvas)
#             if opacity == 0:
#                 indexes = [(i, j, template_colors[i][j]) for i in range(t_size) for j in range(t_size) if template_colors[i][j] != screen_colors[i][j] and template_colors[i][j] == top_color and screen_colors[i][j] in (real_colors + pupmkin_colors)]
#             else:
#                 indexes = [(i, j, template_colors[i][j]) for i in range(t_size) for j in range(t_size) if template_colors[i][j] != screen_colors[i][j] and template_colors[i][j] == top_color and screen_colors[i][j] in (real_colors + pupmkin_colors) and opacity[i][j] == 255]
#             if len(indexes) == 0:
#                 check_tanos(driver)
#                 continue
#             i, j, template_color = random.choice(indexes)
#             canvas_x, canvas_y = canvas_coords[i][j][0], canvas_coords[i][j][1]
            
#             miss = not bool(random.randint(0, 200))
#             if miss:
#                 real_colors_except_template = [i for i in real_colors if i != template_color]
#                 repaint_color = random.choice(real_colors_except_template)

#                 if not change_color(repaint_color, canvas, driver):
#                     return
#                 paint(canvas_x, canvas_y, driver, canvas)
#                 if not change_color(top_color, canvas, driver):
#                     return
#                 logging.info(f"Profile {profile_name}. Miss dropped")
            
#             else:
#                 paint(canvas_x, canvas_y, driver, canvas)
                
#             colored += 1
#             time.sleep(random.uniform(0.5, 4))
#             energy = get_energy(driver)
#         time.sleep(2)
#         end_balance = get_balance(driver)
#         profit = end_balance - start_balance

#         profiles[profile_id]["balance"] = end_balance
#         profiles[profile_id]["last_paint"] = datetime.now()
#         profiles[profile_id]["last_profit"] = profit

#         logging.info(
#             f"Profile {profile_name}. Painting completed. Pixels colored: {colored}, Profit: {profit}, Balance: {end_balance}"
#         )
            
#         return

#     except Exception as e:
#         logging.error(f"Profile {profile_name}. Error in start_paint: {e}")
#         raise

def enable_speed(driver):
        try:
            speed = driver.find_elements(
                By.XPATH, "//button[contains(@class, 'shop_button')]"
            )[3]
            driver.driver.implicitly_wait(2)
            close = driver.find_element(By.XPATH, "//div[contains(@class, 'header')]/div[contains(@class, 'close')]")
            close.click()
            driver.driver.implicitly_wait(10)
        except NoSuchElementException:
            driver.driver.implicitly_wait(10)
        except Exception:
            raise

    


def enable_fast_mode(driver):
    try:
        fast_btn = driver.find_elements(
            By.XPATH, "//button[contains(@class, 'shop_button')]"
        )[4]
        fast_btn.click()
        time.sleep(2)
        check_fast_btn = driver.find_element(
            By.XPATH, "//button[contains(@class, 'fast_mode_button_enabled')]"
        )
        return True
    except NoSuchElementException:
        return False
    except Exception:
        raise


def start_paint(
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
):
    profile_name = profiles[profile_id]["name"]
    try:
        start_balance = get_balance(driver)
        # template = get_template(driver)
        template_path = profiles[profile_id]["temp"]
        template = tournament_templates[template_path]
        energy = get_energy(driver)
        colored = 0
        temp_start = template["start"]
        pixel_coords = [[(x, y) for x in range(x_pixel_zero, x_pixel_end + 1)] for y in range(y_pixel_zero, y_pixel_end + 1)]
        template_colors, opacity = color_from_template(template_path, pixel_coords)
        canvas_coords = [
            [
                convert_coords_from_pixel_to_canvas(
                    coord[0],
                    coord[1],
                    x_canvas_zero,
                    y_canvas_zero,
                    x_pixel_zero,
                    y_pixel_zero,
                    ratio_x,
                    ratio_y,
                ) for coord in row
            ] for row in pixel_coords
        ]
        
        range_x = x_pixel_end - x_pixel_zero + 1
        range_y = y_pixel_end - y_pixel_zero + 1
        
        top_colors = get_top_colors(template_path, template_colors, opacity)
        top_color = random.choice(top_colors)
        if not change_color(top_color, canvas, driver):
            return
        time.sleep(1)
        # paint_btn = driver.find_element(By.XPATH, "//span[text()='Paint']")
        if not enable_fast_mode(driver):
            return
        # enable_speed(driver)

        while energy != 0:
            screen_colors = color_from_screen(canvas_coords, canvas)
            if opacity == 0:
                indexes = [(i, j) for i in range(range_y) for j in range(range_x) if template_colors[i][j] != screen_colors[i][j] and template_colors[i][j] == top_color and screen_colors[i][j] in (real_colors + pupmkin_colors)]
            else:
                indexes = [(i, j) for i in range(range_y) for j in range(range_x) if template_colors[i][j] != screen_colors[i][j] and template_colors[i][j] == top_color and screen_colors[i][j] in (real_colors + pupmkin_colors) and opacity[i][j] == 255]
            if len(indexes) == 0:
                check_tanos(driver)
                continue
            i, j = random.choice(indexes)
            canvas_x, canvas_y = canvas_coords[i][j][0], canvas_coords[i][j][1]
            
            miss = not bool(random.randint(0, 200))
            if miss:
                if len(top_colors) > 1:
                    repaint_color = [i for i in top_colors if i != top_color][0]
                else:
                    real_colors_except_template = [i for i in real_colors if i != top_color]
                    repaint_color = random.choice(real_colors_except_template)

                if not change_color(repaint_color, canvas, driver):
                    return
                paint(canvas_x, canvas_y, driver, canvas)
                if not change_color(top_color, canvas, driver):
                    return
                logging.info(f"Profile {profile_name}. Miss dropped")
            
            else:
                paint(canvas_x, canvas_y, driver, canvas)

            colored += 1
            time.sleep(random.uniform(0.5, 4))
            energy = get_energy(driver)
        time.sleep(2)
        end_balance = get_balance(driver)
        profit = end_balance - start_balance

        profiles[profile_id]["balance"] = end_balance
        profiles[profile_id]["last_paint"] = datetime.now()
        profiles[profile_id]["last_profit"] = profit

        logging.info(
            f"Profile {profile_name}. Painting completed. Pixels colored: {colored}, Profit: {profit}, Balance: {end_balance}"
        )
            
        return

    except Exception as e:
        logging.error(f"Profile {profile_name}. Error in start_paint: {e}")
        raise



# def start_paint(
#     x_canvas_zero,
#     y_canvas_zero,
#     x_pixel_zero,
#     y_pixel_zero,
#     x_pixel_end,
#     y_pixel_end,
#     ratio_x,
#     ratio_y,
#     driver,
#     canvas,
#     profile_id,
#     profiles,
# ):
#     profile_name = profiles[profile_id]["name"]
#     try:
#         start_balance = get_balance(driver)
#         # template = get_template(driver)
#         template_path = profiles[profile_id]["temp"]
#         template = tournament_templates[template_path]
#         energy = get_energy(driver)
#         colored = 0
#         temp_start = template["start"]
#         temp_size = template["size"]
        
#         while energy != 0:
#             x = random.randint(temp_start[0], temp_start[0] + 63)
#             y = random.randint(temp_start[1], temp_start[1] + 63)
#             template_color = color_from_template(x, y, template, template_path)
#             canvas_x, canvas_y = convert_coords_from_pixel_to_canvas(
#                 x,
#                 y,
#                 x_canvas_zero,
#                 y_canvas_zero,
#                 x_pixel_zero,
#                 y_pixel_zero,
#                 ratio_x,
#                 ratio_y,
#             )
#             screen_color = color_from_screen(canvas_x, canvas_y, canvas)

#             if template_color != screen_color and screen_color in (real_colors + pupmkin_colors):
                
#                 miss = not bool(random.randint(0, 200))
                
#                 if miss:
#                     if screen_color in pupmkin_colors:
#                         real_colors_except_template = [i for i in real_colors if i != template_color]
#                         repaint_color = random.choice(real_colors_except_template)
#                     else:
#                         repaint_color = screen_color
                    
#                     paint(canvas_x, canvas_y, repaint_color, driver, canvas)
#                     logging.info(f"Profile {profile_name}. Miss dropped")
                
#                 else:
#                     paint(canvas_x, canvas_y, template_color, driver, canvas)
                
#                 colored += 1
#                 time.sleep(random.uniform(1.3, 2))

#             energy = get_energy(driver)

#         end_balance = get_balance(driver)
#         profit = end_balance - start_balance

#         profiles[profile_id]["balance"] = end_balance
#         profiles[profile_id]["last_paint"] = datetime.now()

#         logging.info(
#             f"Profile {profile_name}. Painting completed. Pixels colored: {colored}, Profit: {profit}, Balance: {end_balance}"
#         )

#     except Exception as e:
#         logging.error(f"Profile {profile_name}. Error in start_paint: {e}")
#         raise


def paint(x, y, driver, canvas):
    try:
        action = ActionChains(driver)
        action.move_to_element_with_offset(canvas, x, y).click().perform()
        check_tanos(driver)

        # paint_btn.click()

    except Exception as e:
        logging.error(f"Error in paint: {e}")
        raise
