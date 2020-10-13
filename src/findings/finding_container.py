import json 
from src.findings.utils import Finding
from src.findings.utils import FindingCategory

class FindingContainer:
    _finding_results = []

    @classmethod
    def addFinding (
        cls, 
        category: FindingCategory, 
        location: str,
        message: str,
        actionable: bool,
        extra_info = None):
        cls._finding_results.append(Finding(category, location, message, actionable, extra_info))

    @classmethod
    def getAllFindings (cls):
        return cls._finding_results
    
    @classmethod
    def toJson(cls):
        findingDictArr = []
        for finding in cls._finding_results:
            findingDictArr.append(finding.toDict())
        return json.dumps(findingDictArr)
    
    @classmethod
    def reset(cls):
        cls._finding_results = []
