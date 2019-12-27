import os
import re

from sat_problem import SATProblem


class DimacLoader:

    def __init__(self, dir_path=None):
        self.dir_path = dir_path if dir_path else os.getcwd() + "/../out/"

    def load_sat_problems(self):
        print("Loading sat problems...")
        SAT_problems = []
        for (dirpath, dirnames, filenames) in os.walk(self.dir_path):

            for filename in filenames:
                file_path = os.path.join(self.dir_path, filename)
                SAT_problems.append(self.__load_dimac(file_path))

        print("Finished loading sat problems...")
        return SAT_problems

    def __load_dimac(self, file_path):
        with open(file_path) as f:
            content = f.readlines()
            clauses = [list(map(int, clause.split())) for clause in content[1:]]

        return SATProblem(clauses, self.__is_sat(file_path))

    def __is_sat(self, file_path):
        m = re.search("sat=(\\d+)_", file_path)
        is_sat = m.group(1)
        return int(is_sat) == 1

