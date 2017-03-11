from pyparsing import alphanums
from pyparsing import Literal
from pyparsing import nums
from pyparsing import OneOrMore
from pyparsing import Optional
from pyparsing import Word
from pyparsing import ZeroOrMore

from treeliker.mode.modedeclaration import OutputArgument, ModeDeclraration, \
    IgnoredArgument, InputArgument, ConstantArgument


class ModeParser(object):
    """Parses a mode file which contains one mode declaration per line,
    where a mode declaration is a predicate like e.g.

      dsstox_cid(+molecule,#integer)
    """

    _modifier = Literal('+') | Literal('-') | Literal('!') | Literal('*') | \
                Literal('@') | Literal('#')
    _arg_name = Word(alphanums + '_')
    _num_restriction = Word(nums)
    _num_restrictor = Literal('[').suppress() + _num_restriction + \
                      Literal(']').suppress()
    _argument = _modifier + _arg_name + Optional(_num_restrictor)
    _predicate_name = Word(alphanums + '_')
    _mode_line = _predicate_name + Literal('(').suppress() + _argument + \
                 ZeroOrMore(Literal(',').suppress() + _argument) + \
                 Literal(')').suppress()
    _modes_file = OneOrMore(_mode_line)

    def __init__(self):
        self._argument.addParseAction(self._create_argument)
        self._mode_line.addParseAction(self._create_mode_declaration)

    def parse(self, file_path):
        return self._modes_file.parseFile(file_path)

    @staticmethod
    def _create_argument(parse_result):
        """
        :param parse_result: e.g. (['-', 'drug', '1'], {}), or
            (['!', 'drug'], {}), or (['+', 'ring1'], {}), or ...
        """
        if parse_result[0] == '-':
            if len(parse_result) == 3:
                return OutputArgument(parse_result[1], int(parse_result[2]))
            else:
                return OutputArgument(parse_result[1])
        elif parse_result[0] == '!':
            return IgnoredArgument(parse_result[1])
        elif parse_result[0] == '+':
            if len(parse_result) == 3:
                return InputArgument(parse_result[1], int(parse_result[2]))
            else:
                return InputArgument(parse_result[1])
        elif parse_result[0] == '#':
            return ConstantArgument(parse_result[1])

        import pdb; pdb.set_trace()
        pass

    @staticmethod
    def _create_mode_declaration(parse_result):
        predicate_name = parse_result.pop(0)
        args = parse_result[:]

        return ModeDeclraration(predicate_name, args)
