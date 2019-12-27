import errno
import os
import shutil
import time

import numpy as np
import random
import deterministic_solvers.PyMiniSolvers.minisolvers as minisolvers


class DimacsGenerator:

    def __init__(self, out_dir, percentage_sat=0.50, seed=None, min_n_vars=1, max_n_vars=5, min_n_clause=2,
                 max_n_clause=5, lit_distr_p=0.4):
        self.seed = seed if seed is not None else time.time_ns() % 100000
        random.seed(self.seed)
        np.random.seed(self.seed)
        self.percentage_sat = percentage_sat
        self.out_dir = out_dir
        self.min_n_vars = min_n_vars
        self.max_n_vars = max_n_vars
        self.min_n_clause = min_n_clause
        self.max_n_clause = max_n_clause
        self.lit_distr_p = lit_distr_p

    def generate(self, number_dimacs):
        number_sat_required = number_dimacs * self.percentage_sat
        number_unsat_required = number_dimacs - number_sat_required

        i = 0
        while i < number_dimacs:
            print("Generation of SATs problem at: " + str(int(i / number_dimacs * 100)) + "% (" + str(number_sat_required)
                  + " SAT left and " + str(number_unsat_required) + " UNSAT left)")
            n_vars, n_clause, clauses, is_sat = self.__gen_clause()

            if((is_sat and number_sat_required == 0) or (not is_sat and number_unsat_required == 0)):
                continue
            if is_sat:
                number_sat_required -= 1
            else:
                number_unsat_required -= 1
            i += 1

            out_filename = self.__make_filename(self.out_dir, n_vars, n_clause, is_sat, i)
            self.__save_sat_problem_to(out_filename, n_vars, clauses)

    def delete_all(self):
        try:
            shutil.rmtree(self.out_dir)
        except FileNotFoundError as e:
            pass

    def __gen_clause(self):
        n_vars = random.randint(self.min_n_vars, self.max_n_vars)
        n_clause = random.randint(self.min_n_clause, self.max_n_clause)
        solver = minisolvers.MinisatSolver()
        for i in range(n_vars):
            solver.new_var(dvar=True)

        clauses = []
        for i in range(n_clause):
            lit_from_geom = np.random.geometric(self.lit_distr_p) + 1
            max_n_lit = max(n_vars, 1)
            current_clause_n_lit = min(lit_from_geom, max_n_lit)
            current_clause = self.__generate_clause(n_vars, current_clause_n_lit)
            clauses.append(current_clause)
            solver.add_clause(current_clause)
        is_sat = solver.solve()

        return n_vars, n_clause, clauses, is_sat

    def __generate_clause(self, n_lits, n_lit_drawn):
        lits = [i + 1 for i in range(n_lits)]
        lits_drawn = np.random.choice(lits, size=int(n_lit_drawn), replace=False)

        return [lit if random.random() < 0.5 else -lit for lit in lits_drawn]

    def __make_filename(self, out_dir, n_vars, n_clause, is_sat, iter_num):
        return "%s/sat=%i_n_vars=%.3d_n_clause=%.3d_lit_distr_p=%.2f_seed=%d-%i.sat" % \
               (out_dir, is_sat, n_vars, n_clause, self.lit_distr_p, self.seed, iter_num)

    def __save_sat_problem_to(self, out_filename, n_vars, clauses):
        if not os.path.exists(os.path.dirname(out_filename)):
            try:
                os.makedirs(os.path.dirname(out_filename))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(out_filename, 'w') as file:
            file.write("p cnf %d %d\n" % (n_vars, len(clauses)))

            for clause in clauses:
                for lit in clause:
                    file.write("%d " % lit)
                file.write("\n")

            file.close()