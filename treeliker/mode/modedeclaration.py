class Argument(object):
    def __repr__(self):
        return '\'%s\'' % str(self)


class InputArgument(Argument):
    def __str__(self):
        if self.number_restriction is None:
            return '+%s' % self.name
        else:
            return '+%s[%i]' % (self.name, self.number_restriction)

    def __init__(self, name, number_restriction=None):
        self.name = name
        self.number_restriction = number_restriction


class OutputArgument(Argument):
    def __str__(self):
        if self.number_restriction is None:
            return '-%s' % self.name
        else:
            return '-%s[%i]' % (self.name, self.number_restriction)

    def __init__(self, name, number_restriction=None):
        self.name = name
        self.number_restriction = number_restriction


class IgnoredArgument(Argument):
    def __str__(self):
        return '!%s' % self.name

    def __init__(self, name):
        self.name = name


class ConstantArgument(Argument):
    def __str__(self):
        return '#%s' % self.name

    def __init__(self, name):
        self.name = name


class ModeDeclraration(object):
    def __str__(self):
        return '%s(%s)' % (
            self.predicate_name, ','.join([str(a) for a in self.arguments]))

    def __repr__(self):
        return '\'%s\'' % str(self)

    def __init__(self, predicate_name, arguments):
        self.predicate_name = predicate_name
        self.arguments = arguments

    def input_arguments(self):
        return [a for a in self.arguments if isinstance(a, InputArgument)]

    def output_arguments(self):
        return [a for a in self.arguments if isinstance(a, OutputArgument)]
