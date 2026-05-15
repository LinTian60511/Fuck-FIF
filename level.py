import tool
import json


class Level:
    def __init__(self, levelName, levelScore, levelId, taskName, taskId, courseName, unitId, levelStatus, unlockScore, t):
        self.levelName = levelName
        self.levelScore = levelScore
        self.levelId = levelId
        self.taskName = taskName
        self.taskId = taskId
        self.courseName = courseName
        self.unitId = unitId
        self.levelStatus = levelStatus
        self.unlockScore = unlockScore
        self.t = t
        self.completed = (levelScore > 0) if unlockScore < 0 else (levelScore > unlockScore)
        self.itemList = []

        tool.level_dir_Audio(taskName, courseName, levelName)

    def refresh(self, driver):
        data = driver.execute_async_script("""
            const cb = arguments[arguments.length - 1];
            const done = setTimeout(() => cb('{}'), 15000);
            const auth = (window.uni && typeof uni.getStorageSync === 'function' && uni.getStorageSync('Authorization')) || localStorage.getItem('Authorization') || '';
            const src = (window.uni && typeof uni.getStorageSync === 'function' && uni.getStorageSync('source')) || localStorage.getItem('source') || '10003';
            const headers = { 'source': src };
            if (auth) headers['Authorization'] = 'Bearer ' + auth;
            fetch('https://moral.fifedu.com/kyxl-app/stu/column/stuUnitInfo?' + new URLSearchParams({ unitId: '""" + self.unitId + """', taskId: '""" + self.taskId + """', bankType: '' }).toString(), {
                credentials: 'include', headers
            }).then(r => r.json()).then(d => { clearTimeout(done); cb(JSON.stringify(d)); }).catch(e => { clearTimeout(done); cb('{}'); });
        """)
        try:
            data = json.loads(data)
        except:
            return False
        if not data or 'error' in data:
            return False
        for lv in data.get('data', {}).get('levelList', []):
            if lv.get('levelId') == self.levelId:
                self.levelScore = lv.get('levelScore', self.levelScore) or 0
                self.unlockScore = lv.get('unlockScore', self.unlockScore) or 0
                self.levelStatus = lv.get('levelStatus', self.levelStatus)
                if self.unlockScore < 0:
                    self.completed = self.levelScore > 0
                else:
                    self.completed = self.levelScore > self.unlockScore
                print(f"  [刷新] {self.levelName}: score={self.levelScore} unlock={self.unlockScore} completed={self.completed}")
                return self.completed
        return False
