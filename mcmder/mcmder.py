"""Use mcmd from python."""
import os
import io
import copy
import subprocess
import pandas

from .errors import McmderError, McmdError
from .utils import df2bytes, to_cstr


class Mcmder(object):
    """Use mcmd from python."""

    def __init__(self, input_data, _mcmd_args=None):
        """Check if input data is file path or pandas.df.

        :param str or pandas.DataFrame input_data:
        :param list _mcmd_args:
        """
        if not isinstance(input_data, pandas.DataFrame) and \
           not isinstance(input_data, str):
            raise ValueError(
                'Input data must be str(file path) or pandas.dataframe.')
        elif isinstance(input_data, str) and not os.path.exists(input_data):
            raise ValueError('Input file does not exist.')
        self.input_data = input_data
        self._mcmd_args = _mcmd_args
        self._dataframe = None

    @property
    def statement(self):
        return ' '.join(self._mcmd_args) if self._mcmd_args else None

    def save(self, output_file, create_dataframe=False):
        """Save data as a csv.

        :param str output_file: file path
        """
        if self._dataframe is not None:
            return self._dataframe.to_csv(output_file)
        elif create_dataframe:
            self._dataframe = pandas.read_csv(
                io.BytesIO(self.execute(output_file, stdout=True)))
        else:
            self.execute(output_file)

    @property
    def dataframe(self):
        if self._dataframe is None:
            self._dataframe = pandas.read_csv(
                io.BytesIO(self.execute(stdout=True)))
        return self._dataframe

    df = dataframe

    def execute(self, output_file=None, stdout=False):
        """Execute M-Command.

        if output_file is not None, just output to file.
        :rtype: bytes
        """
        if self._mcmd_args is None:
            raise McmderError("This mcmder does not have commands yet.")
        args = copy.copy(self._mcmd_args)
        if output_file is not None and stdout:
            args.append('|mtree o=' + output_file)
        elif output_file is not None and not stdout:
            args.append('o=' + output_file)
        if isinstance(self.input_data, pandas.DataFrame):
            stdin = df2bytes(self.input_data)
        else:
            stdin = None
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
        if 'params' in flags:
            completed_process = subprocess.run(
                [mcmd_name, '-params'],
                stdout=subprocess.PIPE
            )
            print(completed_process.stdout)
            return
        if self._mcmd_args is not None:
            next_args = copy.copy(self._mcmd_args)
            next_args.append('|')
            next_args.append(mcmd_name)
        elif isinstance(self.input_data, str):
            next_args = [mcmd_name, 'i='+self.input_data]
        else:
            next_args = [mcmd_name, ]
        for flag in flags:
            next_args.append('-' + flag)
        for k, v in options.items():
            next_args.append(k + '=' + v)
        return Mcmder(self.input_data, _mcmd_args=next_args)

    # Each Commands
    def msortf(self, f):
        return self.mcmd('msortf', f=to_cstr(f))

    def mcut(self, f):
        return self.mcmd('mcut', f=to_cstr(f))

    def muniq(self, k):
        return self.mcmd('muniq', k=to_cstr(k))

    def mfldname(self, f):
        return self.mcmd('mcut', f=to_cstr(f))

    def mjoin(self, m, k, f=None):
        options = {'m': m, 'k': to_cstr(k)}
        if f is not None:
            options['f'] = to_cstr(f)
        return self.mcmd('mjoin', **options)

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
