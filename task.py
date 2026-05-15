import tool

class Task():

    def __init__(self, taskName, taskId, courseNum, remain, complete, score):
        self.taskName= taskName
        self.taskId = taskId
        # 单元数量
        self.courseNum = courseNum
        # 剩余天数
        self.remain = remain
        self.complete = complete
        self.score = score

        # 课程列表
        self.courseList = []

        tool.task_dir_Audio(taskName)

    def __repr__(self):
        return f'''
        taskName: {self.taskName}
        taskId: {self.taskId}
        courseNum: {self.courseNum}
        remain: {self.remain}
        complete: {self.complete}
        score: {self.score}
        '''