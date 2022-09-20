from fim_interpreter import Interpreter
from colorama import Fore, Style


class Debugger(Interpreter):
    def __init__(self, parser, program):
        super().__init__(parser)
        self.current_line = 0
        self.lines = program.split('\n')
        self.breakpoints = set()
        self.command = ''

    def visit(self, node):
        if self.should_stop(node.line):
            print(f'{Fore.YELLOW}Line {node.line}:{Style.RESET_ALL}'
                  f' {self.lines[node.line]}')
            self.handle_commands(node.line)
        self.current_line = node.line
        return super().visit(node)

    def should_stop(self, line):
        if line in self.breakpoints and self.current_line != line:
            return True
        if self.command == 'c':
            return False
        return line != self.current_line

    def handle_commands(self, line):
        self.command = input(f'{Fore.YELLOW}command::: {Style.RESET_ALL}')
        while self.command != 'n':
            if self.command == 'q':
                exit()
            elif self.command == 'env':
                print(self.environment.str_all())
            elif self.command == 'help':
                self.print_help()
            elif self.command == 'sb':
                self.set_breakpoint()
            elif self.command == 'rb':
                self.remove_breakpoint()
            elif self.command == 'b':
                print(f'{Fore.YELLOW}Breakpoints: {Style.RESET_ALL}'
                      f'{self.breakpoints}')
            elif self.command == 'c':
                return
            elif self.command == 'p':
                self.print_program(line)
            else:
                print(f'{Fore.RED}Invalid command{Style.RESET_ALL}')
                self.print_help()
            self.command = input(f'{Fore.YELLOW}command::: {Style.RESET_ALL}')

    @staticmethod
    def print_help():
        print(f'{Fore.GREEN}Valid commands:')
        print('n - next line')
        print('c - continue')
        print('sb - set breakpoint')
        print('rb - remove breakpoint')
        print('b - show breakpoints')
        print('q - quit')
        print('env - print environment')
        print(f'help - print help{Style.RESET_ALL}')

    def set_breakpoint(self):
        breakpoint = input(f'{Fore.YELLOW}set breakpoint::: {Style.RESET_ALL}')
        if breakpoint.isdigit():
            self.breakpoints.add(int(breakpoint))
            print(f'{Fore.YELLOW}Breakpoints: {Style.RESET_ALL}'
                  f'{self.breakpoints}')
        else:
            print(f'{Fore.RED}Invalid breakpoint:'
                  f' should be int {Style.RESET_ALL}')

    def remove_breakpoint(self):
        breakpoint = input(f'{Fore.YELLOW}remove breakpoint::: '
                           f'{Style.RESET_ALL}')
        if breakpoint.isdigit():
            self.breakpoints.remove(int(breakpoint))
            print(f'{Fore.YELLOW}Breakpoints: {Style.RESET_ALL}'
                  f'{self.breakpoints}')
        else:
            print(f'{Fore.RED}Invalid breakpoint:'
                  f' should be int {Style.RESET_ALL}')

    def print_program(self, cur_line):
        print(f'{Fore.YELLOW}Program: {Style.RESET_ALL}')
        for i, line in enumerate(self.lines):
            line_color = Fore.GREEN if i == cur_line else Fore.WHITE
            number_color = Fore.RED if i in self.breakpoints else Fore.YELLOW
            print(f'{number_color}{i}{Style.RESET_ALL} '
                  f'{line_color}{line}{Style.RESET_ALL}')
