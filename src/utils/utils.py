from datetime import timedelta

import numpy as np
from termcolor import colored

from .converter import liter_to_bbl


def format_solution_output(solver, truck_capacity, duration):
    # Imprime a resposta para o usuário
    print()
    if solver.optimal_solution.total_cost == np.inf:
        print(
            colored(
                "Não existe uma solução para o problema com as condições inseridas.",
                "red",
            )
        )
    else:
        unused_trucks = []
        for i, t in enumerate(solver.optimal_solution.trucks):
            if not t.route:
                unused_trucks.append(str(i + 1))
                continue
            print(colored(f"Caminhão {i + 1}", "green"))
            line = f"Rota: {t.start.name} -> "
            for f in t.route:
                line += f"{f.name} -> "
            line += f"{t.end.name}"
            print(line)
            print(f"Carga Total: {liter_to_bbl(truck_capacity) - t.capacity:.2f} bbl")
            print(f"Custo: R$ {t.var_cost + t.fixed_cost:.2f}")
            print()
        if unused_trucks:
            trucks_text = "Caminhões" if len(unused_trucks) != 1 else "Caminhão"
            used_text = "utilizados" if len(unused_trucks) != 1 else "utilizado"
            print(
                colored(
                    f"{trucks_text} não {used_text}: {', '.join(unused_trucks)}.",
                    color="cyan",
                )
            )
        print(
            colored(
                f"Custo Total Otimizado: {solver.optimal_solution.total_cost}", "yellow"
            )
        )
        print(colored(f"Solver Time: {timedelta(seconds=duration)}", "blue"))
