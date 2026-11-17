"""Algoritmos que debe completar o alumnado. Non modificar as sinaturas."""
from __future__ import annotations
from itertools import permutations
from .Problem import Problem

Result = tuple[int, tuple[str, ...]]


class Solver:
    def __init__(self, problem: Problem):
        self.problem = problem

    def brute_force(self, origin: str) -> Result:
        """Devolve (custo, ruta pechada) explorando todas as permutacións.

        A orixe xa foi validada polo comando TSP. Visitar todos os outros
        nodos unha vez e incluír o regreso. En empate, escoller a tupla de
        nomes lexicograficamente menor. Un único nodo: (0, (origin, origin)).
        """
        # TODO: [Práctica Alumno] Enumerar e avaliar os ciclos posibles.
        names = self.problem.names
        costs = self.problem.costs
        start = self.problem.index(origin)
        if len(names) == 1:
            return 0, (origin, origin)

        # Os nomes están ordenados, polo que comparar índices equivale a
        # comparar nomes. permutations xera as rutas en orde lexicográfica:
        # quedarse só cun custo estritamente menor garante o desempate.
        others = [i for i in range(len(names)) if i != start]
        best_cost = None
        best_route: tuple[int, ...] = ()
        for perm in permutations(others):
            cost = costs[start][perm[0]]
            for a, b in zip(perm, perm[1:]):
                cost += costs[a][b]
            cost += costs[perm[-1]][start]
            if best_cost is None or cost < best_cost:
                best_cost, best_route = cost, perm

        route = (origin, *(names[i] for i in best_route), origin)
        return best_cost, route

    def dynamic(self, origin: str) -> Result:
        """Mesmo contrato que brute_force, mediante programación dinámica.

        Resolver o problema mediante programación dinámica e devolver a ruta
        óptima co desempate especificado. Non se esixe un algoritmo concreto.
        """
        # TODO: [Práctica Alumno] Implementar a solución mediante programación dinámica.
        names = self.problem.names
        costs = self.problem.costs
        n = len(names)
        start = self.problem.index(origin)
        if n == 1:
            return 0, (origin, origin)

        # C[w][i] é custo mínimo de saír de i, visitar todos os nodos do
        # conxunto w e volver á orixe. A orixe nunca forma parte de w.
        full = ((1 << n) - 1) & ~(1 << start)
        C: list[list[int | None]] = [[None] * n for _ in range(1 << n)]
        for i in range(n):
            C[0][i] = costs[i][start]  # C(i, ∅) = D(i, orixe)

        # Os subconxuntos procésanse en orde numérica crecente: w - {j} < w,
        # así que cada valor que se precisa xa está calculado.
        for w in range(1, 1 << n):
            if w & ~full:
                continue  # conxuntos que conteñen a orixe
            members = [j for j in range(n) if w >> j & 1]
            for i in range(n):
                if w >> i & 1:
                    continue  # i non pode estar entre os pendentes
                best = None
                for j in members:
                    value = costs[i][j] + C[w & ~(1 << j)][j]
                    if best is None or value < best:
                        best = value
                C[w][i] = best

        total = C[full][start]

        # Reconstrución: en cada paso escóllese o menor índice (= menor nome)
        # que mantén o óptimo, o que dá a ruta lexicograficamente menor.
        route = [start]
        current, w = start, full
        while w:
            for j in range(n):
                if w >> j & 1 and costs[current][j] + C[w & ~(1 << j)][j] == C[w][current]:
                    route.append(j)
                    current = j
                    w &= ~(1 << j)
                    break
        route.append(start)
        return total, tuple(names[i] for i in route)
