import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tool
from task import Task
from course import Course
from level import Level

# ==== 通用按钮检测/点击 ====
SELECTOR_START = ".taste-button.ready-button:not(.end):not(.ing)"
SELECTOR_ING = ".taste-button.ing"
SELECTOR_LOADING = ".el-loading-mask"

def get_userId(driver):
    if get_userId._cached is not None:
        return get_userId._cached
    get_userId._cached = driver.execute_script("""
        var ui = {};
        try {
            if (window.uni && typeof uni.getStorageSync === 'function')
                ui = uni.getStorageSync('userInfo');
            else
                ui = JSON.parse(localStorage.getItem('userInfo') || 'null') || {};
        } catch(e) {
            ui = JSON.parse(localStorage.getItem('userInfo') || 'null') || {};
        }
        return ui.memberId || ui.userId || '';
    """)
    return get_userId._cached

get_userId._cached = None

def click_btn(driver,selector):
    '''CDP真实鼠标点击(兼容iframe)'''
    info = driver.execute_script("""
        var el = document.querySelector(arguments[0]);
        if (!el) return null;
        var r = el.getBoundingClientRect();
        // 检测是否在iframe内，需要加上iframe偏移
        var frameX = 0, frameY = 0;
        if (window !== window.top) {
            var frame = window.frameElement;
            if (frame) {
                var fr = frame.getBoundingClientRect();
                frameX = fr.left;
                frameY = fr.top;
            }
        }
        return {
            x: Math.round(frameX + r.left + r.width/2),
            y: Math.round(frameY + r.top + r.height/2)
        };
    """, selector)
    if not info:
        print(f"  未找到元素: {selector}")
        return
    driver.execute_cdp_cmd("Input.dispatchMouseEvent",
        {"type": "mousePressed", "x": info['x'], "y": info['y'], "button": "left", "clickCount": 1})
    driver.execute_cdp_cmd("Input.dispatchMouseEvent",
        {"type": "mouseReleased", "x": info['x'], "y": info['y'], "button": "left", "clickCount": 1})


def save_page(driver, name):
    '''保存当前iframe页面HTML到 页面/ 目录'''
    os.makedirs("页面", exist_ok=True)
    path = f"页面/{name}.html"
    try:
        html = driver.execute_script("return document.documentElement.outerHTML")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  已保存页面: {path}")
    except Exception as e:
        print(f"  保存页面失败: {e}")
    return path

def click_btn_Challenge(driver):
    '''点击 挑战'''
    print("点击 挑战")
    click_btn(driver, "#tab-tab_active4")

def click_btn_StartChallenge(driver):
    '''点击 开始挑战'''
    print("点击 开始挑战")
    click_btn(driver, "div.startBtn button")

def click_btn_StartRecord(driver):
    '''点击 开始录音'''
    print("点击 开始录音")
    click_btn(driver, ".taste-button.ready-button:not(.ing):not(.end)")
    time.sleep(2)
    
def click_btn_StopRecord(driver):
    '''点击 结束录音'''
    print("点击 结束录音")
    click_btn(driver, ".taste-button.ing")
    time.sleep(2)

def click_btn_Skip(driver):
    '''点击 跳过'''
    print("点击 跳过")
    click_btn(driver, "img.btn-skip")
    time.sleep(2)

def get_currentItemIndex(driver,exclude_gray=False):
    '''获取当前 itemIdx'''
    '''t2/t10 False'''
    '''t4/t12 True'''
    sel = "#talkUl li:not([style*='display: none'])"
    if exclude_gray:
        sel += ":not(.grayAll)"
    try:
        el = driver.find_element(By.CSS_SELECTOR, sel)
        lid = el.get_attribute("id")
        return int(lid.split("_")[-1])
    except:
        return None

def _has_StartRecord(driver):
    '''是否有 开始录音'''
    return driver.execute_script("""
        var el = document.querySelector('.taste-button.ready-button:not(.end):not(.ing)');
        return !!(el && el.offsetHeight > 0);
    """)

def _has_StopRecord(driver):
    '''是否有 结束录音'''
    return driver.execute_script("""
        var el = document.querySelector('.taste-button.ing');
        return !!(el && el.offsetHeight > 0);
    """)

def _has_Skip(driver):
    '''是否有 跳过'''
    return driver.execute_script("""
        var el = document.querySelector('img.btn-skip');
        return !!(el && el.offsetHeight > 0);
    """)

def _has_Loading(driver):
    return driver.execute_script("""
        var el = document.querySelector('.el-loading-mask');
        return !!(el && el.offsetHeight > 0);
    """)

def _record_item(wav_path):
    '''播放音频到虚拟声卡'''
    print(f"播放: {wav_path}")
    tool.play_wav(wav_path, blocking=True)

def _has_exchange(driver):
    '''是否有 交换角色'''
    return driver.execute_script("""
        var el = document.querySelector('div.exchange');
        return !!(el && el.offsetHeight > 0);
    """)

def to_level(driver, taskId,unitIt,levelId):
    '''跳转到对应的 Level 页面'''
    driver.get(
        "https://static.fifedu.com/static/fiforal/kyxl-web-static/student-h5/index.html"
        "#/pages/webView/testWebView/testWebView"
        f"?userId={get_userId(driver)}"
        f"&taskId={taskId}"
        f"&unitId={unitIt}"
        f"&gId={levelId}"
        f"&bankType=undefined"
        f"&_t={int(time.time() * 1000)}"
        )

def _element_exists(driver, selector):
    return driver.execute_script("""
        var el = document.querySelector(arguments[0]);
        return !!(el && el.offsetHeight > 0);
    """, selector)


def do_Normal(driver, task:Task, course:Course, level:Level):
    do_Generic(driver, task, course, level, False)

def do_Conversation(driver, task:Task, course:Course, level:Level):
    do_Generic(driver, task, course, level, True)

def do_Generic(driver, task:Task, course:Course, level:Level, exclude_gray):
    for retry in range(3):
        if retry == 0:
            to_level(driver, task.taskId, course.unitid, level.levelId)
        elif retry == 1:
            print(f"  刷新页面重试...")
            driver.switch_to.default_content()
            driver.refresh()
            time.sleep(3)
        else:
            print(f"  新开标签页重试...")
            driver.switch_to.default_content()
            driver.execute_script("window.open('about:blank','_blank')")
            handles = driver.window_handles
            driver.close()
            driver.switch_to.window(handles[-1])
            to_level(driver, task.taskId, course.unitid, level.levelId)
        
        wait = WebDriverWait(driver, 15)
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)
        time.sleep(3)

        click_btn_Challenge(driver)
        time.sleep(3)

        if _element_exists(driver, "div.startBtn button"):
            click_btn_StartChallenge(driver)
            time.sleep(5)
            break
        else:
            print(f"  未找到开始挑战按钮，重试 ({retry+1}/3)")
            driver.switch_to.default_content()
            continue
    else:
        print(f"  重试3次仍无法进入挑战，跳过")
        return

    while True:                          # 外层：多轮
        done = set()
        total = len(level.itemList)
        stuck = 0

        while len(done) < total:         # 内层：逐句
            idx = get_currentItemIndex(driver, exclude_gray)
            if idx is None or idx >= total:
                stuck += 1
                if stuck % 5 == 0:
                    print(f"  等待句子加载... ({stuck}s)")
                time.sleep(1); 
                if stuck >= 30:
                    print(f"  等待句子加载超时，跳过")
                    break
                continue
            if idx in done:
                stuck += 1
                if stuck % 5 == 0:
                    print(f"  等待句子{idx}跳转... ({stuck}s)")
                time.sleep(1); continue
            stuck = 0

            if _has_Skip(driver):
                click_btn_Skip(driver)
                print(f"跳过第 {idx} 句")
                done.add(idx)
                continue

            item = level.itemList[idx]
            cur_wav = f"audio/{task.taskName}/{course.unitName}/{level.levelName}/{idx}.wav"
            print(f"当前第{idx}句: {item.get('text','')[:30]}")
            _record_item(cur_wav)
            click_btn_StopRecord(driver)

            for _ in range(10):
                if not _has_StopRecord(driver):
                    break
                time.sleep(1)

            done.add(idx)

            for _ in range(10):
                new_idx = get_currentItemIndex(driver, exclude_gray)
                if new_idx is not None and new_idx != idx: break
                if _has_StopRecord(driver) or _has_StartRecord(driver): break
                time.sleep(1)

        time.sleep(5)
        if not _has_Skip(driver) and not _has_StartRecord(driver) and not _has_StopRecord(driver):
            print("  无任何录音/跳过按钮，Level 结束")
            break
        else:
            print("  检测到未完成的句子，继续下一轮")
            continue