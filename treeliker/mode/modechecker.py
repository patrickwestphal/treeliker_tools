from functools import reduce
from networkx import find_cycle
from networkx.classes.graph import Graph
from networkx.exception import NetworkXNoCycle

from treeliker.mode.modedeclaration import OutputArgument, Argument, \
    InputArgument


class CheckFailed(Exception):
    def __init__(self, msg):
        self.msg = msg


class ModeChecker(object):
    """Checks whether certain requirements like

    - acyclicity
    - restrictions on the number of appearances of inputs and outputs

    are met.
    """

    def __init__(self, mode_declarations):
        self.mode_declarations = mode_declarations
        self.checkers = []
        self.checkers.append(self._check_cycle)
        self.checkers.append(self._check_exactly_once_as_output)
        self.checkers.append(self._check_at_least_once_as_input)
        self.checkers.append(self._check_at_most_one_input_arg)

    def check(self):
        for checker in self.checkers:
            checker(self.mode_declarations)

    @staticmethod
    def _check_cycle(mode_declarations):
        g = Graph().to_directed()

        for decl in mode_declarations:
            input_args = decl.input_arguments()
            output_args = decl.output_arguments()

            for o in output_args:
                g.add_node(o.name)

            for i in input_args:
                g.add_node(i.name)

                for o in output_args:
                    g.add_edge(i.name, o.name)

        try:
            res = find_cycle(g)
        except NetworkXNoCycle:
            return

        raise CheckFailed('Cycle found: %s' % str(res))

    @staticmethod
    def _check_exactly_once_as_output(mode_declarations):
        def count(aggregator, argument):
            if isinstance(aggregator, Argument):
                name = aggregator.name
                num_restr = aggregator.number_restriction

                if isinstance(aggregator, OutputArgument):
                    aggregator = {name: (1, num_restr == 1)}
                else:
                    aggregator = {name: (0, False)}

            if argument.name not in aggregator:
                aggregator[argument.name] = (0, False)

            if isinstance(argument, OutputArgument):
                cntr, nr_flag = aggregator[argument.name]

                if argument.number_restriction == 1:
                    if nr_flag:
                        return aggregator
                    else:
                        cntr += 1
                        aggregator[argument.name] = (cntr, True)
                else:
                    cntr += 1
                    aggregator[argument.name] = (cntr, False)

            return aggregator

        args = []
        for decl in mode_declarations:
            for o in decl.output_arguments():
                args.append(o)

            for i in decl.input_arguments():
                args.append(i)

        counts = reduce(count, args)
        filtered = [f for f in filter(lambda i: i[1][0] != 1, counts.items())]

        if len(filtered) > 0:
            raise CheckFailed('These output arguments did not occur exactly '
                              'once: %s' % str(filtered))

    @staticmethod
    def _check_at_least_once_as_input(mode_declarations):
        def count(aggregator, argument):
            if isinstance(aggregator, Argument):
                name = aggregator.name

                if isinstance(aggregator, InputArgument):
                    aggregator = {name: 1}
                else:
                    aggregator = {name: 0}

            if argument.name not in aggregator:
                aggregator[argument.name] = 0

            if isinstance(argument, InputArgument):
                cntr = aggregator[argument.name]
                cntr += 1
                aggregator[argument.name] = cntr

            return aggregator

        args = []
        for decl in mode_declarations:
            for o in decl.output_arguments():
                args.append(o)

            for i in decl.input_arguments():
                args.append(i)

        counts = reduce(count, args)
        filtered = [f for f in filter(lambda i: i[1] == 0, counts.items())]

        if len(filtered) > 0:
            raise CheckFailed('These input arguments occur not at least once: '
                              '%s' % str(filtered))

    @staticmethod
    def _check_at_most_one_input_arg(mode_declarations):
        erroneous = []
        for decl in mode_declarations:
            if len(decl.input_arguments()) > 1:
                erroneous.append(decl)

        if len(erroneous) > 0:
            raise CheckFailed(
                'These mode declarations have more than 1 input argument: %s'
                % ','.join([str(d) for d in erroneous]))
