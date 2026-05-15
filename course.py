import tool

class Course:

    def __init__(self, unitName, complete, unitid, showTypeList, taskName):
        self.unitName = unitName
        self.complete = complete
        self.unitid = unitid
        self.showTypeList = showTypeList
        self.taskName = taskName

        self.levelList = []

        tool.course_dir_Audio(taskName, unitName)
    
    def __repr__(self):
        return f'''
        unitName: {self.unitName}
        complete: {self.complete}
        unitid: {self.unitid}
        showTypeList: {self.showTypeList}
        taskName: {self.taskName}
        '''