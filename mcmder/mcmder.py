"""Use M-Command from python."""
import os
import io
import copy
import subprocess
import pandas

from .errors import McmderError, McmdError
from .utils import df2bytes, to_cstr


class Mcmder(object):
    """Create/Contain M-Command and contain the result as pandas.DataFrame."""

    def __init__(self, input_data=None, _mcmd_args=None, header=True):
        """Check if input data is file path or pandas.df.

        :param str or pandas.DataFrame input_data:
        :param list _mcmd_args:
        """
        if not(input_data is None or isinstance(input_data, str) or
               isinstance(input_data, pandas.DataFrame)):
            raise ValueError(
                'Input data must be str(file path) or pandas.DataFrame.')
        elif isinstance(input_data, str) and not os.path.exists(input_data):
            raise ValueError('Input file does not exist.')
        self.input_data = input_data
        self._mcmd_args = _mcmd_args
        self.header = header
        self._dataframe = None

    @property
    def statement(self):
        return ' '.join(self._mcmd_args) if self._mcmd_args else None

    def save(self, output_file, create_dataframe=False):
        """Save data as a csv.

        :param str output_file: file path to write
        :param bool create_dataframe: save also as a dataframe
        """
        if self._dataframe is not None:
            self._dataframe.to_csv(output_file)
        elif create_dataframe:
            self._dataframe = pandas.read_csv(
                io.BytesIO(self.execute(output_file, stdout=True)))
        else:
            self.execute(output_file)
        return self

    @property
    def dataframe(self):
        if self._dataframe is None:
            self._dataframe = pandas.read_csv(
                io.BytesIO(self.execute(stdout=True)))
        return self._dataframe

    df = dataframe

    def execute(self, output_file=None, stdout=False, header=False):
        """Execute M-Command.

        if output_file is not None, just write into the file.
        :param str output_file: file path to write
        :param bool stdout: get bytes stdout
        :rtype: bytes
        """
        if self._mcmd_args is None:
            raise McmderError("This mcmder does not have commands yet.")
        args = copy.copy(self._mcmd_args)
        if output_file is not None and stdout:
            args.append('|mtree o=' + output_file)
        elif output_file is not None and not stdout:
            args.append('o=' + output_file)
        if header:
            args.append('-nfno')
        stdin = df2bytes(self.input_data) \
            if isinstance(self.input_data, pandas.DataFrame) else None
        completed_process = subprocess.run(
            ' '.join(args), input=stdin,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        if completed_process.returncode != 0:
            raise McmdError(
                completed_process.returncode, ' '.join(args),
                output=completed_process.stdout,
                stderr=completed_process.stderr
            )
        return completed_process.stdout

    def mcmd(self, mcmd_name, *flags, **options):
        """Return new Mcmder added new command.

        flags are added as '-flag', options are added as 'key=value'
        into M-Command
        :param str mcmd_name: M-Command name like 'mcut'
        :rtype: Mcmder
        """
        matched_set = set(flags) & {'params', 'help', 'helpl', 'version'}
        if matched_set != set():
            for flag in matched_set:
                completed_process = subprocess.run(
                    [mcmd_name, '-' + flag], stdout=subprocess.PIPE)
                print(completed_process.stdout)
            return self
        if self._mcmd_args is None:
            if isinstance(self.input_data, str):
                next_args = [mcmd_name, 'i=' + self.input_data]
            else:
                next_args = [mcmd_name, ]
            if not self.header:
                next_args.append('-nfn')
        else:
            next_args = copy.copy(self._mcmd_args)
            next_args.append('|')
            next_args.append(mcmd_name)
        for flag in flags:
            if flag is not None:
                next_args.append('-' + flag)
        for k, v in options.items():
            if v is not None:
                next_args.append(k + '=' + v)
        return Mcmder(self.input_data, _mcmd_args=next_args)

    # Each Commands
    def msortf(self, f, del_percent=True):
        if del_percent:
            return self.mcmd('msortf', f=to_cstr(f)).mcmd('mfldname', 'q')
        else:
            return self.mcmd('msortf', f=to_cstr(f))

    def mcut(self, f):
        return self.mcmd('mcut', f=to_cstr(f))

    def muniq(self, k):
        return self.mcmd('muniq', k=to_cstr(k))

    def mfldname(self, f):
        return self.mcmd('mcut', f=to_cstr(f))

    def mjoin(self, m, k, f=None):
        return self.mcmd('mjoin', m=m, k=to_cstr(k), f=to_cstr(f))

    def msel(self, c):
        return self.mcmd('msel', c="'{}'".format(c))

    # Aggregate
    def msum(self, k, f):
        return self.mcmd(self, k=to_cstr(k), f=to_cstr(f))

    def mavg(self, k, f):
        return self.mcmd('mavg', k=to_cstr(k), f=to_cstr(f))

    def mcount(self, a, f):
        return self.mcmd('mcount', a=to_cstr(a), f=to_cstr(f))

    def mstats(self, k, f, c):
        return self.mcmd('mstats', k=to_cstr(k),
                         f=to_cstr(f), c="'{}'".format(c))
