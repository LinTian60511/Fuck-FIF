from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from selenium.webdriver.chrome.options import Options
import time
from task import Task
from course import Course
from level import Level
import challenge
import os

DRIVER_PATH = os.path.join(os.path.dirname(__file__), "chromedriver-win64", "chromedriver.exe")
FIF_URL = "https://oralenglish.fifedu.com/kyxl-web/teacher/index.do?sign=true&language=2&isLogin=1"
TEACHING_URL = "https://static.fifedu.com/static/fiforal/kyxl-web-static/student-h5/index.html#/pages/teaching/teaching"

options = Options()
options.add_argument("--disable-user-media-security")
options.add_argument("--disable-popup-blocking")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
service = Service(executable_path=DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

driver.execute_cdp_cmd("Browser.grantPermissions", {
    "origin": "https://static.fifedu.com",
    "permissions": ["audioCapture"],
})
task_list = []
userId = ""

def load():
    账号 = input("请输入账号:")
    密码 = input("请输入密码:")
    # 点击登录按钮
    driver.execute_script("document.querySelector('a.login')?.click()")
    time.sleep(1)
    # 输入账号和密码
    driver.find_element(By.XPATH, "//input[@placeholder='请输入学校简称+学工号']").send_keys(账号)
    driver.find_element(By.XPATH, "//input[@placeholder='请输入密码']").send_keys(密码)
    # 点击登录
    driver.find_element(By.XPATH, "//button[contains(@class,'cursor_p')]").click()

def enter_FIF():
    wait = WebDriverWait(driver, 10)
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='FiF口语训练系统']"))).click()
    except:
        print("账号或者密码输入错误,请检查账号密码是否正确")
    time.sleep(5)
    driver.switch_to.window(driver.window_handles[-1])

def enter_AItask():
    driver.get(TEACHING_URL)
    time.sleep(2)

def get_Task(driver):
    '''获取任务详情、课程、Level、题目'''
    get_TaskList(driver)
    if not task_list:
        print("没有任务")
        return

    for task in task_list:
        task:Task
        get_TaskCourseDetails(driver, task.taskId)
        for course in task.courseList:
            course:Course
            get_Level(driver, course.unitid, task.taskId)

    print("\n========== 汇总 ==========")
    for task in task_list:
        print(f"任务: {task.taskName} ({len(task.courseList)}个课程)")
        for course in task.courseList:
            print(f"  课程: {course.unitName} ({len(course.levelList)}个Level)")
            for level in course.levelList:
                print(f"    Level: {level.levelName} - {len(level.itemList)}个题目")
    print("==========================\n")

def get_TaskList(driver, timeout=3):
    global task_list, userId
    task_list.clear()

    data = driver.execute_async_script("""
        const cb = arguments[arguments.length - 1];
        const auth = (window.uni && typeof uni.getStorageSync === 'function' && uni.getStorageSync('Authorization')) || localStorage.getItem('Authorization') || '';
        const src = (window.uni && typeof uni.getStorageSync === 'function' && uni.getStorageSync('source')) || localStorage.getItem('source') || '10003';
        const ui = (window.uni && typeof uni.getStorageSync === 'function' && uni.getStorageSync('userInfo')) || JSON.parse(localStorage.getItem('userInfo') || 'null') || {};
        const uid = ui.memberId || ui.userId || '';
        const headers = { 'Content-Type': 'application/x-www-form-urlencoded', 'source': src };
        if (auth) headers['Authorization'] = 'Bearer ' + auth;
        fetch('https://moral.fifedu.com/kyxl-app/stu/task/teaTaskList', {
            method: 'POST', credentials: 'include', headers,
            body: new URLSearchParams({ userId: uid, status: '1', page: '1' }).toString()
        }).then(r => r.json()).then(cb).catch(e => cb({ error: e.toString() }));
    """)

    if not data:
        print("获取任务列表失败：无响应")
        return []

    if 'error' in data:
        print(f"请求错误：{data['error']}")
        return []

    ttiList = data.get('data', {}).get('ttiList', [])

    if not ttiList:
        print("没有任务或鉴权失败")
        return []

    if not userId:
        userId = driver.execute_script("""
            const ui = (window.uni && uni.getStorageSync('userInfo')) || {};
            return ui.memberId || ui.userId || '';
        """)

    print(f"共找到 {len(ttiList)} 个任务：\n")
    for i, task in enumerate(ttiList, 1):
        print(f"--- 任务 {i} ---")
        print(json.dumps(task, ensure_ascii=False, indent=2))
        print()

    for task in ttiList:
        temp = Task(
            taskName=task.get('taskName'),
            taskId=task.get('taskId'),
            courseNum=task.get('courseNum'),
            remain=task.get('remain'),
            complete=task.get('complete'),
            score=task.get('score')
            )
        task_list.append(temp)

def get_TaskCourseDetails(driver, taskId):
    ''' 获取任务的课程详情'''
    data = driver.execute_async_script("""
        const cb = arguments[arguments.length - 1];
        const auth = (window.uni && typeof uni.getStorageSync === 'function' && uni.getStorageSync('Authorization')) || localStorage.getItem('Authorization') || '';
        const src = (window.uni && typeof uni.getStorageSync === 'function' && uni.getStorageSync('source')) || localStorage.getItem('source') || '10003';
        const ui = (window.uni && typeof uni.getStorageSync === 'function' && uni.getStorageSync('userInfo')) || JSON.parse(localStorage.getItem('userInfo') || 'null') || {};
        const uid = ui.memberId || ui.userId || '';
        const headers = { 'Content-Type': 'application/x-www-form-urlencoded', 'source': src };
        if (auth) headers['Authorization'] = 'Bearer ' + auth;
        fetch('https://moral.fifedu.com/kyxl-app/task/stu/teaTaskDetail', {
            method: 'POST', credentials: 'include', headers,
            body: new URLSearchParams({ userId: uid, id: '""" + taskId + """' }).toString()
        }).then(r => r.json()).then(cb).catch(e => cb({ error: e.toString() }));
    """)

    if not data:
        print("获取课程详情失败：无响应")
        return []

    if 'error' in data:
        print(f"请求错误：{data['error']}")
        return []

    ttdList = data.get('data', {}).get('ttdList', [])

    if not ttdList:
        print("没有课程数据或鉴权失败")
        return []

    print(f"任务 {data['data'].get('taskName', taskId)} 共 {len(ttdList)} 个课程：\n")
    for i, course in enumerate(ttdList, 1):
        print(f"--- 课程 {i} ---")
        print(json.dumps(course, ensure_ascii=False, indent=2))
        print()
    
    for task in task_list:
        task:Task
        if task.taskId == taskId:
            for course in ttdList:
                temp = Course(
                    unitName=course.get('unitName'),
                    complete=course.get('complete'),
                    unitid=course.get('unitid'),
                    showTypeList=course.get('showTypeList'),
                    taskName=task.taskName
                    )
                task.courseList.append(temp)

def get_Level(driver, unitId, taskId):
    '''获取课程的Level详情（题型名称、分数等）'''
    data = driver.execute_async_script("""
        const cb = arguments[arguments.length - 1];
        const auth = (window.uni && uni.getStorageSync('Authorization')) || localStorage.getItem('Authorization') || '';
        const src = (window.uni && uni.getStorageSync('source')) || localStorage.getItem('source') || '10003';
        const headers = { 'source': src };
        if (auth) headers['Authorization'] = 'Bearer ' + auth;
        fetch('https://moral.fifedu.com/kyxl-app/stu/column/stuUnitInfo?' + new URLSearchParams({ unitId: '""" + unitId + """', taskId: '""" + taskId + """', bankType: '' }).toString(), {
            credentials: 'include', headers
        }).then(r => r.json()).then(cb).catch(e => cb({ error: e.toString() }));
    """)

    if not data:
        print("获取Level详情失败：无响应")
        return []

    if 'error' in data:
        print(f"请求错误：{data['error']}")
        return []

    levelList = data.get('data', {}).get('levelList', [])

    if not levelList:
        print("没有Level数据")
        return []

    print(f"课程 {unitId} 共 {len(levelList)} 个Level：\n")
    for i, level in enumerate(levelList, 1):
        print(f"--- Level {i} ---")
        print(f"  名称: {level.get('levelName')}")
        print(f"  分数: {level.get('levelScore')}")
        print()
    # 创建level对象
    for task in task_list:
        task:Task
        if task.taskId == taskId:
            for couse in task.courseList:
                couse:Course
                if couse.unitid == unitId:
                    stl = getattr(couse, 'showTypeList', [])
                    print(f"  showTypeList={stl}, levelList共{len(levelList)}个")
                    for idx, level in enumerate(levelList):
                        showType = couse.showTypeList[idx] if idx < len(couse.showTypeList) else ''
                        temp = Level(
                            levelName=level.get('levelName'),
                            levelScore=level.get('levelScore'),
                            levelId=level.get('levelId'),
                            taskName=task.taskName,
                            taskId=task.taskId,
                            courseName=couse.unitName,
                            unitId=couse.unitid,
                            levelStatus=level.get('levelStatus', 0),
                            unlockScore=level.get('unlockScore', 0),
                            t=showType
                            )
                        temp.itemList = get_LevelItem(level)
                        couse.levelList.append(temp)

def get_LevelItem(levelData):
    '''获取Level的题目及音频URL，按res_path去重，id从0开始'''
    items = []
    seen = set()
    levelPath = levelData.get('levelPath', '')
    baseUrl = levelPath.replace('.zip', '/') if levelPath else ''

    moshiList = levelData.get('levelContent', {}).get('moshi', [])

    for moshi in moshiList:
        qItems = moshi.get('question', {}).get('qcontent', {}).get('item', [])
        for qItem in qItems:
            questions = qItem.get('questions', [])
            for q in questions:
                resPath = q.get('res_path', '')
                if not resPath or resPath in seen:
                    continue
                seen.add(resPath)

                text = q.get('text') or q.get('title', '')
                audioUrl = baseUrl + resPath

                items.append({
                    'id': len(items),
                    'text': text,
                    'title_cn': q.get('title_cn', ''),
                    'res_path': resPath,
                    'audioUrl': audioUrl,
                    'recordingTime': q.get('recordingTime', '')
                })

    return items

def get_ItemAudio(taskName, courseName, levelName, itemList):
    '''把itemList里的音频逐个下载到 audio/{taskName}/{courseName}/{levelName}/{id}.mp3 并转wav'''
    import urllib.request
    import os
    import tool

    dirPath = os.path.join("audio", taskName, courseName, levelName)
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]

    for item in itemList:
        url = item.get('audioUrl', '')
        if not url:
            print(f"  跳过 item {item['id']}：无audioUrl")
            continue
        mp3_path = os.path.join(dirPath, f"{item['id']}.mp3")
        wav_path = os.path.join(dirPath, f"{item['id']}.wav")

        if os.path.exists(wav_path):
            continue

        if not os.path.exists(mp3_path):
            try:
                with opener.open(url, timeout=30) as resp, open(mp3_path, 'wb') as f:
                    f.write(resp.read())
                print(f"  已下载 item {item['id']}: {os.path.basename(url)}")
            except Exception as e:
                print(f"  下载失败 item {item['id']}: {e}")
                continue

        if not os.path.exists(wav_path):
            tool.mp3_to_wav(mp3_path, wav_path)
            os.remove(mp3_path)

def download_Audio():
    '''遍历task_list，下载所有Level下的item音频'''
    if not task_list:
        print("没有任务数据，请先运行 get_Task")
        return

    for task in task_list:
        for course in task.courseList:
            for level in course.levelList:
                if not level.itemList:
                    continue
                print(f"\n下载: {task.taskName}/{course.unitName}/{level.levelName}")
                get_ItemAudio(task.taskName, course.unitName, level.levelName, level.itemList)

def start_Challenge(driver):
    '''遍历所有level，循环重试直到完成或跳下一个'''

    for task in task_list:
        task:Task
        print(f"\n===== 任务: {task.taskName} =====")
        for course in task.courseList:
            course:Course
            print(f"  -- 课程: {course.unitName} --")
            for level in course.levelList:
                level:Level
                print(f"拉取 {level.levelId} 的最新数据...")
                if level.refresh(driver):
                    print(f"  Level: {level.levelName} 已完成,跳过")
                    continue

                print(f"  Level: {level.levelName} 开始挑战")
                retry = 0
                level_finished = False
                while retry < 3:
                    print(f"    第 {retry+1} 次挑战...")
                    if not level_finished:
                        match level.t:
                            case "t2" | "t10" | "t11":
                                challenge.do_Normal(driver, task, course, level)
                            case "t4" | "t12":
                                challenge.do_Conversation(driver, task, course, level)
                            case _:
                                print(f"    未知题型 {level.t}，跳过")
                                break
                        driver.switch_to.default_content()
                        level_finished = True

                    time.sleep(5)
                    print(f"拉取 {level.levelId} 的最新数据...")
                    if level.refresh(driver):
                        print(f"  Level: {level.levelName} 已完成，进入下一关")
                        break
                    else:
                        print(f"  Level: {level.levelName} 未通过，等待后重检...")
                        time.sleep(5)
                        retry += 1
                else:
                    print(f"  Level: {level.levelName} 重试 {retry} 次未通过，跳过")

def main():
    os.system('cls')

    driver.get("https://www.fifedu.com/iplat/html/home/home.html")
    time.sleep(1)

    # 登录
    load()

    # 进入FiF
    enter_FIF()

    # 进入 AI任务
    time.sleep(1)
    enter_AItask()
    
    # 获取任务详情
    get_Task(driver)

    # 下载音频
    download_Audio()

    # 开始挑战
    start_Challenge(driver)

if __name__ == "__main__":
    main()