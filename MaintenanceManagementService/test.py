# import sys
# sys.path.append('C:/Users/U/Documents/4.Semester/Masterarbeit/concept_implementation')
from queue import Queue

advisory1 = {'advisory1": "change"}
advisory2 = {"advisory2": "replace"}

advisories = Queue()

advisories.put(advisory1)

advisories.put(advisory2)

result = [{}, {"advisory2": "replace"}]